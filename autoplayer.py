# --- SCRIPT BY KAWEDILORU --- #
'''
This script will randomly play videos back to back in a window.
INSTRUCTIONS:
    - Put all video files into a folder inside that one called "vids"
    - Install all libraries, with specific versions for moviepy==1.0.3 and pillow==9.5.0
    - Adjust the values in CONSTANTS tab to fit your desires (don't be stupid)
        - If the videos are laggy, reduce the MAX_FPS and RESOLUTION.
'''

###########
# LIBRARIES
###########
from moviepy.editor import VideoFileClip
import numpy as np
import os
import pyautogui
import pygame
from random import choice
import sys
from threading import Thread
from time import sleep



###########
# CONSTANTS
###########s
TOTAL_VIDEOS = -1 # How many videos to play before terminating the program; set to -1 for infinite videos
PLAY_LENGTH = -1 # How long to play each video; set to -1 to have native video lengths
MINIMUM_PLAYBACK = 1 # Seconds minimum to keep videos on screen for
VOLUME_PCT = 100 # Percent volume to play the videos' audios at
MAX_FPS = 24 # Maximum FPS per video; heavily affects performance
RESOLUTION = 240 # Pixels to display videos at
FULLSCREEN = True # Whether fullscreen mode is enabled
SCALE = 1 if FULLSCREEN else 0.5 # ONLY CHANGE LAST NUMBER - Proportion of screen dimensions to take up when windowed
PREPARE_TIME = 1 # Seconds to wait before starting the videos
MAX_QUEUE_LENGTH = 100 # Queue size to stop at so memory isn't busted
UPDATE_VIDS = True # Whether to automatically update the video names text file
# dont touch these vv
VIDEO_FOLDER = 'vids' # Path to all video files
NAMES_TEXT_FILE = 'vids.txt' # Local file with names of every video in that directory ^
WIDTH, HEIGHT = pyautogui.size()
WIDTH *= SCALE; HEIGHT *= SCALE



#########
# CLASSES
#########
class Queue:
    # CONSTRUCTOR
    def __init__(self):
        self._q = list()
    # GETTERS/SETTERS
    @property
    def q(self):
        return self._q
    @q.setter
    def q(self, n):
        self._q = n
    # METHODS
    'Add something to the queue.'
    def add(self, item):
        self.q.append(item)
    
    'Pop something from the queue.'
    def pop(self):
        try: return self.q.pop(0)
        except IndexError: return None
    
    'For debugging.'
    def __str__(self):
        return f'{self.q}'



#############
# SUBROUTINES
#############
'Load videos into the queue to be played.'
def load_videos():
    r = float('inf') if TOTAL_VIDEOS == -1 else TOTAL_VIDEOS
    while r > 0:
        # buffer if at max length
        while len(clipQueue.q) > MAX_QUEUE_LENGTH:
            sleep(1)
        # get the file and load the clip
        try:
            file = choice(allVids).rstrip('\n')
            clip = VideoFileClip(f'{VIDEO_FOLDER}/{file}').volumex(VOLUME_PCT/100).resize(height=RESOLUTION)
            if int(clip.duration) < MINIMUM_PLAYBACK: clip.loop(duration=MINIMUM_PLAYBACK)
            if PLAY_LENGTH != -1: clipQueue.add([file, clip.loop(duration=PLAY_LENGTH)])
            else: clipQueue.add([file, clip])
        except OSError: print('Corrupted file ignored.')
        r -= 1
    return

'Stops the current clip.'
def stop_clip(clip):
    pygame.mixer.music.stop()
    pygame.mixer.music.unload()
    clip.close()

'Convert MoviePY audio to pygame sound by saving a file.'
def play_clip_audio(clip):
    clip.audio.write_audiofile('temp.wav', fps=44100, verbose=False, logger=None)
    pygame.mixer.music.load('temp.wav')
    pygame.mixer.music.play()

