# Smite Divine Arsenal

A tool for capturing and analyzing item data from the Smite game.

## Requirements

- Python 3.10 or higher
- Tesseract OCR installed (default path: `C:\Program Files\Tesseract-OCR\tesseract.exe`)
- PyQt6, OpenCV, NumPy, and other dependencies listed in requirements.txt

## Installation

1. Clone the repository
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
3. Ensure Tesseract OCR is installed on your system
4. Install keyboard library for global hotkeys (if not already installed):
   ```
   pip install keyboard
   ```

## Usage

Run the application with the following command:

```
python main.py
```

### Command-line Options

- `--debug`: Enable debug mode for more detailed logging
- `--ocr-debug`: Enable OCR debugging to save processed images and OCR results
- `--tesseract-path PATH`: Specify the path to Tesseract OCR executable
- `--output-dir DIR`: Specify the output directory for captured data

Example:
```
python main.py --debug --ocr-debug
```

### Hotkeys

The application supports the following hotkeys:

- **F5**: Capture the current screen (works even when the application is not in focus)

The F5 key is registered as a global hotkey, allowing you to press it while playing Smite without needing to switch back to the capture tool first. This makes data collection much more seamless.

## Important Notes on Window Focus

**The application can only capture screenshots when the Smite game window is in focus (foreground).**

This is a limitation of Windows security: applications cannot capture screenshots of other applications that aren't in focus. However, you can now press F5 while playing Smite, and the application will automatically attempt to capture the current screen.

### How to Use Effectively:

1. Start the Smite Divine Arsenal tool
2. Launch Smite and navigate to the item shop or god selection screen
3. Press F5 to capture data without switching back to the tool
4. You can verify captures by checking the tool window later

### Alternative Capture Methods:

- Use the "Capture Now" button when you have the tool window open
- Enable automatic capture mode to periodically check for new data

## Debug Tools

The repository includes several debugging scripts:

- `debug_capture.py`: Visualize the capture process and test image processing
- `debug_ocr.py`: Test OCR with various configurations
- `debug_validation.py`: Test item validation rules
- `debug_screenshot.py`: Test screenshot capturing when Smite is in different window states

To run the screenshot detection test:

```
python debug_screenshot.py --count 10 --interval 2
```

This will take 10 screenshots at 2-second intervals, helping you diagnose any issues with window detection.

## Troubleshooting

If the application is not detecting items or gods correctly:

1. Enable debug mode with `--debug` to see more detailed logs
2. Try OCR debugging with `--ocr-debug` to inspect the image processing steps
3. Verify that Tesseract OCR is installed correctly and the path is set properly
4. Ensure the Smite window is in focus when capturing
5. Check that your screen resolution matches the expected 1920x1080 (other resolutions may work but are not fully tested)

### Global Hotkey Issues

If the F5 global hotkey isn't working:

1. Make sure you have the keyboard library installed (`pip install keyboard`)
2. Run the application as administrator (global hotkeys may require elevated privileges)
3. Check if F5 is already assigned to another global hotkey in your system
4. You can manually use the "Capture Now" button in the tool as a fallback

## License

MIT License - See LICENSE file for details 