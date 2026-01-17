# Drosophila larvae data processing

## Requirements
The video tracking requires the [TRex](https://trex.run/) software (v2.0.0).

## Usage
- In [**bash_execute.py**](./bash/bash_execute.py) adjust:
  - `CONDA="..."` conda-based environment management system (e.g. "Users/aljoscha/miniforge3")
  - `TREX= CONDA + "..."` TRex path (e.g. "/envs/beta/bin/TRex.app/Contents/MacOS/TRex")
  - `MAIN_DIR = '...'` directory containing PiVR data (e.g. "/Users/aljoscha/Downloads/2402_IAVxWT_4min_50p")
- Run [**bash_execute.py**](./bash/bash_execute.py)
> now each subdirectory contains the with TREX tracked data in csv-files

If further data processing is needed: 
- Sort individual and group subdirectories in subdirectories whose names contain "group" and "single"
- In [**MAIN_data_prep.py**](./MAIN_data_prep.py) adjust the following, if unsure look up example in [**config_settings.py**](./config_settings.py):
  - project = "..."
  - main_dir = "..."
  - genotype = [...]
- Run [**MAIN_data_prep.py**](./MAIN_data_prep.py).

## Overview
> Data preprocessing of PiVR video data of *Drosophila melanogaster* behavioural experiments. Extracting movement Parameters such as position, speed and midline offset via TRex as well as further data analysis extracting group features such as neighbour distances and encounter.

## Project structure
- [**config_settings.py**](./config_settings.py) contains relevant parameters: video metadata, Arena size, genotypes, plotting choices, etc.
- [**util_data_prep**](./util_data_prep.py) contains functions to process the raw data and extract the relevant features.
- [**MAIN_data_prep.py**](./MAIN_data_prep.py) reads the raw data (csv), overlays and scales it and saves it into a multi indexed data frame 
- [**bash** (subdirectory)](./bash) contains files for video conversion and the tracking via **TRex** 2 beta software
  - [**bash_execute.py**](./bash/bash_execute.py) automates the execution of **TRex** via bash scripts
  - [**beta_groups.settings**](./bash/beta_group.settings) contains the settings for the Tracking
  - [**ffmpeg_video_conversion.sh**](./bash/ffmpeg_video_conversion.sh) converts h264 videos to mp4
  - [**TRex_tracking.sh**](./bash/TRex_tracking.sh) is the bash script to track the videos


## Data Structure

### Video conversion & TRex tracking
Directory structure required for video conversion and **TRex** tracking. This is the default output of the **PiVR** for video recordings.
```
|-main_dir
|   |-sub_dir_name1
|   |   |   |-video_file.h264
|   |   |   |-2025.12.23_17-30-00_data.csv
|   |   |   |-experiment_settings.json
|   |   |   |-stimulation_used.csv
|   |-sub_dir_name2
|   |   |   |-[...]
|   |-[...]
```
### Preprocessing
For the further data processing using [MAIN_data_prep.py](./MAIN_data_prep.py) data should contain the TRex tracking output (`./data/file_name.csv`, `./sub_sub_dir_name.png`) and be stored in a directory structure as follows:
- The main directory contains two subdirectories: **sub_dir_groups** and **sub_dir_singles**.
- Each of these subdirectories contains several sub-subdirectories with the data.
- The data is stored in a **data** subdirectory within each sub-subdirectory.
<p>

- **sub_sub_dir_group_name1** -> default structure of **PiVR** output
- png-files and `data` directory containing csv-files -> default structure **TRex** output
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

### Output
The multi indexed pandas data frames are stored in a pickle file with the following structure:

- df_initial.pkl
    - Index names: `['sub_dir', 'condition', 'genotype', 'individual_id', 'frame']`
    - Columns: `['midline_offset', 'speed', 'x', 'y', 'midline_offset_signless']`

- df_group_parameters.pkl
    - Index names: `['sub_dir', 'condition', 'genotype', 'group_type', 'group_id', 'individual_id', 'frame']`
    - Columns: `['midline_offset', 'speed', 'x', 'y', 'midline_offset_signless', 'pairwise_distance', 'nearest_neighbor_distance', 'encounter_count']`
