import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (
    QApplication, QVBoxLayout, QHBoxLayout, QSlider, QWidget, QLabel, QLineEdit, QPushButton, QStackedWidget, QGridLayout
)
from PyQt5.QtCore import Qt


# Butterworth low-pass filter
def low_pass_filter(data, cutoff, fs, order=4):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    filtered_data = filtfilt(b, a, data)
    return filtered_data


class Stage1(QWidget):
    def __init__(self, eeg_data, time, fs, stacked_widget):
        super().__init__()
        self.eeg_data = eeg_data
        self.time = time
        self.fs = fs
        self.cutoff = 30  # Default cutoff frequency
        self.filtered_data = None
        self.stacked_widget = stacked_widget

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Cutoff Frequency Label
        self.label = QLabel(f"Current Cutoff Frequency: {self.cutoff} Hz")
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        # Matplotlib Figure
        self.figure, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(8, 8))
        self.figure.tight_layout(pad=3)
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # Slider
        slider_label = QLabel("Adjust Cutoff Frequency (Hz):")
        slider_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(slider_label)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(1)
        self.slider.setMaximum(100)
        self.slider.setValue(self.cutoff)
        self.slider.setSingleStep(1)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(1)
        self.slider.valueChanged.connect(self.update_plot)
        layout.addWidget(self.slider)

        slider_label_layout = QHBoxLayout()
        slider_label_layout.addWidget(QLabel("1Hz"))  # Start label
        slider_label_layout.addStretch()
        slider_label_layout.addWidget(QLabel("50Hz"))  # End label
        layout.addLayout(slider_label_layout)

        # Buttons
        button_layout = QHBoxLayout()
        self.feedback_label = QLabel("")
        export_button = QPushButton("Export Filtered Data")
        export_button.clicked.connect(self.export_data)
        next_button = QPushButton("Next")
        next_button.clicked.connect(self.goto_stage2)
        image_button = QPushButton("Save Image")
        image_button.clicked.connect(self.export_image)
        button_layout.addWidget(export_button)
        button_layout.addWidget(image_button)
        button_layout.addWidget(next_button)
        layout.addLayout(button_layout)

        # Feedback Label for Export
        self.feedback_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.feedback_label)

        self.setLayout(layout)
        self.update_plot()

    def update_plot(self):
        self.cutoff = self.slider.value()
        self.label.setText(f"Current Cutoff Frequency: {self.cutoff} Hz")

        # Apply low-pass filter
        filtered_fp1 = low_pass_filter(self.eeg_data['FP1'], self.cutoff, self.fs)
        filtered_fp2 = low_pass_filter(self.eeg_data['FP2'], self.cutoff, self.fs)

        # Save filtered data for export
        self.filtered_data = pd.DataFrame({
            'Time (s)': self.time,
            'FP1_Filtered': filtered_fp1,
            'FP2_Filtered': filtered_fp2
        })

        # Clear and redraw plots
        self.ax1.clear()
        self.ax2.clear()

        self.ax1.plot(self.time, self.eeg_data['FP1'], label="Raw FP1", alpha=0.5)
        self.ax1.plot(self.time, filtered_fp1, label="Filtered FP1", alpha=0.8)
        self.ax1.set_title("Channel FP1")
        self.ax1.set_ylabel("Amplitude (μV)")
        self.ax1.legend()
        self.ax1.grid(True)

        self.ax2.plot(self.time, self.eeg_data['FP2'], label="Raw FP2", alpha=0.5)
        self.ax2.plot(self.time, filtered_fp2, label="Filtered FP2", alpha=0.8)
        self.ax2.set_title("Channel FP2")
        self.ax2.set_xlabel("Time (s)")
        self.ax2.set_ylabel("Amplitude (μV)")
        self.ax2.legend()
        self.ax2.grid(True)

        self.canvas.draw()

    def export_data(self):
        if self.filtered_data is not None:
            self.filtered_data.to_csv("filtered_data.csv", index=False)
            self.feedback_label.setText("Filtered data saved to 'filtered_data.csv'.")

    def export_image(self):
        self.figure.savefig("stage-1.png")
        self.feedback_label.setText("Image saved to 'stage-1.png'.")

    def goto_stage2(self):
        stage2 = self.stacked_widget.widget(1)
        stage2.load_data(self.filtered_data)
        self.stacked_widget.setCurrentIndex(1)


