"""
Author: Luke Fox
Script: autodraw.py
Description: This script takes in an input image, then using PIL to find the edges and convert the image to monochrome.
             Then, the remaining white pixels are mapped to a text file which is read by pynput. An online paint app is
             opened and pynput clicks in the positions of the mapped white pixels to automatically redraw the image.
             These drawings can then be saved and reused by storing the corresponding text files.
Credits: Some of the below code was sourceed from the following -
         https://www.codementor.io/isaib.cicourel/image-manipulation-in-python-du1089j1u
"""

import os
import sys
import re
import time
import tkinter as tk
import webbrowser
import random
import requests
import contextlib
import shutil
from google_images_download import google_images_download
from PIL import Image, ImageFilter
from colorama import Fore, Style
from pynput.mouse import Button, Controller
from tkinter import filedialog
from tqdm import tqdm

mouse = Controller()
root = tk.Tk()
# root.deiconify()
root.withdraw()


def main():
    menu()


def menu():
    print('\nWelcome!\n')
    print(Fore.LIGHTCYAN_EX + '-------------')
    print('1) Load an existing drawing')
    print('2) Open an new image and start drawing')
    print('3) Play the guessing game')
    print('-------------' + Style.RESET_ALL)
    option = int(input('\nPlease enter an option: '))
    print(option)

    if option == 1:
        drawings = show_drawings()
        input_file = input(Fore.LIGHTWHITE_EX + '\nPlease enter the drawing you would like to open (without .txt): ')
        if input_file + '.txt' not in drawings:
            print('\nError! File not found.')
            menu()
        else:
            draw('drawings/%s.txt' % input_file)

    elif option == 2:
        opened_image = open_image()
        black_image = convert_black(opened_image)
        final_image = find_edges(black_image)
        get_coordinates(final_image)
        draw('coordinates.txt')
        save()

    elif option == 3:
        play_game()

    else:
        print('\nPlease enter a valid option...\n')
        menu()


def show_drawings():
    files = []
    print('\nSaved Drawings: \n')
    for file in os.listdir("drawings"):
        if file.endswith(".txt"):
            print(Fore.LIGHTMAGENTA_EX, '--> ' + file)
            files.append(file)
    return files


def open_image():
    print('\nChoose an image!')
    root.lift()
    file_path = filedialog.askopenfilename(
        initialdir='/', title='Select Image',
        filetypes=[('Image', '*.jpeg *.jpg *.png')]
    )
    root.update()
    if file_path == '':
        print('\nNo file selected!\n')
        menu()
    else:
        time.sleep(2)  # wait until tkinter window closes
        image = Image.open(file_path)
        return image


def convert_black(image_file_path):
    pallet_image = image_file_path.convert('RGBA')
    edges = pallet_image.filter(ImageFilter.FIND_EDGES)
    black_image = edges.convert('1')  # convert image to black and white
    # final_image = black_image.filter(ImageFilter.SMOOTH)
    return black_image


def find_edges(image):
    col = image
    gray = col.convert('L')
    bw = gray.point(lambda x: 0 if x < 128 else 255, '1')
    width, height = bw.size
    cropped_image = bw.crop((5, 5, width - 5, height - 5))  # Crop white border out of image

    if width and height > 700:
        print('Image too large, resizing by half...')
        resize_factor = width / 700
        resize = cropped_image.resize((int(width / resize_factor), int(height / resize_factor)))
        print('New image size: ', (int(width / resize_factor), int(height / resize_factor)))
        # resize.save('converted_image.png')
        return resize

    else:
        # cropped_example.save('converted_image.png')
        return cropped_image


def get_pixel(image, i, j):
    width, height = image.size
    if i > width or j > height:
        return None  # if out of bounds
    pixel = image.getpixel((i, j))
    return pixel


