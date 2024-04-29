import sys
import os
import glob
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QFileDialog, QProgressBar, QTextEdit, QMessageBox, QCheckBox
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import rawpy
import imageio

class CR2RepairWorker(QThread):
    progress_updated = pyqtSignal(int)
    log_updated = pyqtSignal(str)
    repair_finished = pyqtSignal(str)

    def __init__(self, reference_file_path, encrypted_folder_path, convert_to_tiff, convert_folder):
        super().__init__()
        self.reference_file_path = reference_file_path
        self.encrypted_folder_path = encrypted_folder_path
        self.convert_to_tiff = convert_to_tiff
        self.convert_folder = convert_folder

    def run(self):
        # Create the "Repaired" folder if it doesn't exist
        repaired_folder_path = os.path.join(self.encrypted_folder_path, "Repaired")
        os.makedirs(repaired_folder_path, exist_ok=True)

        # Create the "Converted" folder if converting to TIFF
        if self.convert_to_tiff:
            converted_folder_path = os.path.join(self.encrypted_folder_path, "Converted")
            os.makedirs(converted_folder_path, exist_ok=True)

        # Load reference header from the reference file
        with open(self.reference_file_path, 'rb') as f:
            buf = bytearray(f.read())
            pos = buf.rfind(b'\xFF\xD8\xFF\xC4')
            reference_header = buf[:pos]
            reference_header[0x62:0x65] = b'\0\0\0'

        # Get a list of all CR2 files in the encrypted folder
        encrypted_files = glob.glob(os.path.join(self.encrypted_folder_path, '*.CR2.*'))

        total_files = len(encrypted_files)

        # Process each encrypted file
        for i, encrypted_file in enumerate(encrypted_files):
            # Get the file name without the extension
            file_name, _ = os.path.splitext(os.path.basename(encrypted_file))

            # Update progress
            progress_value = (i + 1) * 100 // total_files
            self.progress_updated.emit(progress_value)

            # Update log
            self.log_updated.emit(f"Processing {file_name}...")

            # Get data from the encrypted file
            with open(encrypted_file, 'rb') as f:
                buf = bytearray(f.read())
                pos = buf.rfind(b'\xFF\xD8\xFF\xC4')
                actual_body = buf[pos:]

            # Write the fixed file to the Repaired folder without any additional extension
            repaired_file_path = os.path.join(repaired_folder_path, file_name)
            with open(repaired_file_path, 'wb') as f:
                f.write(reference_header)
                f.write(actual_body)

            # Update log
            self.log_updated.emit(f"{file_name} repaired.")

            # Optionally convert to TIFF
            if self.convert_to_tiff:
                with rawpy.imread(repaired_file_path) as raw:
                    rgb = raw.postprocess()
                # Get the base filename without extension
                base_filename = os.path.splitext(file_name)[0]
                # Construct the TIFF file path with the base filename and .tiff extension only
                tiff_file = os.path.join(converted_folder_path, base_filename + ".tiff")
                imageio.imsave(tiff_file, rgb)
                self.log_updated.emit(f"{base_filename} converted to TIFF.")

        if self.convert_to_tiff:
            self.repair_finished.emit(f"Repaired files saved to the 'Repaired' folder.\nTIFF files converted and saved to the 'Converted' folder.")
        else:
            self.repair_finished.emit("Repaired files saved to the 'Repaired' folder.")

class CR2RepairApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("CR2 Repair Tool")
        self.setGeometry(100, 100, 400, 400)

        layout = QVBoxLayout()

        self.reference_label = QLabel("Reference File:")
        self.reference_path_edit = QLineEdit()
        self.reference_browse_button = QPushButton("Browse", self)
        self.reference_browse_button.setObjectName("browseButton")
        self.reference_browse_button.clicked.connect(self.browse_reference_file)

        self.encrypted_label = QLabel("Encrypted Folder:")
        self.encrypted_path_edit = QLineEdit()
        self.encrypted_browse_button = QPushButton("Browse", self)
        self.encrypted_browse_button.setObjectName("browseButton")
        self.encrypted_browse_button.clicked.connect(self.browse_encrypted_folder)

        self.convert_checkbox = QCheckBox("Convert CR2 to TIFF")
        self.convert_checkbox.stateChanged.connect(self.toggle_convert_checkbox)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)

        self.repair_button = QPushButton("Repair", self)
        self.repair_button.setObjectName("blueButton")
        self.repair_button.clicked.connect(self.repair_cr2_files)

        layout.addWidget(self.reference_label)
        layout.addWidget(self.reference_path_edit)
        layout.addWidget(self.reference_browse_button)
        layout.addWidget(self.encrypted_label)
        layout.addWidget(self.encrypted_path_edit)
        layout.addWidget(self.encrypted_browse_button)
        layout.addWidget(self.convert_checkbox)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.log_box)
        layout.addWidget(self.repair_button)

        self.setLayout(layout)

        self.setStyleSheet("""
        #browseButton, #blueButton {
            background-color: #3498db;
            border: none;
            color: white;
            padding: 10px 20px;
            font-size: 16px;
            border-radius: 4px;
        }
        #browseButton:hover, #blueButton:hover {
            background-color: #2980b9;
        }
        """)

        # Initialize convert_folder attribute
        self.convert_folder = ""

    def browse_reference_file(self):
        reference_file, _ = QFileDialog.getOpenFileName(self, "Select Reference CR2 File", "", "CR2 Files (*.CR2)")
        if reference_file:
            self.reference_path_edit.setText(reference_file)

    def browse_encrypted_folder(self):
        encrypted_folder = QFileDialog.getExistingDirectory(self, "Select Encrypted Folder")
        if encrypted_folder:
            self.encrypted_path_edit.setText(encrypted_folder)

    def toggle_convert_checkbox(self, state):
        if state == Qt.CheckState.Checked:
            self.convert_folder = QFileDialog.getExistingDirectory(self, "Select Converted Folder")
            if not self.convert_folder:
                self.convert_checkbox.setChecked(False)

    def repair_cr2_files(self):
        reference_file_path = self.reference_path_edit.text()
        encrypted_folder_path = self.encrypted_path_edit.text()
        convert_to_tiff = self.convert_checkbox.isChecked()

        if not os.path.exists(reference_file_path):
            self.show_message("Error", "Reference CR2 file does not exist.")
            return
        if not os.path.exists(encrypted_folder_path):
            self.show_message("Error", "Encrypted folder does not exist.")
            return

        self.worker = CR2RepairWorker(reference_file_path, encrypted_folder_path, convert_to_tiff, self.convert_folder)
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.log_updated.connect(self.update_log)
        self.worker.repair_finished.connect(self.repair_finished)
        self.worker.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def update_log(self, message):
        self.log_box.append(message)

    def repair_finished(self, message):
        self.show_message("Success", message)

    def show_message(self, title, message):
        QMessageBox.information(self, title, message)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CR2RepairApp()
    window.show()
    sys.exit(app.exec())
