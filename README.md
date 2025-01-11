# EEG Eye Blink Analysis Tool

## Overview
This tool is designed to analyze EEG data and identify eye blinks recorded from EEG signals. The application provides an intuitive GUI for:
1. Determining the optimal low-pass filter cutoff frequency to remove noise.
2. Setting thresholds to identify eye blink events in the filtered EEG signal.

The tool uses data from two EEG channels (`FP1` and `FP2`) to analyze eye blinks, and outputs the detected events with visualization and export options.

---

## Features
- **Intro Screen**:
  - Input the user's name and analysis date.
  - Upload the EEG data file (CSV format).

- **Stage 1**:
  - Visualize raw and filtered EEG signals.
  - Adjust the low-pass filter cutoff frequency using a slider.
  - Export filtered data to a CSV file.
  - Save visualizations as images.

- **Stage 2**:
  - Adjust thresholds for eye blink detection on each channel using sliders.
  - Detect and highlight eye blink events in red on the EEG plots.
  - Export visualizations for documentation.

---

## Prerequisites
Make sure the following dependencies are installed:
- Python >= 3.8
- PyQt5
- numpy
- pandas
- matplotlib
- scipy

---

## Installation
1. Clone or download this repository.
2. Install the required dependencies:
    
    ```
    pip install -r requirements.txt
## Usage
1. Run the application:
    ```
    python eeg_blink.py
2. Intro Screen:
- Enter your name and the current date.
- Upload a valid CSV file with EEG data.
- Click "Start" once all fields are filled.
3. Stage 1:
- Adjust the cutoff frequency using the slider to filter out noise.
- Export the filtered EEG data or save a visualization image.
4. Stage 2:
- Set thresholds for both EEG channels using sliders and input fields.
- Visualize and identify eye blink events.
- Save the visualization of detected eye blinks as an image.

## CSV File Format
The input CSV file should have the following structure:
    
    Time (s),FP1,FP2
    0.00,8123,8200
    0.01,8135,8221

    Time (s): Time in seconds.
    FP1 and FP2: EEG signals from two channels. 

## Author
This tool was developed to simplify EEG signal analysis and enhance understanding of eye blink detection in EEG data.