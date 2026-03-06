#=- Kawediloru || 6 March 2026 -=#
'''
PyGame Autoplayer
plays videos back to back using pygame n stuff
make sure u get dependencies under #libraries
sometimes it desyncs but whatever
'''

###############
# CUSTOMIZATION
###############

VOLUME:int = 100 # as a percentage

FULLSCREEN = True # whether or not to have the pygame window fullscreened
SCALE = 1 # scale of the videos in relation to the screen. and also how big non fullscreen window is



###########
# LIBRARIES
###########

import numpy as np, os, pyautogui, pygame, sys
from moviepy.editor import VideoFileClip, vfx # moviepy==1.0.3
from random import choice
from threading import Thread
from time import sleep



###########
# CONSTANTS
###########

VIDEOS_FOLDER:str = "vids"
VIDEOS_TEXTFILE:str = "vids.txt"

WIDTH, HEIGHT = pyautogui.size()
FQUEUE_SIZE = 100
CQUEUE_SIZE = 5

MAX_ITER = 2147483648
SLEEP_LEN = 0.2



###########
# FUNCTIONS
###########

def stop(): #VOID
    '''
    Function to stop the program properly.
    '''
    pygame.quit()
    os.remove("cur.wav")
    raise SystemExit("Stopping...")



def gather_videos(): #LIST
    '''
    Function to get all filenames from the appropriate textfile.
    '''
    with open(VIDEOS_TEXTFILE, 'r', encoding="utf-8") as f:
        return f.readlines()



def add_filename_to_queue(l:list): #VOID
    '''
    Function to add a random filename to a queue of them.
    '''
    name:str = choice(l)
    fileQueue.append(name.rstrip('\n'))



def filename_to_video_object(n:str): #OBJECT: VideoFileClip
    '''
    Function that creates a clip object from
    the filename so it can play when loaded.
    '''
    try:
        clip = VideoFileClip(f"{VIDEOS_FOLDER}/{n}", target_resolution=(HEIGHT * SCALE, None)).rotate(90).fx(vfx.mirror_y).volumex(VOLUME/100)
        return clip
    
    except OSError as e:
        print(f"{e}; Bad File in List Ignored.")
        return None



def cache_video(name:str): #VOID
    '''
    Function to cache video objects into a small queue of a few videos
    '''
    clip = filename_to_video_object(name)
    if (clip): clipQueue.append(clip)
    


def manage_queues(): #VOID
    '''
    Function to manage the file and clip queues
    Kinda just like fills them when necessary
    '''
    i:int = 0
    while (i < MAX_ITER):
        if (len(fileQueue) < FQUEUE_SIZE):
            try: add_filename_to_queue(filenames)
            except Exception as e: f"Passing with error {e}"
        
        if (len(clipQueue) < CQUEUE_SIZE):
            try: cache_video(fileQueue.pop(0))
            except Exception as e: f"Passing with error {e}"
        
        i += 1
        sleep(SLEEP_LEN)



def stop_video(clip): #VOID
    pygame.mixer.music.stop()
    pygame.mixer.music.unload()
    clip.close()



def play_audio(clip): #VOID
    '''
    Function to play the audio of a clip when called (through play_video)
    Creates a temporary audio file to play the sound from cuz it's easy that way
    '''
    clip.audio.write_audiofile("cur.wav", fps=44100, verbose=False, logger=None)
    pygame.mixer.music.load("cur.wav")
    pygame.mixer.music.play()



def play_video(clip): #VOID
    '''
    Function that actively plays a video to the screen.
    '''
    
    # if there's audio, play it
    if clip.audio:
        try: play_audio(clip)
        except Exception as e: print(f"Current audio failed to load: {e}")
    
    try:
        for frame in clip.iter_frames(fps=clip.fps, dtype="uint8"):
            # check for events (also to tick pygame)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    stop_video(clip)
                    stop()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        stop_video(clip)
                        return
            
            # draw it properly
            frameSurface = pygame.surfarray.make_surface(frame)
            clipRect = frameSurface.get_rect(center=((WIDTH * SCALE) // 2, (HEIGHT * SCALE) // 2))
            screen.fill((0, 0, 0))
            screen.blit(frameSurface, clipRect)
            pygame.display.update()
            
            CLOCK.tick(clip.fps)
    
    except OSError as e: f"Current video failed to load: {e}"
    
    stop_video(clip)



def manage_videos(): #VOID
    '''
    Function to manage the playing of videos in generallll ig
    Basically waits for a video to enter the queue before playing
    '''
    i:int = 0
    while (i < MAX_ITER):
        while (len(clipQueue) == 0):
            sleep(SLEEP_LEN)
        
        play_video(clipQueue.pop(0))
        
        i += 1



######
# MAIN
######

pygame.init()
CLOCK = pygame.time.Clock()

if FULLSCREEN: screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
else: screen = pygame.display.set_mode((WIDTH * SCALE, HEIGHT * SCALE))

try: filenames:list = gather_videos()
except: raise SystemExit("Error: failed to get filenames. Run update_txtfile.py first!")

fileQueue:list = []
clipQueue:list = []

thrQueueManagement = Thread(target=manage_queues, daemon=True)
thrQueueManagement.start()

manage_videos()