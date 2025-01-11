import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (
    QApplication, QVBoxLayout, QHBoxLayout, QSlider, QWidget, QLabel, QLineEdit, QPushButton, QStackedWidget, QFileDialog, QDateEdit
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QPixmap


# Butterworth low-pass filter
def low_pass_filter(data, cutoff, fs, order=4):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    filtered_data = filtfilt(b, a, data)
    return filtered_data

# Intro Screen
class IntroScreen(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.file_path = None  # Placeholder for selected file
        self.init_ui()
        self.resize(300,400)

    def init_ui(self):
        layout = QVBoxLayout()

        # Logo
        logo = QLabel()
        pixmap = QPixmap("./NervNet.png") 
        pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio)
        logo.setPixmap(pixmap)
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo)

        # Name Input
        name_layout = QHBoxLayout()
        name_label = QLabel("Name:")
        self.name_input = QLineEdit()
        self.name_input.textChanged.connect(self.validate_inputs)
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)

        # Date Picker
        date_layout = QHBoxLayout()
        date_label = QLabel("Date:")
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)  # Enable dropdown calendar
        self.date_input.setDate(QDate.currentDate())  # Set default to today
        self.date_input.dateChanged.connect(self.validate_inputs)
        date_layout.addWidget(date_label)
        date_layout.addWidget(self.date_input)
        layout.addLayout(date_layout)

        # File Input
        file_layout = QHBoxLayout()
        file_label = QLabel("CSV File:")
        self.file_button = QPushButton("Browse")
        self.file_button.clicked.connect(self.browse_file)
        self.file_feedback = QLabel("No file selected")
        file_layout.addWidget(file_label)
        file_layout.addWidget(self.file_button)
        layout.addLayout(file_layout)
        layout.addWidget(self.file_feedback)

        # Start Button
        self.start_button = QPushButton("Start")
        self.start_button.setEnabled(False)  # Initially disabled
        self.start_button.clicked.connect(self.start_main_app)
        layout.addWidget(self.start_button)

        self.setLayout(layout)

    def browse_file(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Select CSV File", "", "CSV Files (*.csv)")
        if file_path:
            self.file_path = file_path
            self.file_feedback.setText(file_path)
            self.validate_inputs()

    def validate_inputs(self):
        name_filled = bool(self.name_input.text().strip())
        date_filled = bool(self.date_input.text().strip())
        file_selected = bool(self.file_path)
        self.start_button.setEnabled(name_filled and date_filled and file_selected)

    def start_main_app(self):
        # Pass user inputs to the next stage
        main_app = self.stacked_widget.widget(1)
        main_app.file_path = self.file_path

        # Load the data into Stage1
        eeg_data = pd.read_csv(self.file_path)
        main_app.stage1.eeg_data = eeg_data
        main_app.stage1.time = eeg_data["Time (s)"]
        main_app.stage1.fs = 256  # Assumed sampling frequency
        main_app.stage1.update_plot()
        main_app.stage1.user_name = self.name_input.text().strip()
        main_app.stage1.user_date = self.date_input.text().strip()

        # Switch to the main app
        self.stacked_widget.resize(1200, 900)
        self.stacked_widget.setCurrentIndex(1)

class Stage1(QWidget):
    def __init__(self, eeg_data, time, fs, user_name, user_date, stacked_widget):
        super().__init__()
        self.eeg_data = eeg_data
        self.time = time
        self.fs = fs
        self.cutoff = 30  # Default cutoff frequency
        self.filtered_data = None
        self.user_name = user_name
        self.user_date = user_date
        self.stacked_widget = stacked_widget

        self.init_ui()
        self.resize(1200,900)

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
        if self.eeg_data is not None :
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
        file_name = self.user_name+"_"+self.user_date+"_"+"stage-1.png"
        file_name = file_name.replace("/","_")
        self.figure.savefig(file_name)
        self.feedback_label.setText(f'Image saved to "{file_name}".')

    def goto_stage2(self):
        stage2 = self.stacked_widget.widget(1)
        stage2.load_data(self.filtered_data)
        stage2.user_name = self.user_name
        stage2.user_date = self.user_date
        self.stacked_widget.setCurrentIndex(1)


class Stage2(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.filtered_data = None
        self.stacked_widget = stacked_widget
        self.user_name = None
        self.user_date = None

        # Threshold defaults
        self.base_thresholds = {"FP1": 8500, "FP2": -8400}
        self.slider_values = {"FP1": 100, "FP2": 100}

        self.init_ui()
        self.resize(1200,900)

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
        self.feedback_label = QLabel("")
        back_button = QPushButton("Back")
        back_button.clicked.connect(self.goto_stage1)
        image_button = QPushButton("Save Image")
        image_button.clicked.connect(self.export_image)
        button_layout.addWidget(back_button)
        button_layout.addWidget(image_button)
        layout.addLayout(button_layout)

        # Feedback Label for Export
        self.feedback_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.feedback_label)

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
        file_name = self.user_name+"_"+self.user_date+"_"+"stage-2.png"
        file_name = file_name.replace("/","_")
        self.figure.savefig(file_name)
        self.feedback_label.setText(f'Image saved to "{file_name}".')

class MainApp(QStackedWidget):
    def __init__(self, eeg_data=None, time=None, fs=None, user_name=None, user_date=None):
        super().__init__()
        self.stage1 = Stage1(eeg_data, time, fs, user_name, user_date, self)
        self.stage2 = Stage2(self)
        self.addWidget(self.stage1)
        self.addWidget(self.stage2)
        self.setCurrentIndex(0)

def main():
    app = QApplication(sys.argv)

    # Create the stacked widget
    stacked_widget = QStackedWidget()

    # Add Intro Screen
    intro_screen = IntroScreen(stacked_widget)
    stacked_widget.addWidget(intro_screen)

    # Add Main Application
    main_app = MainApp()
    stacked_widget.addWidget(main_app)

    # Set window title and size
    stacked_widget.setWindowTitle("EEG Analysis Tool")
    stacked_widget.resize(300, 400)
    stacked_widget.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
