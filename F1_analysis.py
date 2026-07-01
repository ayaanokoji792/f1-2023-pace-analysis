# -*- coding: utf-8 -*-
"""F1 2023: Verstappen vs. the grid — lap-time pace and consistency analysis."""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

print("Loading datasets...")
# Colab: upload the three CSVs to /content/. Running locally: change these to './drivers.csv' etc.
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

# 3.5 POOLED summary — quick headline numbers (pace is reliable; the std is circuit-inflated)
max_median = max_laps['lap_time_sec'].median()
grid_median = grid_laps['lap_time_sec'].median()
max_std = max_laps['lap_time_sec'].std()
grid_std = grid_laps['lap_time_sec'].std()
pace_gap = grid_median - max_median
consistency_gap = (grid_std - max_std) / grid_std * 100

print("\n--- Pooled statistics (all circuits together, green-flag laps) ---")
print(f"Verstappen   : median {max_median:.3f}s | std {max_std:.3f}s | n = {len(max_laps)}")
print(f"Rest of grid : median {grid_median:.3f}s | std {grid_std:.3f}s | n = {len(grid_laps)}")
print(f"Pace gap        : {pace_gap:+.3f}s per lap (reliable)")
print(f"Consistency gap : {consistency_gap:+.1f}% (WARNING: std inflated by pooling circuits)")
print("------------------------------------------------------------------")

# 3.6 PER-CIRCUIT NORMALIZED consistency — the honest way to measure it.
# For each race, take every driver's OWN lap-to-lap std, then compare Verstappen's
# spread to the typical (median) driver's spread AT THAT SAME CIRCUIT. Averaging these
# race-by-race removes circuit variance AND compares like-with-like (driver vs driver).
per_race = []
for rid in race_ids_2023:
    race_laps = clean_laps[clean_laps['raceId'] == rid]
    lap_counts = race_laps.groupby('driverId')['lap_time_sec'].size()
    valid_drivers = lap_counts[lap_counts >= 5].index          # need enough laps for a stable std
    rl = race_laps[race_laps['driverId'].isin(valid_drivers)]
    if max_id not in valid_drivers or len(valid_drivers) < 5:
        continue
    driver_std = rl.groupby('driverId')['lap_time_sec'].std()
    driver_med = rl.groupby('driverId')['lap_time_sec'].median()
    per_race.append({
        'raceId': rid,
        'v_std': driver_std[max_id],                            # Verstappen's spread this race
        'field_std': driver_std.drop(max_id).median(),          # a typical driver's spread this race
        'pace_delta': driver_med.drop(max_id).median() - driver_med[max_id],  # +ve = VER faster
    })

per_race = pd.DataFrame(per_race)
per_race['spread_ratio'] = per_race['v_std'] / per_race['field_std']   # <1 = VER more consistent

mean_spread_ratio = per_race['spread_ratio'].mean()
consistency_gap_norm = (1 - mean_spread_ratio) * 100          # +ve = VER tighter than typical driver
mean_pace_delta = per_race['pace_delta'].mean()               # circuit-fair pace advantage (s/lap)
races_more_consistent = int((per_race['spread_ratio'] < 1).sum())
n_races = len(per_race)

print("\n--- Per-circuit normalized (the defensible consistency metric) ---")
print(f"Races analysed                 : {n_races}")
print(f"Verstappen's spread vs typical : {mean_spread_ratio:.3f}x the field's")
print(f"Consistency edge (normalized)  : {consistency_gap_norm:+.1f}% tighter than a typical driver")
print(f"More consistent than the field : in {races_more_consistent} of {n_races} races")
print(f"Pace advantage (circuit-fair)  : {mean_pace_delta:+.3f}s per lap")
print("-> Paste the normalized consistency figure into the README.")
print("------------------------------------------------------------------\n")

# 4. Generate Visualization
print("Generating visualization...")
plt.figure(figsize=(12, 6))
sns.histplot(grid_laps['lap_time_sec'], label='Rest of the Grid', color='gray', stat='density', bins=40, alpha=0.3, kde=True, line_kws={'linewidth': 2})
sns.histplot(max_laps['lap_time_sec'], label='Max Verstappen', color='blue', stat='density', bins=40, alpha=0.5, kde=True, line_kws={'linewidth': 2})
plt.title('F1 2023 Season: Lap Time Distribution (Verstappen vs. Grid)', fontsize=16, fontweight='bold', pad=15)
plt.xlabel('Lap Time (Seconds)', fontsize=12)
plt.ylabel('Density (Frequency of Pace)', fontsize=12)
plt.legend(fontsize=11)
plt.grid(axis='both', linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()
print("Done.")
