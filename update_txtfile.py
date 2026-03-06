#=- Kawediloru || 6 March 2026 -=#
'''
PyGame Autoplayer - update_txtfile.py
puts all video file names into a text file so it can be retrieved more easily
'''

###########
# LIBRARIES
###########

import os



###########
# CONSTANTS
###########

VIDEOS_FOLDER:str = "vids"
VIDEOS_TEXTFILE:str = "vids.txt"

FILE_EXTENTIONS:list = ['.mp4', '.avi', '.mov', '.mpeg', '.mpg',
                       '.ogv', '.webm', '.mkv', '.flv', '.mts',
                       '.m2ts', '.ts', '.3gp', '.m4v', '.gif']



###########
# FUNCTIONS
###########

def create_text_file(): #VOID
    '''
    Function to creates a text file with
    every video file in VIDEOS_FOLDER
    '''
    with open(VIDEOS_TEXTFILE, 'w', encoding="utf-8") as f:
        l = [f for f in os.listdir(VIDEOS_FOLDER) if any(extension in f for extension in FILE_EXTENTIONS)]
        f.write('\n'.join(l))



######
# MAIN
######

create_text_file()
print("Text file finished!")