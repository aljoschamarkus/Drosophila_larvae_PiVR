# Drosophila larvae data processing

## Overview
> Project to analyse and visualise video data of Drosophila melanogaster behavioural experiments. Extracting Basic movement Parameters such as speed and midline offset, as well as Group features such as neighbour distances and encounter Analysis.

## Project structure

- `config_parameters` contains relevant parameters: video metadata, Arena size, genotypes, plotting choices, etc.
- `util_data_preperation` contains functions to process the raw data and extract the relevant features.
- `MAIN_data_preparation.py` reads the raw data (csv), overlays and scales it and saves it into a multi indexed data frame
#### bash (subdirectory)
contains files for the tracking via `TRex` 2 beta software
- `bash_execute.py` automates the execution of `TRex` via bash scripts
- `beta_groups.settings` contains the settings for the Tracking
- `ffmpeg_video_conversion.sh` converts h264 videos to mp4
- `TRex_tracking.sh` is the bash script to track the videos

## Data Structure

### Required input data structure
The data should be stored in a directory structure as follows:
- The main directory contains two subdirectories: `sub_dir_groups` and `sub_dir_singles`.
- Each of these subdirectories contains several sub-subdirectories with the data.
- The data is stored in a `data` subdirectory within each sub-subdirectory.


- The `sub_sub_dir_group_name1` are stored individually as a default by the `PiVR`
- The data directories and the png-files are stored this way by `TRex` as a default
```
|-main_dir
|   |-sub_dir_groups
|   |   |-sub_sub_dir_group_name1
|   |   |   |-data
|   |   |   |   |-file0.csv
|   |   |   |   |-[...]
|   |   |   |-sub_sub_dir_group_name1.png
|   |   |   |-[...]
|   |   |-[...]
|   |-sub_dir_singles
|   |   |-sub_sub_dir_single_name1
|   |   |   |-data
|   |   |   |   |-file0.csv
|   |   |   |   |-[...]
|   |   |   |-sub_sub_dir_single_name1.png
|   |   |   |-[...]
|   |   |-[...]
```
The csv-files contain the following (relevant) columns:
- `frame` the frame number
- `MIDLINE_OFFSET` the midline offset of the larva
- `SPEED#wcentroid (cm/s)` the speed of the larva which is not actually in cm/s but in pixels per frame
- `X#wcentroid (cm)` the x-coordinate of the larva
- `Y#wcentroid (cm)` the y-coordinate of the larva

  The multi indexed pandas data frames are stored in a pickle file with the following structure:

- df_initial.pkl
    - Index names: ['sub_dir', 'condition', 'genotype', 'individual_id', 'frame']
    - Columns: ['midline_offset', 'speed', 'x', 'y', 'midline_offset_signless']

- df_group_parameters.pkl
    - Index names: ['sub_dir', 'condition', 'genotype', 'group_type', 'group_id', 'individual_id', 'frame']
    - Columns: ['midline_offset', 'speed', 'x', 'y', 'midline_offset_signless', 'pairwise_distance', 'nearest_neighbor_distance', 'encounter_count']