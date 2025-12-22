import subprocess

CONDA="/Users/aljoscha/miniforge3"
TREX= CONDA + "/envs/beta/bin/TRex.app/Contents/MacOS/TRex"
print(TREX)

MAIN_DIR = '/Users/aljoscha/Downloads/2402_IAVxWT_4min_50p'
SETTINGS_FILE = '/bash/beta_group.settings'

# Pass the variable as an argument to the Bash script
subprocess.run(["bash", "ffmpeg_video_conversion.sh", MAIN_DIR])

subprocess.run(["bash", "TRex_tracking.sh", CONDA, TREX, MAIN_DIR, SETTINGS_FILE])