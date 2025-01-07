import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (
    QApplication, QVBoxLayout, QHBoxLayout, QSlider, QWidget, QLabel, QLineEdit
)
from PyQt5.QtCore import Qt


class BlinkDetectionApp(QWidget):
    def __init__(self, eeg_data, time, fs):
        super().__init__()
        self.eeg_data = eeg_data
        self.time = time
        self.fs = fs

        # Default base thresholds for each channel
        self.base_thresholds = {
            "FP1": 8000,
            "FP2": -8000,
        }

        self.slider_values = {
            "FP1": 100,
            "FP2": 100,
        }

        self.slider_min = 100
        self.slider_max = 2000

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("EEG Blink Detection - Dual Channel")
        self.setGeometry(100, 100, 1200, 900)

        # Main layout
        main_layout = QVBoxLayout()

        # Add Matplotlib figure
        self.figure, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(8, 10))
        self.figure.tight_layout(pad=3)
        self.canvas = FigureCanvas(self.figure)
        main_layout.addWidget(self.canvas)

        # Channel 1 controls
        self.add_channel_controls(main_layout, "FP1")

        # Channel 2 controls
        self.add_channel_controls(main_layout, "FP2")

        self.setLayout(main_layout)
        self.update_plot()

    def add_channel_controls(self, layout, channel):
        # Create a layout for the controls
        controls_layout = QVBoxLayout()

        # Base threshold input
        threshold_layout = QHBoxLayout()
        threshold_label = QLabel(f"Base Threshold for {channel}:")
        base_input = QLineEdit(str(self.base_thresholds[channel]))
        base_input.setFixedWidth(100)
        base_input.editingFinished.connect(
            lambda ch=channel, inp=base_input: self.update_base_threshold(ch, inp)
        )
        threshold_layout.addWidget(threshold_label)
        threshold_layout.addWidget(base_input)
        controls_layout.addLayout(threshold_layout)

        # Slider
        slider_label = QLabel(f"Adjust Threshold Range for {channel} (± μV):")
        slider_label.setAlignment(Qt.AlignCenter)
        controls_layout.addWidget(slider_label)

        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(self.slider_min)
        slider.setMaximum(self.slider_max)
        slider.setValue(self.slider_values[channel])
        slider.setSingleStep(50)
        slider.setTickPosition(QSlider.TicksBelow)
        slider.setTickInterval(200)
        slider.valueChanged.connect(lambda value, ch=channel: self.update_slider(ch, value))
        controls_layout.addWidget(slider)

        layout.addLayout(controls_layout)

    def update_base_threshold(self, channel, input_widget):
        try:
            value = int(input_widget.text())
            self.base_thresholds[channel] = value
            self.update_plot()
        except ValueError:
            input_widget.setText(str(self.base_thresholds[channel]))

    def update_slider(self, channel, value):
        self.slider_values[channel] = value
        self.update_plot()

    def get_threshold_range(self, channel):
        base = self.base_thresholds[channel]
        range_offset = self.slider_values[channel]
        return base - range_offset, base + range_offset

    def update_plot(self):
        # Clear subplots
        self.ax1.clear()
        self.ax2.clear()

        # Update Channel 1 (FP1)
        self.update_channel_plot(
            self.ax1,
            "FP1",
            self.get_threshold_range("FP1"),
            "Detected Blinks - Channel FP1",
        )

        # Update Channel 2 (FP2)
        self.update_channel_plot(
            self.ax2,
            "FP2",
            self.get_threshold_range("FP2"),
            "Detected Blinks - Channel FP2",
        )

        # Update the canvas
        self.canvas.draw()

    def update_channel_plot(self, ax, channel, threshold_range, title):
        data = self.eeg_data[channel]

        # Identify blinks
        blink_mask = (data > threshold_range[1]) | (data < threshold_range[0])

        # Plot raw data and detected blinks
        ax.plot(self.time, data, label=f"Raw {channel}", alpha=0.8)
        ax.scatter(
            self.time[blink_mask],
            data[blink_mask],
            color="red",
            label="Detected Blinks",
            zorder=5,
        )
        ax.axhline(
            threshold_range[1],
            color="green",
            linestyle="--",
            label=f"Upper Threshold ({threshold_range[1]} μV)",
        )
        ax.axhline(
            threshold_range[0],
            color="green",
            linestyle="--",
            label=f"Lower Threshold ({threshold_range[0]} μV)",
        )
        ax.set_title(title)
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Amplitude (μV)")
        ax.legend()
        ax.grid(True)


def main():
    # Load EEG data
    file_path = "eeg-data/Ecog_waveform.csv"  # Update with your file path
    eeg_data = pd.read_csv(file_path)
    time = eeg_data["Time (s)"]
    fs = 256  # Sampling frequency (assumed)

    app = QApplication(sys.argv)
    ex = BlinkDetectionApp(eeg_data, time, fs)
    ex.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
