# -*- coding: utf-8 -*-
"""F1 2023: Verstappen vs. the grid — lap-time pace and consistency analysis."""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

print("Loading datasets...")
drivers = pd.read_csv('/content/drivers.csv')
races = pd.read_csv('/content/races.csv')
lap_times = pd.read_csv('/content/lap_times.csv', usecols=['raceId', 'driverId', 'milliseconds'])

# 1. Isolating Verstappen to compare his baseline against the field
races_2023 = races[races['year'] == 2023]
race_ids_2023 = races_2023['raceId'].tolist()
max_v = drivers[drivers['driverRef'] == 'max_verstappen']
max_id = max_v['driverId'].values[0]

# 2. Extract laps and convert to seconds
laps_2023 = lap_times[lap_times['raceId'].isin(race_ids_2023)].copy()
laps_2023['lap_time_sec'] = laps_2023['milliseconds'] / 1000

# Dropping pit stops, red flags, and safety car laps so the density curve doesn't break
# We only keep laps between 70 and 110 seconds.
clean_laps = laps_2023[(laps_2023['lap_time_sec'] >= 70) & (laps_2023['lap_time_sec'] <= 110)]

# 3. Separate the datasets
max_laps = clean_laps[clean_laps['driverId'] == max_id]
grid_laps = clean_laps[clean_laps['driverId'] != max_id]

# 3.5 Quantify the gap — the actual numbers behind the chart
# Median captures typical pace (robust to the odd slow lap); std captures consistency.
# Note: laps are pooled across all 2023 circuits. Both groups span the same races, so the
# comparison is broadly fair, but it is not normalised per-circuit (see README limitations).
max_median = max_laps['lap_time_sec'].median()
grid_median = grid_laps['lap_time_sec'].median()
max_std = max_laps['lap_time_sec'].std()
grid_std = grid_laps['lap_time_sec'].std()

pace_gap = grid_median - max_median                      # seconds/lap; positive = Verstappen faster
consistency_gap = (grid_std - max_std) / grid_std * 100  # %; positive = Verstappen tighter spread

print("\n--- Summary statistics (green-flag laps, 70-110s) ---")
print(f"Verstappen   : median {max_median:.3f}s | std {max_std:.3f}s | n = {len(max_laps)}")
print(f"Rest of grid : median {grid_median:.3f}s | std {grid_std:.3f}s | n = {len(grid_laps)}")
print(f"Pace gap        : {pace_gap:+.3f}s per lap (median; positive = Verstappen faster)")
print(f"Consistency gap : {consistency_gap:+.1f}% tighter spread for Verstappen")
print("-> Paste these into the README's 'What the chart shows' section.")
print("------------------------------------------------------\n")

# 4. Generate Upgraded Visualization
print("Data cleaned. Generating upgraded visualization...")
plt.figure(figsize=(12, 6))

# Using a Histogram + KDE for a much more robust look
sns.histplot(grid_laps['lap_time_sec'], label='Rest of the Grid', color='gray', stat='density', bins=40, alpha=0.3, kde=True, line_kws={'linewidth': 2})
sns.histplot(max_laps['lap_time_sec'], label='Max Verstappen', color='blue', stat='density', bins=40, alpha=0.5, kde=True, line_kws={'linewidth': 2})

# Formatting
plt.title('F1 2023 Season: Lap Time Consistency (Verstappen vs. Grid)', fontsize=16, fontweight='bold', pad=15)
plt.xlabel('Lap Time (Seconds)', fontsize=12)
plt.ylabel('Density (Frequency of Pace)', fontsize=12)
plt.legend(fontsize=11)
plt.grid(axis='both', linestyle='--', alpha=0.5)
plt.tight_layout()

# Render
plt.show()
print("Success! Right-click and save this image.")
