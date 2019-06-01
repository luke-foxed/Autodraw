# Autodraw

## What It Does
This python script works by scanning a user-selected image and using PIL to find it's edges and applying additional filters to return a monchrome image. Then the filtered image is scanned for white pixels, which are subsequently written to a temporary text file. From here, GUI automation through pynput is used to click each of these coordinates from the text file - recreating the image. This drawing can then be saved by storing the text file in the 'drawings' folder to be reused.

## Usage

- Install the required packackes using `pip install -r requirements.txt`
- Run the script and either redraw an existing image from the 'drawings' folder, or open a new image and draw it

## Made With

- pynput (GUI automation)
- tkinter (Dialog box)
- pillow (Image processing)
- tqdm  (Progress bar)
- colorama (Colored printing)