class Stage2(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.filtered_data = None
        self.stacked_widget = stacked_widget

        # Threshold defaults
        self.base_thresholds = {"FP1": 8500, "FP2": -8400}
        self.slider_values = {"FP1": 100, "FP2": 100}

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Matplotlib Figure
        self.figure, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(8, 8))
        self.figure.tight_layout(pad=3)
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # Sliders and Threshold Controls
        slider_layout = QVBoxLayout()
        self.add_channel_controls(slider_layout, "FP1")
        self.add_channel_controls(slider_layout, "FP2")
        layout.addLayout(slider_layout)

        # Buttons
        button_layout = QHBoxLayout()
        back_button = QPushButton("Back")
        back_button.clicked.connect(self.goto_stage1)
        image_button = QPushButton("Save Image")
        image_button.clicked.connect(self.export_image)
        button_layout.addWidget(back_button)
        button_layout.addWidget(image_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def add_channel_controls(self, layout, channel):
        # Threshold Input and Slider
        controls_layout = QHBoxLayout()

        # Base Threshold Input
        threshold_label = QLabel(f"Base Threshold for {channel}:")
        base_input = QLineEdit(str(self.base_thresholds[channel]))
        base_input.setFixedWidth(100)
        base_input.editingFinished.connect(
            lambda ch=channel, inp=base_input: self.update_base_threshold(ch, inp)
        )
        controls_layout.addWidget(threshold_label)
        controls_layout.addWidget(base_input)

        # Slider
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(50)
        slider.setMaximum(500)
        slider.setValue(self.slider_values[channel])
        slider.setSingleStep(10)
        slider.setTickPosition(QSlider.TicksBelow)
        slider.setTickInterval(50)
        slider.valueChanged.connect(lambda value, ch=channel: self.update_slider(ch, value))
        controls_layout.addWidget(slider)

        layout.addLayout(controls_layout)

    def load_data(self, filtered_data):
        self.filtered_data = filtered_data
        self.update_plot()

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

    def update_plot(self):
        if self.filtered_data is None:
            return

        self.ax1.clear()
        self.ax2.clear()

        # Process FP1
        self.plot_channel(self.ax1, "FP1_Filtered", "FP1")

        # Process FP2
        self.plot_channel(self.ax2, "FP2_Filtered", "FP2")

        self.canvas.draw()

    def plot_channel(self, ax, column, channel):
        base = self.base_thresholds[channel]
        range_offset = self.slider_values[channel]
        upper, lower = base + range_offset, base - range_offset
        data = self.filtered_data[column]
        time = self.filtered_data["Time (s)"]

        # Blink Detection
        blink_mask = (data > upper) | (data < lower)

        # Plot Data
        ax.plot(time, data, label=f"{channel} Filtered", alpha=0.8)
        ax.scatter(time[blink_mask], data[blink_mask], color="red", label="Detected Blinks", zorder=5)
        ax.axhline(upper, color="green", linestyle="--", label=f"Upper Threshold ({upper} μV)")
        ax.axhline(lower, color="green", linestyle="--", label=f"Lower Threshold ({lower} μV)")
        ax.set_title(f"Channel {channel}")
        ax.legend()
        ax.grid(True)

    def goto_stage1(self):
        self.stacked_widget.setCurrentIndex(0)

    def export_image(self):
        self.figure.savefig("stage-2.png")
        self.feedback_label.setText("Image saved to 'stage-2.png'.")

class MainApp(QStackedWidget):
    def __init__(self, eeg_data, time, fs):
        super().__init__()
        self.stage1 = Stage1(eeg_data, time, fs, self)
        self.stage2 = Stage2(self)
        self.addWidget(self.stage1)
        self.addWidget(self.stage2)
        self.setCurrentIndex(0)

def main():
    # Load EEG data
    file_path = "eeg-data/Ecog_waveform_2.csv"  # Update with your file path
    eeg_data = pd.read_csv(file_path)
    time = eeg_data["Time (s)"]
    fs = 256  # Sampling frequency (assumed)

    app = QApplication(sys.argv)
    main_app = MainApp(eeg_data, time, fs)
    
    # Set window title and size
    main_app.setWindowTitle("EEG Analysis Tool")
    main_app.resize(1200, 900)  # Width: 1200px, Height: 900px
    
    main_app.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