'Play a clip when called.'
def play_individual_clip(c):
    # transform
    clip = c.resize(height=HEIGHT).rotate(90).set_fps(min(c.fps, MAX_FPS))
    # play audio if it exists
    if clip.audio:
        try: play_clip_audio(clip)
        except Exception as e: print(f'Current audio failed to load: {e}')
    # render video
    try:
        for frame in clip.iter_frames(fps=clip.fps, dtype='uint8'):
            # check event each frame so it dont freeze
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    clip.close()
                    pygame.quit()
                    os.remove('temp.wav')
                    sys.exit()
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_RETURN:
                        stop_clip(clip)
                        return
            
            # convert moviepy to pygame format
            frameSurface = pygame.surfarray.make_surface(frame)
            frameSurface = pygame.transform.flip(frameSurface, True, False)
            videoRect = frameSurface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            # draw
            screen.fill((0, 0, 0))
            screen.blit(frameSurface, videoRect)
            pygame.display.update()
            # fps
            CLOCK.tick(clip.fps)
    
    except OSError:
        # load frame properly
        frame = clip.get_frame(0)
        frameSurface = pygame.surfarray.make_surface(np.rot90(frame))
        frameSurface = pygame.transform.flip(frameSurface, True, False)
        videoRect = frameSurface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        
        screen.fill((0, 0, 0))
        screen.blit(frameSurface, videoRect)
        pygame.display.update()
        # hold the frame for the proper time
        try: sleep(PLAY_LENGTH)
        except ValueError: sleep(MINIMUM_PLAYBACK)
    # stop
    stop_clip(clip)
    return

'Run the videos from the queue.'
def play_videos():
    r = float('inf') if TOTAL_VIDEOS == -1 else TOTAL_VIDEOS
    while r > 0:
        # buffer if queue empty
        while len(clipQueue.q) == 0:
            sleep(0.5)
        # get next clip in q and play it
        clip = clipQueue.pop()
        print(f'Playing: {clip[0]}')
        play_individual_clip(clip[1])
        r -= 1
    return

'Give any obvious error messages.'
def check_for_dumbassery():
    if not (PLAY_LENGTH == -1 or PLAY_LENGTH > 0):
        print('Play length is invalid/too short.')
        exit()
    elif (PLAY_LENGTH != -1) and (PLAY_LENGTH < MINIMUM_PLAYBACK):
        print('Play length must be longer than minimum playback.')
        exit()

'Create textfile in case it doesnt exist'
def create_text_file():
    with open(NAMES_TEXT_FILE, 'w', encoding='utf-8') as f:
        l = [f for f in os.listdir(VIDEO_FOLDER) if any(ext in f for ext in ['.mp4', '.avi', '.mov', '.mpeg', '.mpg', '.ogv', '.webm', '.mkv', '.flv', '.mts', '.m2ts', '.ts', '.3gp', '.m4v', '.gif'])]
        f.write('\n'.join(l))
        print('Created video names text file.')

'Get and store the file names of all files.'
def get_filenames():
    with open(NAMES_TEXT_FILE, 'r', encoding='utf-8') as f:
        print('File Loaded.')
        return f.readlines()



##############
# MAIN PROGRAM
##############
# check params
check_for_dumbassery()

# get all filenames
if UPDATE_VIDS: create_text_file()
try: allVids = get_filenames()
except FileNotFoundError:
    print('Please enable the UPDATE_VIDS variable to create the text file of video file names.')
    exit()
print('Directories Loaded into Memory.')

# initiate and thread queue
clipQueue = Queue()
threadLoadVids = Thread(target=load_videos, daemon=True)
threadLoadVids.start()

# give it a sec
print('Preparing Queue.')
sleep(PREPARE_TIME)

# setup pygame to work
pygame.init()
if FULLSCREEN: screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
else: screen = pygame.display.set_mode((WIDTH, HEIGHT))
CLOCK = pygame.time.Clock()

# play dem
play_videos()

# stop
pygame.quit()
os.remove('temp.wav')
