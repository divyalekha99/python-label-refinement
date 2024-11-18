import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path

# Paths to your result CSV files
bpi_challenge_2013 = Path('/Users/divyalekhas/Documents/Masters/replication_new/results/BPI13_closed_VARIANTS_NEW.csv')
road_traffic_fines = Path('/Users/divyalekhas/Documents/Masters/replication_new/results/Road_fine_short_VARIANTS_NEW.csv')
road_traffic_fines_long = Path('/Users/divyalekhas/Documents/Masters/replication_new/results/Road_fine_VARIANTS_NEW.csv')
environmental_permit = Path('/Users/divyalekhas/Documents/Masters/replication_new/results/Permit.csv')


def load_csv_data(path):
    try:
        df = pd.read_csv(path)
        df['refined_f1_score'] = 2 * (df['Precision Align'] * df['Fitness']) / (df['Precision Align'] + df['Fitness'])
        df['unrefined_f1_score'] = 2 * (df['original_precision'] * df['original_fitness']) / (df['original_precision'] + df['original_fitness'])
        return df
    except Exception as e:
        print(f"Error loading {path}: {e}")
        return pd.DataFrame()


df_bpi_challenge_2013 = load_csv_data(bpi_challenge_2013)
df_road_traffic_fines = load_csv_data(road_traffic_fines)
df_road_traffic_fines_long = load_csv_data(road_traffic_fines_long)
df_environmental_permit = load_csv_data(environmental_permit)


bpi_2013_runtime = df_bpi_challenge_2013['Runtime'].mean()
road_fines_runtime = df_road_traffic_fines['Runtime'].mean()
road_fines_long_runtime = df_road_traffic_fines_long['Runtime'].mean()
environmental_permit_runtime = df_environmental_permit['Runtime'].mean()


print("Average Runtime:")
print(f"BPI Challenge 2013: {bpi_2013_runtime:.2f} seconds")
print(f"Road Traffic Fines Short: {road_fines_runtime:.2f} seconds")
print(f"Road Traffic Fines Long: {road_fines_long_runtime:.2f} seconds")
print(f"Environmental Permit: {environmental_permit_runtime:.2f} seconds")


def print_metrics(df, label):
    if not df.empty:
        refined_max_precision = df['Precision Align'].max()
        refined_avg_precision = df['Precision Align'].mean()
        refined_max_f1_score = df['refined_f1_score'].max()
        refined_avg_f1_score = df['refined_f1_score'].mean()

        unrefined_avg_precision = df['original_precision'].mean()
        unrefined_max_precision = df['original_precision'].max()
        unrefined_avg_f1_score = df['unrefined_f1_score'].mean()
        unrefined_max_f1_score = df['unrefined_f1_score'].max()

        print(f"\nMetrics for {label}:")
        print(f"Unrefined Average Precision: {unrefined_avg_precision:.4f}")
        print(f"Unrefined Max Precision: {unrefined_max_precision:.4f}")
        print(f"Unrefined Average F1-Score: {unrefined_avg_f1_score:.4f}")
        print(f"Unrefined Max F1-Score: {unrefined_max_f1_score:.4f}")
        print(f"Refined Max Precision: {refined_max_precision:.4f}")
        print(f"Refined Average Precision: {refined_avg_precision:.4f}")
        print(f"Refined Max F1-Score: {refined_max_f1_score:.4f}")
        print(f"Refined Average F1-Score: {refined_avg_f1_score:.4f}")


print_metrics(df_bpi_challenge_2013, "BPI Challenge 2013")
print_metrics(df_road_traffic_fines, "Road Traffic Fines Short")
print_metrics(df_road_traffic_fines_long, "Road Traffic Fines Long")
print_metrics(df_environmental_permit, "Environmental Permit")


unrefined_avg_precision_bpi = df_bpi_challenge_2013['original_precision'].mean()
unrefined_avg_precision_road_fines = df_road_traffic_fines['original_precision'].mean()
unrefined_avg_precision_road_fines_long = df_road_traffic_fines_long['original_precision'].mean()
unrefined_avg_precision_environmental_permit = df_environmental_permit['original_precision'].mean()


plt.figure()
fig, ax = plt.subplots()
bp1 = ax.boxplot(df_bpi_challenge_2013['Precision Align'], positions=[1], patch_artist=True, boxprops=dict(facecolor="C0"))
bp2 = ax.boxplot(df_road_traffic_fines['Precision Align'], positions=[2], patch_artist=True, boxprops=dict(facecolor="C2"))
bp3 = ax.boxplot(df_environmental_permit['Precision Align'], positions=[3], patch_artist=True, boxprops=dict(facecolor="C3"))



ax.hlines(y=unrefined_avg_precision_bpi, xmin=0.85, xmax=1.15, color='r', linestyles='dashed')  # BPI 2013
ax.hlines(y=unrefined_avg_precision_road_fines, xmin=1.85, xmax=2.15, color='r', linestyles='dashed')
ax.hlines(y=unrefined_avg_precision_environmental_permit, xmin=2.85, xmax=3.15, color='r', linestyles='dashed')  # Environmental Permit


ax.set_yticks(np.linspace(0, 1, 11))
ax.set_ylim([0, 1])
ax.legend([bp1["boxes"][0], bp2["boxes"][0], bp3["boxes"][0]],
          ['BPI Challenge 2013', 'Road Traffic Fines', 'Environmental Permit'],
          loc='upper center', bbox_to_anchor=(0.5, 1.16), ncol=2, fancybox=True)
plt.xticks(list(range(1, 4)), ['BPI 2013', 'Road Traffic Fines', 'Environmental Permit'])
plt.subplots_adjust(bottom=0.15)

plt.xlabel('Event Log')
plt.ylabel('Precision')
plt.title('Precision Comparison Across Event Logs')
plt.savefig('/Users/divyalekhas/Documents/Masters/replication_new/average_precision_comparison.png', dpi=300)
plt.show()
