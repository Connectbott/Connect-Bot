# =============================================================================
# RECEIVES AN IMAGE OF THE BOARD (BGR) AND RETURNS THE NUMBER OF THE COLUMN
# BELONGING TO THAT WHICH CONTAINS THE PLAYER's MOVE.
# ->Player's move is detected comparing the current game state to the previous'
#
# =============================================================================
import cv2
import numpy as np
from matplotlib import pyplot as plt
import subprocess
import time
import calibrate as c

global col_start
global col_width

def crop_column(board, n):
    col_start = 0
    col_width = 85
    x1 = col_start + col_width * n
    x2 = x1 + col_width
    return board[:, x1:x2, :].copy()


def get_yellow_count(img):
    mask = c.segment_yellow(img)
    ret, labels = cv2.connectedComponents(mask)
    n_yellow_bodies = ret - 1
    return mask, n_yellow_bodies


def get_played_column(previous_game_state, count=0):
    array_game_state = np.asarray(previous_game_state) * (-1)
    array_game_state = array_game_state.clip(min=0) 
    
    subprocess.call("./snap_gameState.sh", shell=True)
    board_BGR = cv2.imread("img/gameState.jpg")
    board_BGR = c.homography(board_BGR) 

# ============================================================================= 
#    plt.title('Homografia actual')
#    plt.imshow(cv2.cvtColor(board_BGR, cv2.COLOR_BGR2RGB))
#    plt.show()
    
#    plt.title('binarized')
#    plt.imshow(c.segment_yellow(board_BGR), 'gray')
#    plt.show()
# =============================================================================
    
    column_counts = array_game_state.sum(axis=0)
    played_columns = []
    for i in range(7):
        actual_column = crop_column(board_BGR, i)
# =============================================================================
#         plt.imshow(actual_column)
#         plt.show()
# =============================================================================
        _, actual_column_count = get_yellow_count(actual_column)
# =============================================================================
#         plt.title(str(i))
#         plt.imshow(_, 'gray')
#         plt.show()
# =============================================================================
        previous_column_count = column_counts[i]
#        print("count for column ", i, " is ", actual_column_count, ", was ", previous_column_count)
        
        if actual_column_count == previous_column_count + 1:
            played_columns.append(i+1)

    if len(played_columns) == 1:
        print("Human has played column ", played_columns[0])
        return played_columns[0]
    elif count < 5:
        print("Error detecting move, retaking picture...")
        return get_played_column(previous_game_state, count+1)
    else:
        raise Exception('Maximum attempts when checking column played')
        
        





    
    

