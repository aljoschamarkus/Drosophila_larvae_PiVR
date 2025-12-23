import os
import cv2
import numpy as np
import pandas as pd

from config_settings import bootstrap_reps_p2
from util_data_prep import handle_main_dir_p2
from util_data_prep import create_mapping_actual_groups
from util_data_prep import create_mapping_artificial_groups_bootstrapped
from util_data_prep import compute_pairwise_distances_and_encounters

import config_settings

# Constants and configuration
project = 'nompC_10'
main_dir = "/Users/aljoscha/Downloads/2402_IAVxWT_4min_50p"
genotype = ["IAVxWT"]

circle_default = [7, 7, 6.5]
group_size = 5
bootstrap_reps = 5

fps = 30
# speed_avg_threshold = config_settings.speed_avg_threshold
# speed_avg_window = 5
encounter_distance_threshold = 1

counter = 0

# Prepare the output data
data_frame = []

# Get the directory structure
results_data_dir, results_plt_dir = handle_main_dir_p2()

# Process each subdirectory in main_dir
for sub_dir in os.listdir(main_dir):
    sub_dir_path = os.path.join(main_dir, sub_dir)
    if not os.path.isdir(sub_dir_path):
        continue

    # Identify condition from folder name
    if "group" in sub_dir.lower():
        cond = "group"
    elif "single" in sub_dir.lower():
        cond = "single"
    else:
        print(f"Skipping: {sub_dir} (Unknown condition)")
        continue  # Skip unknown conditions

    # Identify the genotype from the folder name
    geno = next((g for g in genotype if g in sub_dir), None)
    if not geno:
        print(f"Skipping: {sub_dir} (No matching genotype)")
        continue

    # Process images in the subdirectory
    x_mid, y_mid, radius = None, None, None  # Initialize circle values
    conversion_factor = None
    for png_file in os.listdir(sub_dir_path):
        if png_file.endswith('.png'):
            image_path = os.path.join(sub_dir_path, png_file)
            image = cv2.imread(image_path, cv2.IMREAD_COLOR)
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            blurred_image = cv2.GaussianBlur(gray_image, (9, 9), 2)

            # Detect circles
            detected_circles = cv2.HoughCircles(
                blurred_image, cv2.HOUGH_GRADIENT,
                dp=1.2, minDist=100,
                param1=50, param2=30,
                minRadius=10, maxRadius=500
            )

            if detected_circles is not None:
                detected_circles = np.uint16(np.around(detected_circles))
                largest_circle = max(detected_circles[0, :], key=lambda c: c[2])
                x_mid, y_mid, radius = largest_circle
                conversion_factor = circle_default[2] / radius
                # print(conversion_factor)
            break  # Stop after processing the first image

    # Process CSV files in the subdirectory
    data_dir = os.path.join(sub_dir_path, 'data')
    if os.path.isdir(data_dir):
        for csv_file in os.listdir(data_dir):
            if csv_file.endswith('.csv'):
                csv_path = os.path.join(data_dir, csv_file)
                csv_data = pd.read_csv(csv_path, usecols=['frame', 'X#wcentroid (cm)', 'Y#wcentroid (cm)', 'SPEED#wcentroid (cm/s)', 'MIDLINE_OFFSET'])

                distances = np.sqrt((csv_data['X#wcentroid (cm)'] - x_mid)**2 + (csv_data['Y#wcentroid (cm)'] - y_mid)**2)
                mask = distances > 1.05 * radius
                csv_data.loc[mask, ['X#wcentroid (cm)', 'Y#wcentroid (cm)']] = np.nan

                csv_data['X#wcentroid (cm)'] -= x_mid
                csv_data['Y#wcentroid (cm)'] -= y_mid
                csv_data['X#wcentroid (cm)'] *= conversion_factor
                csv_data['Y#wcentroid (cm)'] *= conversion_factor
                csv_data['X#wcentroid (cm)'] += circle_default[0]
                csv_data['Y#wcentroid (cm)'] += circle_default[1]
                csv_data['SPEED#wcentroid (cm/s)'] *= conversion_factor
                csv_data['speed_trex'] = csv_data['SPEED#wcentroid (cm/s)']


                def compute_speed(csv_data, fps=fps):
                    """Calculate speed in cm/s from position data."""
                    dx = csv_data['X#wcentroid (cm)'].diff()
                    dy = csv_data['Y#wcentroid (cm)'].diff()
                    csv_data['speed_manual'] = np.sqrt(dx ** 2 + dy ** 2) * fps
                    return csv_data


                # def smooth_speed(csv_data, window=5, method='rolling', input_speed='speed_manual'):
                #     from scipy.signal import savgol_filter
                #     """Smooth speed using a rolling average or Savitzky-Golay filter."""
                #     if method == 'rolling':
                #         csv_data[input_speed] = csv_data[input_speed].rolling(window=window, center=True).mean()
                #     elif method == 'savgol':
                #         csv_data[input_speed] = savgol_filter(csv_data[input_speed], window_length=window, polyorder=2,
                #                                               mode='interp')
                #     return csv_data


                csv_data = compute_speed(csv_data, fps)
                # csv_data = smooth_speed(csv_data, speed_avg_window, method='rolling', input_speed='speed_processed')
                # csv_data = smooth_speed(csv_data, speed_avg_window, method='rolling', input_speed='speed_manual')

                # def plot_speed(csv_data):
                #     """Plot original and smoothed speed."""
                #     import matplotlib.pyplot as plt
                #     plt.figure(figsize=(10, 5))
                #     plt.plot(csv_data['frame'], csv_data['speed_manual'], label='manual Speed', linewidth=2)
                #     plt.plot(csv_data['frame'], csv_data['speed_processed'], label='Processed Speed', linewidth=2)
                #     plt.xlabel('Frame')
                #     plt.ylabel('Speed (cm/s)')
                #     plt.legend()
                #     plt.show()
                #
                #
                # plot_speed(csv_data)

                csv_data['midline_offset_signless'] = np.abs(csv_data['MIDLINE_OFFSET'])
                csv_data['sub_dir'] = sub_dir
                csv_data['condition'] = cond
                csv_data['genotype'] = geno
                csv_data['individual_id'] = f'I_ID_{counter}'

                data_frame.append(csv_data)
                counter += 1

