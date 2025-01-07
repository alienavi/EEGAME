import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from scipy.signal import butter, filtfilt

# Load data
eeg_data = pd.read_csv('eeg-data/Ecog_waveform_2.csv')
time = eeg_data['Time (s)']
channel1 = eeg_data['FP1']
channel2 = eeg_data['FP2']

# Butterworth filter function
def butter_lowpass_filter(data, cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return filtfilt(b, a, data)

def highpass_filter(data, cutoff, fs, order=5):
    # Create a Butterworth high-pass filter
    nyquist = 0.5 * fs  # Nyquist frequency
    normal_cutoff = cutoff / nyquist  # Normalized cutoff frequency
    b, a = butter(order, normal_cutoff, btype='high', analog=False)  # Butterworth filter coefficients
    y = filtfilt(b, a, data)  # Apply the filter to the data
    return y

# Sampling frequency (estimated from time difference)
fs = 250

# Initial cutoff frequency (but no initial filtering applied)
initial_cutoff = 5.0

# Plotting
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6))
plt.subplots_adjust(left=0.1, bottom=0.25)


channel_1_dcr= highpass_filter(channel1, 0.1, fs)
channel_2_dcr=highpass_filter(channel2, 0.1, fs)

# Plot original signals only
line1, = ax1.plot(time, channel_1_dcr, label='Original FP1', color='blue')
ax1.set_title("EEG Channel FP1")
ax1.legend()

line2, = ax2.plot(time, channel_2_dcr, label='Original FP2', color='orange')
ax2.set_title("EEG Channel FP2")
ax2.legend()

# Placeholder lines for the filtered data, initially set to the original signal values
line1_f, = ax1.plot(time, channel_1_dcr, label='Filtered FP1', color='green', alpha=0.7, linestyle='--')
line2_f, = ax2.plot(time, channel_2_dcr, label='Filtered FP2', color='red', alpha=0.7, linestyle='--')

# Hide the filtered lines initially
line1_f.set_visible(False)
line2_f.set_visible(False)

# Slider for cutoff frequency
ax_cutoff = plt.axes([0.1, 0.1, 0.8, 0.03], facecolor='lightgoldenrodyellow')
cutoff_slider = Slider(ax_cutoff, 'Cutoff Frequency (Hz)', 0.1, 50.0, valinit=initial_cutoff)

# Update function for slider
def update(val):
    cutoff = cutoff_slider.val
    filtered_channel1 = butter_lowpass_filter(channel_1_dcr, cutoff, fs)
    filtered_channel2 = butter_lowpass_filter(channel_2_dcr, cutoff, fs)
    
    # Set the filtered data to the new lines
    line1_f.set_ydata(filtered_channel1)
    line2_f.set_ydata(filtered_channel2)
    
    # Make the filtered lines visible
    line1_f.set_visible(True)
    line2_f.set_visible(True)
    ax1.legend()
    ax2.legend()
    
    fig.canvas.draw_idle()

cutoff_slider.on_changed(update)

plt.show()

""" import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
from scipy.signal import butter, filtfilt

# Load data
eeg_data = pd.read_csv('Ecog_waveform_2.csv')
time = eeg_data['Time (s)']
channel1 = eeg_data['FP1']
channel2 = eeg_data['FP2']

# Butterworth filter functions
def butter_lowpass_filter(data, cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return filtfilt(b, a, data)

def highpass_filter(data, cutoff, fs, order=5):
    nyq = 0.5 * fs  # Define the Nyquist frequency
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='high', analog=False)
    return filtfilt(b, a, data)

# Sampling frequency (estimated from time difference)
fs = 250

# Initial cutoff frequency (for low-pass filtering)
initial_cutoff = 5.0

# Plotting setup
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6))
plt.subplots_adjust(left=0.1, bottom=0.25)

# Plot original signals only
line1, = ax1.plot(time, channel1, label='Original FP1', color='blue')
ax1.set_title("EEG Channel FP1")
ax1.legend()

line2, = ax2.plot(time, channel2, label='Original FP2', color='orange')
ax2.set_title("EEG Channel FP2")
ax2.legend()

# Placeholder lines for the filtered data, initially set to the original signal values
line1_f, = ax1.plot(time, channel1, label='Filtered FP1', color='green', alpha=0.7, linestyle='--')
line2_f, = ax2.plot(time, channel2, label='Filtered FP2', color='red', alpha=0.7, linestyle='--')

# Hide the filtered lines initially
line1_f.set_visible(False)
line2_f.set_visible(False)

# Button for removing DC shift (applying high-pass filter)
ax_button = plt.axes([0.1, 0.15, 0.3, 0.05])
button = Button(ax_button, 'Remove DC Shift')

# Function to handle button click
def remove_dc_shift(event):
    # Apply high-pass filter to the original channels
    filtered_channel1 = highpass_filter(channel1, 0.1, fs)
    filtered_channel2 = highpass_filter(channel2, 0.1, fs)
    
    # Update the filtered data to the new lines
    line1_f.set_ydata(filtered_channel1)
    line2_f.set_ydata(filtered_channel2)

    # Make the filtered lines visible
    line1_f.set_visible(True)
    line2_f.set_visible(True)
    
    ax1.legend()
    ax2.legend()
    fig.canvas.draw_idle()

# Connect button click event to the remove_dc_shift function
button.on_clicked(remove_dc_shift)

# Slider for low-pass cutoff frequency
ax_cutoff = plt.axes([0.1, 0.1, 0.8, 0.03], facecolor='lightgoldenrodyellow')
cutoff_slider = Slider(ax_cutoff, 'Cutoff Frequency (Hz)', 0.1, 50.0, valinit=initial_cutoff)

# Update function for slider
def update(val):
    # Only update if the high-pass filtered lines are visible
    if line1_f.get_visible():
        cutoff = cutoff_slider.val
        
        # Get the current high-pass filtered data
        highpass_data1 = line1_f.get_ydata()
        highpass_data2 = line2_f.get_ydata()
        
        # Apply low-pass filter to the high-pass filtered data
        lowpass_channel1 = butter_lowpass_filter(highpass_data1, cutoff, fs)
        lowpass_channel2 = butter_lowpass_filter(highpass_data2, cutoff, fs)
        
        # Update the filtered lines with low-pass filtered data
        line1_f.set_ydata(lowpass_channel1)
        line2_f.set_ydata(lowpass_channel2)
        
        fig.canvas.draw_idle()

cutoff_slider.on_changed(update)

plt.show()
 """
