from matplotlib import pyplot as plt
import numpy as np
import imutils
import cv2
import subprocess
import calib as c

global img
global mean_hsv
global matrix

def start_calib():
    global img
    global mean_hsv
    global matrix
    img = cv2.imread("img/calibrate.jpg")
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    
    # =============================================================================
    # right = 0
    # up = 120
    # 
    # 
    # topLeft_col = 580 + right
    # topLeft_row = 370 - up
    # 
    # topRight_col = 2960 + right
    # topRight_row = 340 - up
    # 
    # bottomLeft_col = 490 + right
    # bottomLeft_row = 2280 - up
    # 
    # bottomRight_col = 3100 + right
    # bottomRight_row = 2220 - up
    # =============================================================================
    
    topLeft_col = 426
    topLeft_row = 122
    
    topRight_col = 2880
    topRight_row = 100
    
    bottomLeft_col = 252 
    bottomLeft_row = 2100
    
    bottomRight_col = 3080 
    bottomRight_row = 2120
    
    
    # =============================================================================
    # #TOP LEFT
    #cv2.circle(imgRGB, (topLeft_col,topLeft_row), 20, (255,0,0), -1)
    # #TOP RIGHT
    #cv2.circle(imgRGB, (topRight_col,topRight_row), 20, (255,0,0), -1)
    # #BOTTOM LEFT
    #cv2.circle(imgRGB, (bottomLeft_col,bottomLeft_row), 20, (255,0,0), -1)
    # #BOTTOM RIGHT
    #cv2.circle(imgRGB, (bottomRight_col,bottomRight_row), 20, (255,0,0), -1)
    # 
    #plt.imshow(imgRGB)
    #plt.show()
    # =============================================================================
    
    
    pts1 = np.float32([[topLeft_col,topLeft_row], [topRight_col,topRight_row], 
                       [bottomLeft_col,bottomLeft_row], [bottomRight_col,bottomRight_row]])
    pts2 = np.float32([[0,0], [600,0], [0,400], [600,400]])
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    
    
    global yellow_hsv
    boardRGB = homography(imgRGB)
    
    yellow  = boardRGB[360:375, 40:55, :]
    yellow_hsv = cv2.cvtColor(yellow, cv2.COLOR_RGB2HSV)
    mean_h = np.mean(yellow_hsv[:,:,0])
    mean_s = np.mean(yellow_hsv[:,:,1])
    mean_v = np.mean(yellow_hsv[:,:,2])
    yellow_hsv = np.dstack((mean_h, mean_s, mean_v)).astype(np.uint8)

def snap_calibrate():
    subprocess.call("./snap_calibrate.sh", shell=True)


def homography(image):
    global matrix
    return cv2.warpPerspective(image, matrix, (600,400))





def segment_yellow(col_BGR):
    '''
    :param img_BGR: numpy array. 
    :return:
    '''
    global yellow_hsv
    img_hsv = cv2.cvtColor(col_BGR, cv2.COLOR_BGR2HSV)

    # mask for yellow chips
    #yellow_mask = cv2.inRange(img_hsv, (20, 0, 0), (30, 255, 255))
    lower = np.array([yellow_hsv[0][0][0]-10, 200, 200])
    upper = np.array([yellow_hsv[0][0][0]+10, 255, 255])
    yellow_mask = cv2.inRange(img_hsv, lower, upper)
    croped = cv2.bitwise_and(col_BGR, col_BGR, mask=yellow_mask)

    # Binarization
    gray = croped[:, :, 0]
    binary = (gray > 0) * 255
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY)
# =============================================================================
#     plt.imshow(binary, 'gray')
#     plt.show()
# =============================================================================
    
    # Noise removal
    #opened = cv2.morphologyEx(binary, cv2.MORPH_OPEN, np.ones((1, 1)))

    # Morphology
    dilation = cv2.dilate(binary, np.ones((10, 10)), iterations=1)

    erosion = cv2.erode(dilation, np.ones((5, 5)), iterations=1)

    #final = cv2.blur(dilation,(15,15))
    final = erosion
# =============================================================================
#     plt.imshow(final, 'gray')
#     plt.show()
# =============================================================================
    return final



# =============================================================================
# MEANT TO RETURN ONLY COL START AND COL WIDTH
# =============================================================================
def get_column_measures():
    # =============================================================================
    # img: image of board containing ONLY 2 red chips placed in 1st and 7th col 
    # =============================================================================
    # =============================================================================
    # Segment out the yellow chips
    # =============================================================================
    global img
    global mean_hsv
    
    board = homography(img)
    boardRGB = cv2.cvtColor(board, cv2.COLOR_BGR2RGB)
    
    #cv2.circle(boardRGB, (50,370), 5, (255,0,0), -1)
    #cv2.circle(boardRGB, (550,375), 5, (255,0,0), -1)

    
    thresh = segment_yellow(board)
    
    
    # =============================================================================
    # keep contour of binary shapes
    # =============================================================================
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    
    
    # =============================================================================
    # Compute center of contours
    # =============================================================================
    centers_XY = []    
    for c in cnts:
        M = cv2.moments(c)
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        centers_XY.append([cX,cY])
        cv2.circle(boardRGB, (cX, cY), 6, (255, 0, 0), -1)
        
    #cv2.line(boardRGB, (centers_XY[0][0], centers_XY[0][1]), (centers_XY[1][0], centers_XY[1][1]),(0,255,0), 3)
    #plt.imshow(boardRGB)
    #plt.show()
    
    #col,fil
    x1, y1 = centers_XY[0]
    x2, y2 = centers_XY[1]
    distance =  np.sqrt((x1 - x2)**2 + (y1 - y2)**2)
    
    # dist entre 2 cols == diametro ficha
    # ancho de columna = distancia entre 2 columnas / num de columnas entre estas 2
    width_col = int(distance/6)
    radius = int(width_col/2)
    
    
    col_inici = max(x2 - radius, 0)
    
    #print("col_start: ", col_inici)
    #print("col_width: ", width_col)



    return col_inici, width_col


