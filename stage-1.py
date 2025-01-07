import sys
import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QSlider, QWidget, QLabel, QPushButton
from PyQt5.QtCore import Qt


# Butterworth low-pass filter
def low_pass_filter(data, cutoff, fs, order=4):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    filtered_data = filtfilt(b, a, data)
    return filtered_data


class EEGDenoisingApp(QWidget):
    def __init__(self, eeg_data, time, fs, optimal_cutoff=30):
        super().__init__()
        self.eeg_data = eeg_data
        self.time = time
        self.fs = fs
        self.cutoff = 30  # Default cutoff frequency
        self.optimal_cutoff = optimal_cutoff

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("EEG Denoising - Low-Pass Filter")
        self.setGeometry(100, 100, 1200, 800)

        # Main layout
        main_layout = QVBoxLayout()

        # Add current cutoff frequency label
        self.label = QLabel(f"Current Cutoff Frequency: {self.cutoff} Hz")
        self.label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.label)

        # Add a Matplotlib figure
        self.figure, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(8, 6))
        self.figure.tight_layout(pad=3)
        self.canvas = FigureCanvas(self.figure)
        main_layout.addWidget(self.canvas)

        # Add slider layout
        slider_layout = QVBoxLayout()

        # Slider label
        slider_label = QLabel("Adjust Cutoff Frequency (Hz):")
        slider_label.setAlignment(Qt.AlignCenter)
        slider_layout.addWidget(slider_label)

        # Slider ticks label
        slider_ticks_layout = QHBoxLayout()
        slider_ticks_layout.addWidget(QLabel("1 Hz"))  # Start tick
        slider_ticks_layout.addStretch()
        slider_ticks_layout.addWidget(QLabel("50 Hz"))  # Middle tick
        slider_ticks_layout.addStretch()
        slider_ticks_layout.addWidget(QLabel("100 Hz"))  # End tick
        slider_layout.addLayout(slider_ticks_layout)

        # Slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(1)
        self.slider.setMaximum(100)
        self.slider.setValue(self.cutoff)
        self.slider.setSingleStep(1)  # Increment by 1
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(5)
        self.slider.valueChanged.connect(self.update_plot)
        slider_layout.addWidget(self.slider)

        main_layout.addLayout(slider_layout)

        # Add optimal cutoff frequency layout
        optimal_layout = QHBoxLayout()

        # Optimal cutoff label
        self.optimal_label = QLabel(f"Optimal Cutoff Frequency: {self.optimal_cutoff} Hz")
        self.optimal_label.setAlignment(Qt.AlignLeft)
        optimal_layout.addWidget(self.optimal_label)

        # Button to set optimal cutoff
        self.optimal_button = QPushButton("Set Optimal Cutoff")
        self.optimal_button.clicked.connect(self.set_optimal_cutoff)
        optimal_layout.addWidget(self.optimal_button)

        main_layout.addLayout(optimal_layout)

        self.setLayout(main_layout)
        self.update_plot()

    def update_plot(self):
        self.cutoff = self.slider.value()
        self.label.setText(f"Current Cutoff Frequency: {self.cutoff} Hz")

        # Apply low-pass filter
        filtered_fp1 = low_pass_filter(self.eeg_data['FP1'], self.cutoff, self.fs)
        filtered_fp2 = low_pass_filter(self.eeg_data['FP2'], self.cutoff, self.fs)

        # Clear the plots and redraw
        self.ax1.clear()
        self.ax2.clear()

        # Plot for Channel FP1
        self.ax1.plot(self.time, self.eeg_data['FP1'], label="Raw FP1", alpha=0.5)
        self.ax1.plot(self.time, filtered_fp1, label="Filtered FP1", alpha=0.8)
        self.ax1.set_title("Channel FP1")
        self.ax1.set_xlabel("Time (s)")
        self.ax1.set_ylabel("Amplitude (μV)")
        self.ax1.legend()
        self.ax1.grid(True)

        # Plot for Channel FP2
        self.ax2.plot(self.time, self.eeg_data['FP2'], label="Raw FP2", alpha=0.5)
        self.ax2.plot(self.time, filtered_fp2, label="Filtered FP2", alpha=0.8)
        self.ax2.set_title("Channel FP2")
        self.ax2.set_xlabel("Time (s)")
        self.ax2.set_ylabel("Amplitude (μV)")
        self.ax2.legend()
        self.ax2.grid(True)

        # Update the canvas
        self.canvas.draw()

    def set_optimal_cutoff(self):
        self.slider.setValue(self.optimal_cutoff)


def main():
    # Load EEG data
    file_path = "eeg-data/Ecog_waveform.csv"  # Update with your file path
    eeg_data = pd.read_csv(file_path)
    time = eeg_data['Time (s)']
    fs = 256  # Sampling frequency (assumed)
    optimal_cutoff = 15  # Example optimal cutoff frequency (replace as needed)

    app = QApplication(sys.argv)
    ex = EEGDenoisingApp(eeg_data, time, fs, optimal_cutoff)
    ex.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
