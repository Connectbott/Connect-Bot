import RPi.GPIO as GPIO
import I2C_LCD_driver
import random
import boardMorphology as bm
import calibrate as c

from colorzero import Color
from gpiozero import AngularServo, LED, Button, RGBLED
from time import sleep
from time import *

global EASY 
global MEDIUM
global HARD

EASY = 1
MEDIUM = 3
HARD = 4


global FINISH_SELECTION
global LEVEL
global LEVEL_PRESSED

FINISH_SELECTION = False
LEVEL = 1
LEVEL_PRESSED = False


# =============================================================================
# CALIBRACION DE LA CAMARA
# =============================================================================

def calibrate(finish_button, lcd):
    ready2calibrate(finish_button, lcd)
    c.snap_calibrate()
    c.start_calib()
    emptyBoard(finish_button, lcd)
    
def ready2calibrate(finish_button, lcd):
    global FINISH_SELECTION
    
    mssg_ready2calibrate(lcd)
    
    while not FINISH_SELECTION:
        finish_button.when_pressed = pressButtonFinish
    
    FINISH_SELECTION = False
    

# =============================================================================
# DETECCION DE LA COLUMNA JUGADA
# =============================================================================

def get_playedColumn(gameState):
    return int(bm.get_played_column(gameState))


# =============================================================================
# TIRAR FICHA
# =============================================================================

def throwChip():
    servo_pin = 14
    servo = AngularServo(servo_pin,initial_angle=-90,min_angle=90,max_angle=-90,min_pulse_width=0.75/1000, max_pulse_width=2.25/1000,frame_width=20/1000)   
    sleep(1)
    servo.angle = 90
    sleep(1)
    servo.detach()
    servo.close()


# =============================================================================
# MOVER CARRITO
# =============================================================================
def limitSwitchOn():
    limit_button_pin = 22
    limit_button = Button(limit_button_pin)
    return limit_button.is_pressed

def go2Columns(columns,lcd):
    columns.sort(reverse=True)

    home_cm = 6.4
    column_cm = 3.5
    
    delay = .0208 / 150
    
    DIR = 17  # Direction GPIO Pin
    STEP = 27 # Step GPIO Pin
    CW = 1     # Clockwise Rotation
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(DIR, GPIO.OUT)
    GPIO.setup(STEP, GPIO.OUT)
    GPIO.output(DIR, CW)
    
    MODE = (5, 6, 13)   # Microstep Resolution GPIO Pins
    GPIO.setup(MODE, GPIO.OUT)
    RESOLUTION = {'1/8': (1, 1, 0)}
    GPIO.output(MODE, RESOLUTION['1/8'])
    
    
#    Movemos al home
    l = home_cm
    v= l*50
    step_count = round(v)*8
    
    for x in range(step_count):
        GPIO.output(STEP, GPIO.HIGH)
        sleep(delay)
        GPIO.output(STEP, GPIO.LOW)
        sleep(delay)
    
#   Movemos a la primera columna
    l = column_cm * columns[0]
    v= l*50
    step_count = round(v)*8
    
    for x in range(step_count):
        GPIO.output(STEP, GPIO.HIGH)
        sleep(delay)
        GPIO.output(STEP, GPIO.LOW)
        sleep(delay)
    
    
#    Tiramos la ficha
    throwChip()
#
    mssg_cheating(lcd)
    CW = 0
    GPIO.output(DIR, CW)
    
#   Vamos a la otra columna
    columns_back = columns[0]-columns[1]
    l = column_cm * columns_back
    v= l*50
    step_count = round(v)*8
    
    for x in range(step_count):
        GPIO.output(STEP, GPIO.HIGH)
        sleep(delay)
        GPIO.output(STEP, GPIO.LOW)
        sleep(delay)
    
    throwChip()
    
    #   Regresamos a la primera columna
    columns2home = columns[0] - columns_back
    l = column_cm * columns2home
    v= l*50
    step_count = round(v)*8
    
    for x in range(step_count):
        GPIO.output(STEP, GPIO.HIGH)
        sleep(delay)
        GPIO.output(STEP, GPIO.LOW)
        sleep(delay)
    
