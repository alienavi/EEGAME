import tkinter as tk
from tkinter import messagebox
import pandas as pd
import numpy as np
from scipy.signal import butter, filtfilt

# Load EEG data
eeg_data = pd.read_csv('Ecog_waveform_2.csv')
time = eeg_data['Time (s)']
channel1 = eeg_data['FP1']
channel2 = eeg_data['FP2']

# Sampling frequency (estimated from time difference)
fs = 250

# High-pass filter for DC removal
def highpass_filter(data, cutoff, fs, order=5):
    nyquist = 0.5 * fs  # Nyquist frequency
    normal_cutoff = cutoff / nyquist  # Normalized cutoff frequency
    b, a = butter(order, normal_cutoff, btype='high', analog=False)  # Butterworth filter coefficients
    return filtfilt(b, a, data)

# Low-pass Butterworth filter for denoising
def butter_lowpass_filter(data, cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return filtfilt(b, a, data)

# DC removal for both channels
channel_1_dcr = highpass_filter(channel1, 0.1, fs)
channel_2_dcr = highpass_filter(channel2, 0.1, fs)


class NeuroGameApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Neuroscience Gamified Learning")
        self.current_stage = 1
        
        # Main Frame
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(pady=20, padx=20)
        
        # Title Label
        self.title_label = tk.Label(self.main_frame, text="Welcome to Neuroscience Game", font=("Arial", 16, "bold"))
        self.title_label.pack(pady=10)
        
        # Instruction Label
        self.instruction_label = tk.Label(self.main_frame, text="Press 'Start' to begin Stage 1", font=("Arial", 12))
        self.instruction_label.pack(pady=10)
        
        # Start Button
        self.start_button = tk.Button(self.main_frame, text="Start", font=("Arial", 12), command=self.start_stage)
        self.start_button.pack(pady=10)
        
        # Placeholder for Dynamic Content
        self.dynamic_frame = tk.Frame(self.main_frame)
        self.dynamic_frame.pack(pady=20)

    def start_stage(self):
        """Start the current stage."""
        for widget in self.dynamic_frame.winfo_children():
            widget.destroy()
        
        if self.current_stage == 1:
            self.load_stage_1()
        elif self.current_stage == 2:
            self.load_stage_2()
        elif self.current_stage == 3:
            self.load_stage_3()
        else:
            messagebox.showinfo("Game Complete", "Congratulations! You've completed all stages.")
    
    def load_stage_1(self):
        """Stage 1: Denoising EEG Signals."""
        self.instruction_label.config(text="Stage 1: Denoising EEG Signals")

        # Canvas dimensions
        canvas_width = 800
        canvas_height = 200  # Height for each subplot

        # Create two canvases for FP1 and FP2
        canvas_fp1 = tk.Canvas(self.dynamic_frame, width=canvas_width, height=canvas_height + 50, bg="white")
        canvas_fp2 = tk.Canvas(self.dynamic_frame, width=canvas_width, height=canvas_height + 50, bg="white")
        
        canvas_fp1.pack()
        canvas_fp2.pack()

        # Plot scaling factors
        scale_factor_x = canvas_width / len(time)
        scale_factor_y_fp1 = canvas_height / (np.max(channel_1_dcr) - np.min(channel_1_dcr))
        scale_factor_y_fp2 = canvas_height / (np.max(channel_2_dcr) - np.min(channel_2_dcr))

        # Function to plot a signal on a Tkinter Canvas
        def plot_signal(canvas, signal_data, color, scale_factor_y):
            points = []
            for i in range(len(signal_data)):
                x = i * scale_factor_x
                y = canvas_height / 2 - (signal_data[i] * scale_factor_y)
                points.append((x, y))
            for i in range(len(points) - 1):
                canvas.create_line(points[i][0], points[i][1], points[i + 1][0], points[i + 1][1], fill=color, width=2)

        # Plot original signals
        plot_signal(canvas_fp1, channel_1_dcr, "blue", scale_factor_y_fp1)
        plot_signal(canvas_fp2, channel_2_dcr, "orange", scale_factor_y_fp2)

        # Placeholder for filtered signals
        filtered_lines_fp1 = []
        filtered_lines_fp2 = []

        def update_filtered_signal(cutoff):
            """Update filtered signals based on slider or entry value."""
            nonlocal filtered_lines_fp1, filtered_lines_fp2

            # Clear previous filtered lines
            for line in filtered_lines_fp1:
                canvas_fp1.delete(line)
            for line in filtered_lines_fp2:
                canvas_fp2.delete(line)

            # Apply low-pass filter to both channels
            filtered_channel_1 = butter_lowpass_filter(channel_1_dcr, cutoff, fs)
            filtered_channel_2 = butter_lowpass_filter(channel_2_dcr, cutoff, fs)

            # Plot new filtered signals
            def plot_filtered(canvas, signal_data, color, scale_factor_y):
                points = []
                lines = []
                for i in range(len(signal_data)):
                    x = i * scale_factor_x
                    y = canvas_height / 2 - (signal_data[i] * scale_factor_y)
                    points.append((x, y))
                for i in range(len(points) - 1):
                    line_id = canvas.create_line(
                        points[i][0], points[i][1], points[i + 1][0], points[i + 1][1],
                        fill=color, width=2, dash=(4,)
                    )
                    lines.append(line_id)
                return lines

            # Update filtered lines for FP1 and FP2
            filtered_lines_fp1 = plot_filtered(canvas_fp1, filtered_channel_1, "green", scale_factor_y_fp1)
            filtered_lines_fp2 = plot_filtered(canvas_fp2, filtered_channel_2, "red", scale_factor_y_fp2)

        def update_slider_from_entry(event):
            """Update slider position when user enters a value."""
            try:
                value = float(entry_cutoff.get())
                if 0.5 <= value <= 50.0:
                    cutoff_slider.set(value)
                    update_filtered_signal(value)
                else:
                    messagebox.showerror("Invalid Input", "Please enter a value between 0.5 and 50.0 Hz.")
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a numeric value.")

        def update_entry_from_slider(val):
            """Update entry box when slider is moved."""
            entry_cutoff.delete(0, tk.END)
            entry_cutoff.insert(0, f"{float(val):.1f}")
            update_filtered_signal(float(val))

        # Slider for cutoff frequency adjustment
        cutoff_slider_label = tk.Label(self.dynamic_frame, text="Adjust Cutoff Frequency (Hz):", font=("Arial", 12))
        cutoff_slider_label.pack(pady=5)

        cutoff_slider_value = tk.DoubleVar(value=5.0)  # Initial value of slider

        cutoff_slider = tk.Scale(
            self.dynamic_frame,
            from_=0.5,
            to=50.0,
            resolution=0.5,
            orient=tk.HORIZONTAL,
            length=600,
            variable=cutoff_slider_value,
            command=lambda val: update_entry_from_slider(val),
        )
        
        cutoff_slider.pack()

        # Entry box for direct input of cutoff frequency
        entry_label = tk.Label(self.dynamic_frame, text="Enter Cutoff Frequency (Hz):", font=("Arial", 12))
        entry_label.pack(pady=5)

        entry_cutoff = tk.Entry(self.dynamic_frame, font=("Arial", 12), width=10)
        entry_cutoff.insert(0, "5.0")  # Default value
        entry_cutoff.bind("<Return>", update_slider_from_entry)  # Update slider when Enter is pressed
        entry_cutoff.pack()

        # Next Stage Button (disabled initially)
        next_button = tk.Button(self.dynamic_frame, text="Next Stage", font=("Arial", 12), state=tk.DISABLED,
                                command=self.next_stage)

        def enable_next_stage():
            """Enable the Next Stage button once settings are selected."""
            next_button.config(state=tk.NORMAL)

            confirm_button = tk.Button(self.dynamic_frame, text="Confirm Settings", font=("Arial", 12),
                               command=enable_next_stage)
    
            confirm_button.pack(pady=10)
            next_button.pack(pady=10)



    def load_stage_2(self):
        """Stage 2: Thresholding to Identify Eye Blinks."""
        self.instruction_label.config(text="Stage 2: Thresholding to Identify Eye Blinks")
        
    def load_stage_3(self):
        """Stage 3: Build an ML Classifier."""
        self.instruction_label.config(text="Stage 3: Build an ML Classifier")
        
    def next_stage(self):
        """Proceed to the next stage."""
        if self.current_stage < 3:
            self.current_stage += 1
            self.start_stage()
    
if __name__ == "__main__":
    root = tk.Tk()
    app = NeuroGameApp(root)
    root.mainloop()
