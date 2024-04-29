# CR2-Repair-Tool

![image](https://github.com/DRCRecoveryData/CR2-Repair-Tool/blob/main/Images/Screenshot%20from%202024-04-29%2016-33-33.png)

CR2-Repair-Tool is a PyQt6 application for repairing CR2 image files using a reference CR2 file. Provides a user-friendly GUI.

# Demo

![Watch the video](https://github.com/DRCRecoveryData/CR2-Repair-Tool/blob/main/Images/Screencast%20from%202024-04-29%2016-27-41.webm)

## Requirements

- Python 3.x
- PyQt6
- rawpy
- imageio

`pip install pyqt6 rawpy imageio`

## Usage

1. Clone the repository or download the `cr2repair-gui.py` file.
2. Install PyQt6 if you haven't already:
```pip install PyQt6```

4. Run the `cr2repair-gui.py` file:
```python cr2repair-gui.py```
5. The GUI window will appear. Use the "Browse" buttons to select the reference CR2 file and the encrypted folder.
6. Click the "Repair" button to start the repair process.
7. Progress will be displayed in the progress bar and log box. Once the repair is complete, a success message will appear.

## How it Works

- The tool reads the reference CR2 file and locates the offset header.
- It then scans the encrypted folder for CR2 files to be repaired.
- For each file found, it copies the data after the offset header from the reference file and writes it to a new file in the "Repaired" folder.
- The process is tracked in the log box, and progress is shown in the progress bar.

## Styling

- The GUI features modern blue buttons styled with CSS to enhance the user experience.

## Limitations

- This tool is specifically designed for repairing CR2 files and may not work with other file formats.
- It assumes that the reference CR2 file and the encrypted files have a specific structure, so results may vary with different files.

## Disclaimer

- Use this tool at your own risk. Always make backups of your files before attempting any modifications.