#    Regresamos al home
    l = home_cm
    v= l*50
    step_count = round(v)*8
    
    for x in range(step_count):
        GPIO.output(STEP, GPIO.HIGH)
        sleep(delay)
        GPIO.output(STEP, GPIO.LOW)
        sleep(delay)

def go2Column(column):
    home_cm = 6.4
    column_cm = 3.5
    
    delay = .0208 / 150
    
    DIR = 17  # Direction GPIO Pin
    STEP = 27 # Step GPIO Pin
    CW = 1     # Clockwise Rotation
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(DIR, GPIO.OUT)
    GPIO.setup(STEP, GPIO.OUT)
    GPIO.output(DIR, CW)
    
    MODE = (5, 6, 13)   # Microstep Resolution GPIO Pins
    GPIO.setup(MODE, GPIO.OUT)
    RESOLUTION = {'1/8': (1, 1, 0)}
    GPIO.output(MODE, RESOLUTION['1/8'])
    
    
#    Movemos al home
    l = home_cm
    v= l*50
    step_count = round(v)*8
    
    for x in range(step_count):
        GPIO.output(STEP, GPIO.HIGH)
        sleep(delay)
        GPIO.output(STEP, GPIO.LOW)
        sleep(delay)
    
#   Movemos a la columna
    l = column_cm * column
    v= l*50
    step_count = round(v)*8
    
    for x in range(step_count):
        GPIO.output(STEP, GPIO.HIGH)
        sleep(delay)
        GPIO.output(STEP, GPIO.LOW)
        sleep(delay)
    
    
#    Tiramos la ficha
    throwChip()
#
    CW = 0
    GPIO.output(DIR, CW)
    
#   Regresamos a la primera columna
    l = column_cm * column
    v= l*50
    step_count = round(v)*8
    
    for x in range(step_count):
        GPIO.output(STEP, GPIO.HIGH)
        sleep(delay)
        GPIO.output(STEP, GPIO.LOW)
        sleep(delay)
        
#    Regresamos al home
    l = home_cm
    v= l*50
    step_count = round(v)*8
    
    for x in range(step_count):
        GPIO.output(STEP, GPIO.HIGH)
        sleep(delay)
        GPIO.output(STEP, GPIO.LOW)
        sleep(delay)

     
# =============================================================================
# ESCOGER DIFICULTAD 
# =============================================================================

def declare_buttons():
    level_button_pin = 26
    finish_button_pin = 19
    level_button = Button(level_button_pin)
    finish_button = Button(finish_button_pin) 
    return level_button, finish_button


def close_buttons(level_button, finish_button):
    global FINISH_SELECTION
    FINISH_SELECTION = False
    level_button.close()
    finish_button.close()


def setLevel(level_button, finish_button, level_led, lcd):
    global FINISH_SELECTION
    global LEVEL
    global LEVEL_PRESSED
    while not FINISH_SELECTION:
        
        level_button.when_pressed = pressButtonLevel
        
        if LEVEL_PRESSED == True:
            levelUp()
            changeLevel(level_led)
            mssg_level(lcd)
            LEVEL_PRESSED = False
            
        finish_button.when_pressed = pressButtonFinish
            
    FINISH_SELECTION = False


def pressButtonFinish():
    global FINISH_SELECTION
    FINISH_SELECTION = True


def pressButtonLevel():
    global LEVEL_PRESSED
    LEVEL_PRESSED = True

def levelUp():
    global LEVEL
    global EASY 
    global MEDIUM
    global HARD
    if LEVEL == HARD:
        LEVEL = EASY
    elif LEVEL == EASY:
        LEVEL = MEDIUM
    elif LEVEL == MEDIUM:
        LEVEL = HARD

def chooseLevel(level_button, finish_button, level_led, lcd):
    global LEVEL
    LEVEL = EASY
    mssg_level(lcd)
    setLevel(level_button, finish_button, level_led, lcd)
    return LEVEL

    
#==============================================================================
# LED DIFICULTAD
#==============================================================================

def declare_level_led():
    r_pin = 16
    g_pin = 20
    b_pin = 21
    level_led = RGBLED(r_pin, g_pin, b_pin)
    level_led.color = Color('green')
    return level_led


