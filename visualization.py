import pandas as pd
import matplotlib.pyplot as plt

# Load EEG data from CSV (replace with your file path)
file_path = "eeg-data/Ecog_waveform_2.csv"  # Update with the actual path
eeg_data = pd.read_csv(file_path)

# Extract columns for visualization
time = eeg_data['Time (s)']  # Time in seconds
fp1 = eeg_data['FP1']        # Channel FP1
fp2 = eeg_data['FP2']        # Channel FP2

# Plot EEG data for both channels
plt.figure(figsize=(12, 6))
plt.plot(time, fp1, label="FP1", alpha=0.8)
plt.plot(time, fp2, label="FP2", alpha=0.8)
plt.title("Raw EEG Data")
plt.xlabel("Time (s)")
plt.ylabel("Amplitude (μV)")
plt.legend()
plt.grid(True)
plt.show()