def get_coordinates(image):
    width, height = image.size
    for i in range(width):
        for j in range(height):
            pixel = get_pixel(image, i, j)
            if pixel == 255:
                coordinates = [i, j]
                f = open('coordinates.txt', 'a')
                f.write("%s\n" % coordinates)
                f.close()


def draw(coordinates):
    print(Fore.LIGHTGREEN_EX + '\nDrawing will start 10 in seconds, use this time to select your brush/color!\n' +
          Style.RESET_ALL)
    time.sleep(1)
    webbrowser.open('http://kleki.com/')
    time.sleep(10)  # allow for time to select brush size/color
    mouse.click(Button.left)
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    time.sleep(0.5)

    num_lines = sum(1 for line in open(coordinates, 'r'))
    with open(coordinates, "r") as f:
        for line in tqdm(f, total=num_lines):
            x = int(re.findall(r'\d+', line)[0]) + (screen_width / 4)
            y = int(re.findall(r'\d+', line)[1]) + (screen_height / 4)
            mouse.position = (x, y)
            time.sleep(0.0029)  # slow down mouse clicks so they can register on screen
            mouse.click(Button.left)
    time.sleep(2)
    print(Fore.LIGHTGREEN_EX, 'Finished...')


def save():
    save_file = input(Fore.LIGHTYELLOW_EX + '\nDo you want to save this drawing? (Y/N): ' + Style.RESET_ALL).upper()
    if save_file == 'Y':
        file_name = input('Enter a file name (without .txt): ') + '.txt'
        try:
            os.rename('coordinates.txt', 'drawings/%s' % file_name)
        except OSError:
            print(OSError)
            os.remove('coordinates.txt')
    else:
        os.remove('coordinates.txt')


def get_hint(noun, image_2_path):
    image2 = Image.open('downloads/%s/%s' % (noun, image_2_path))
    black_image = convert_black(image2)
    final_image = find_edges(black_image)
    get_coordinates(final_image)
    draw('coordinates.txt')

    os.remove('coordinates.txt')
    shutil.rmtree('downloads')


def play_game():
    print(Fore.LIGHTCYAN_EX + '\n-------------')
    print('To play, guess the drawing! You have one hint, press "h" for your hint')
    print('-------------\n' + Style.RESET_ALL)

    lives = 3
    hints = 1

    nouns = requests.get("http://www.desiquintans.com/downloads/nounlist/nounlist.txt").text
    noun_list = list(nouns.split("\n"))

    random_noun = noun_list[random.randint(0, len(noun_list) - 1)]

    response = google_images_download.googleimagesdownload()
    arguments = {"keywords": random_noun, "limit": 2, "size": "medium"}

    with contextlib.redirect_stdout(None):  # disable logging so the noun isn't printed!
        response.download(arguments)

    sys.stdout = sys.__stdout__  # re-enable logging

    arr = os.listdir('downloads/%s' % random_noun)
    image_1_path = arr[0]
    image_2_path = arr[1]

    image1 = Image.open('downloads/%s/%s' % (random_noun, image_1_path))
    black_image = convert_black(image1)
    final_image = find_edges(black_image)
    get_coordinates(final_image)
    draw('coordinates.txt')

    os.remove('coordinates.txt')

    while lives is not 0:

        print(Fore.MAGENTA + 'Lives left: %d\n' % lives)
        option = input(Fore.LIGHTYELLOW_EX + '\nWhat do you think this drawing is? ' + Style.RESET_ALL).lower()

        if option == random_noun:
            print(Fore.GREEN + 'YOU WIN!')
            time.sleep(2)
            sys.exit(0)
        elif option == 'h' and hints == 1:
            print('\nDrawing second image...\n')
            get_hint(random_noun, image_2_path)
            hints -= 1
        else:
            lives -= 1

    print(Fore.RED + '\n0 LIVES LEFT - GAME OVER!')
    print('CORRECT ANSWER: %s' % random_noun)

    try:
        shutil.rmtree('downloads')
    except OSError:
        pass

    sys.exit()


if __name__ == "__main__":
    main()