def changeLevel(level_led):
    global LEVEL
    if LEVEL == EASY:
        level_led.color = Color('green')
    elif LEVEL == MEDIUM:
        level_led.color = Color('orange')
    elif LEVEL == HARD:
        level_led.color = Color('red')
    
    
def close_level_led(level_led):
    level_led.close()
  

# =============================================================================
# BOTON PASAR TURNO
# =============================================================================

def wait_pass_turn(finish_button):
    global FINISH_SELECTION
    FINISH_SELECTION = False

    while not FINISH_SELECTION:
        finish_button.when_pressed = pressButtonFinish
            
    FINISH_SELECTION = False


# =============================================================================
# LED TURNO
# =============================================================================

def declare_turn_led():
    turn_led_pin = 12
    turn_led = LED(turn_led_pin)
    turn_led.on()             
    return turn_led


def changeTurn(turn_led):
    turn_led.toggle()
    
    
def close_turn_led(turn_led):
    turn_led.close()

# ==============================================================================
# LCD
# ==============================================================================

def mssg_level(lcd):
    global LEVEL
    lcd.lcd_clear()
    if LEVEL == EASY:
        lcd.lcd_display_string("ESCOGE EL NIVEL:", 1)
        lcd.lcd_display_string("FACIL", 2)
    elif LEVEL == MEDIUM:
        lcd.lcd_display_string("ESCOGE EL NIVEL:", 1)
        lcd.lcd_display_string("MEDIO", 2)
    elif LEVEL == HARD:
        lcd.lcd_display_string("ESCOGE EL NIVEL:", 1)
        lcd.lcd_display_string("DIFICIL", 2)
        

def mssg_again(lcd, play_again):
    lcd.lcd_clear()
    lcd.lcd_display_string("LA REVANCHA??", 1)
    if play_again:
        lcd.lcd_display_string("SI", 2)
    else:
        lcd.lcd_display_string("NO", 2)
    

def mssg_humanTurn(lcd):
    lcd.lcd_clear()
    num = random.randint(1,5)
    if num == 1:
        lcd.lcd_display_string("PUEDES JUGAR", 1)
        lcd.lcd_display_string("ENSERIO", 2)
    elif num == 2:
        lcd.lcd_display_string("QUE LENTO ERES", 1)
        lcd.lcd_display_string("TIRA YA PESADO", 2)
    elif num == 3:
        lcd.lcd_display_string("NO TE PONGAS", 1)
        lcd.lcd_display_string("NERVIOSO CRACK", 2)
    elif num == 4:
        lcd.lcd_display_string("CONSEJO:", 1)
        lcd.lcd_display_string("YO NO HARIA ESO", 2)
    else:
        lcd.lcd_display_string("Y CREERAS QUE", 1)
        lcd.lcd_display_string("VAS GANANDO...", 2)


def mssg_robotTurn(lcd):
    lcd.lcd_clear()
    num = random.randint(1,5)
    if num == 1:
        lcd.lcd_display_string("PODEIS SUBIR", 1)
        lcd.lcd_display_string("LA DIFICULTAD?", 2)
    elif num == 2:
        lcd.lcd_display_string("QUIETO AHI,", 1)
        lcd.lcd_display_string("ES MI TURNO", 2)
    elif num == 3:
        lcd.lcd_display_string("PODEIS SUBIR", 1)
        lcd.lcd_display_string("LA DIFICULTAD?", 2)
    elif num == 4:
        lcd.lcd_display_string("ME LO PONES", 1)
        lcd.lcd_display_string("DEMASIADO FACIL", 2)
    else:
        lcd.lcd_display_string("QUE PENA ME DAS", 1)
        lcd.lcd_display_string("ERES MALISIMO", 2)
    
    