# Combine all data
df_initial = pd.concat(data_frame, ignore_index=True)
df_initial.set_index(['sub_dir', 'condition', 'genotype', 'individual_id', 'frame'], inplace=True)
df_initial.rename(columns={
    'MIDLINE_OFFSET': 'midline_offset',
    'SPEED#wcentroid (cm/s)': 'speed',
    'X#wcentroid (cm)': 'x',
    'Y#wcentroid (cm)': 'y'
}, inplace=True)

df_initial.to_pickle(os.path.join(results_data_dir, f"df_initial_{project}.pkl"))


df1 = df_initial.xs('group', level='condition')
for geno in genotype:
    print(geno)
    df2 = df_initial.xs(('group', geno), level=['condition', 'genotype'])
    print(len(df2.index.get_level_values('sub_dir').unique()))
    print(len(df2.index.get_level_values('individual_id').unique()))
print('all')
print(len(df1.index.get_level_values('sub_dir').unique()))
print(len(df1.index.get_level_values('individual_id').unique()))

# Mapping Functions
mapping_functions = {
    "map_RGN": create_mapping_actual_groups,
    "map_AIB": create_mapping_artificial_groups_bootstrapped,
}

# mapping_conditions = {
#     "map_RGN": "group",
#     "map_AIB": "single",
# }

mapping_list = []
for name, func in mapping_functions.items():
    kwargs = {
        "df": df_initial,
    }
    if "group_size" in func.__code__.co_varnames:
        kwargs["group_size"] = group_size
    if "bootstrap_reps" in func.__code__.co_varnames:
        kwargs["bootstrap_reps"] = bootstrap_reps
    mapping_list.append(func(**kwargs))

map_RGN, map_AIB = mapping_list

print('map', len(map_RGN['group_id'].unique()))

map_RGN['group_type'] = 'group'
map_AIB['group_type'] = 'single'

map_combined = pd.concat([map_RGN, map_AIB])
df_merged = df_initial.reset_index().merge(map_combined, on='individual_id', how='inner')
df_groups = df_merged.set_index(['sub_dir', 'condition', 'genotype', 'group_type', 'group_id', 'individual_id', 'frame'])
# df_groups.to_pickle(os.path.join(results_data_dir, "df_groups_p2.pkl"))

df_group_parameters = compute_pairwise_distances_and_encounters(df_groups, encounter_distance_threshold)
df_group_parameters.to_pickle(os.path.join(results_data_dir, f"df_group_parameters_{project}.pkl"))