def mssg_cheating(lcd):
    lcd.lcd_clear()
    num = random.randint(1,5)
    if num == 1:
        lcd.lcd_display_string("       UPS!", 1)
        lcd.lcd_display_string("JEJEJEJEJEJEJE", 2)
    elif num == 2:
        lcd.lcd_display_string("UNA FICHA AQUI...", 1)
        lcd.lcd_display_string("OTRA POR ALLI...", 2)
    elif num == 3:
        lcd.lcd_display_string("CASI...", 1)
        lcd.lcd_display_string("PERO NO", 2)
    elif num == 4:
        lcd.lcd_display_string("VAYA, SE ME HA", 1)
        lcd.lcd_display_string("IDO EL SERVO", 2)
    else:
        lcd.lcd_display_string("QUE HA PASADO?", 1)
        lcd.lcd_display_string("NO GANAS EH", 2) 
    
        
def mssg_win(lcd):
    lcd.lcd_clear()
    num = random.randint(1,5)
    if num == 1:
        lcd.lcd_display_string("NO GANAS NI", 1)
        lcd.lcd_display_string("A UN ROBOT :)", 2)
    elif num == 2:
        lcd.lcd_display_string("LO QUE DECIA...", 1)
        lcd.lcd_display_string("ERES MALISIMO", 2)
    elif num == 3:
        lcd.lcd_display_string("VAYA PALIZA", 1)
        lcd.lcd_display_string("CRACK", 2)
    elif num == 4:
        lcd.lcd_display_string("NO GANAS NI", 1)
        lcd.lcd_display_string("A PARCHIS-BOT", 2)
    else:
        lcd.lcd_display_string("APESTA A ", 1)
        lcd.lcd_display_string("DERROTA", 2) 


def mssg_lose(lcd):
    lcd.lcd_clear()
    num = random.randint(1,5)
    if num == 1:
        lcd.lcd_display_string("TE HE DEJADO", 1)
        lcd.lcd_display_string("GANAR, CRACK", 2)
    elif num == 2:
        lcd.lcd_display_string("NO TE VENGAS", 1)
        lcd.lcd_display_string("ARRIBA CAMPEON", 2)
    elif num == 3:
        lcd.lcd_display_string("ORGULLOSO?", 1)
        lcd.lcd_display_string("SOY UN ROBOT", 2)
    elif num == 4:
        lcd.lcd_display_string("NO ESTABA", 1)
        lcd.lcd_display_string("ATENTO", 2)
    else:
        lcd.lcd_display_string("QUE SUERTE", 1)
        lcd.lcd_display_string("HAS TENIDO...", 2) 


def mssg_emptyBoard(lcd):
    lcd.lcd_clear()
    lcd.lcd_display_string("VACIA", 1)
    lcd.lcd_display_string("EL TABLERO", 2)


def mssg_ready2calibrate(lcd):
    lcd.lcd_clear()
    lcd.lcd_display_string("COLOCA FICHAS EN", 1)
    lcd.lcd_display_string("COL: 1 Y 7", 2)

# ==============================================================================
# PLAY AGAIN OR NOT
# ==============================================================================

def playAgain(level_button, finish_button, lcd):
    global FINISH_SELECTION
    global LEVEL
    global LEVEL_PRESSED
    
    play_again = False
    mssg_again(lcd,play_again)
    
    while not FINISH_SELECTION:
        
        level_button.when_pressed = pressButtonLevel
        
        if LEVEL_PRESSED == True:
            if play_again:
                play_again = False
                mssg_again(lcd,play_again)
            else:
                play_again = True
                mssg_again(lcd,play_again)
            LEVEL_PRESSED = False
            
        finish_button.when_pressed = pressButtonFinish
    
    FINISH_SELECTION = False
    return play_again

def emptyBoard(finish_button, lcd):
    global FINISH_SELECTION
    
    mssg_emptyBoard(lcd)
    
    while not FINISH_SELECTION:
        finish_button.when_pressed = pressButtonFinish
    
    FINISH_SELECTION = False


# ==============================================================================
# FUNCIONES GENERALES
# ==============================================================================

def declareAll():
    level_button, finish_button = declare_buttons()
    level_led = declare_level_led()
    turn_led = declare_turn_led()
    lcd = I2C_LCD_driver.lcd()
    return level_button, finish_button, level_led, turn_led, lcd


def closeAll(level_button, finish_button, level_led, turn_led, lcd):
    close_buttons(level_button, finish_button)
    close_level_led(level_led)
    close_turn_led(turn_led)
    lcd.lcd_clear()
    
    
    

