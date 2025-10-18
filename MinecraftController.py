import serial.tools.list_ports
import keyboard
from pynput.mouse import Button, Controller
import time
import win32api
import win32con

#Function for moving camera, use Windows32 API library to simulae mouse movements
def move_camera(dx, dy):
    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int(dx), int(-dy), 0, 0)

#Function to release all keys if held
def release_all_keys():
    keyboard.release('w')
    keyboard.release('s')
    keyboard.release('a')
    keyboard.release('d')
    keyboard.release('space')
    mous.release(Button.right)
    mous.release(Button.left)

#Function to set a specific key state
def set_key(key, should_press):
    #If the keystate of a specific key is NOT what data receives
    if key_states[key] != should_press:
        #If it key should be pressed (true)
        if should_press:
            keyboard.press(key)
        #Else, release the key
        else:
            keyboard.release(key)
        #update the key state to the current key state
        key_states[key] = should_press

#Dictionary to store keys and states
key_states = {
    'w': False,
    's': False,
    'a': False,
    'd': False,
    'space': False
}

#loop value
loop = True
#deadzones for movement joystick
deadzone1 = 540
deadzone2 = 460
#controller object for functions
mous = Controller()

#states of LMB / RMB
left_state = 1
right_state = 1

#Debounce variables for certain keystrokes that are NOT related to movement
last_scroll_time = 0
scroll_cooldown = 0.15  #150ms between scrolls
last_e_press_time = 0
e_cooldown = 0.5  #300ms between inventory toggles
last_q_press_time = 0
q_cooldown = 0.1 #100ms between item drops
last_shift_press_time = 0
shift_cooldown = 0.5 #500ms between sneaking
last_esc_press_time = 0
esc_cooldown = 0.3 #300ms between pressing esc

#data time variables for data receiving tracing
last_data_time = 0
data_timeout = 0.1

#Serial port finding / connecting
ports = serial.tools.list_ports.comports()
serialInst = serial.Serial(port = 'COM4', baudrate= 115200, timeout= 0.001)

portList = []

#prints out all serial ports
for onePort in ports:
    portList.append(str(onePort))
    print(str(onePort))

"""The indexes used of variable "decode" can be customized based on what values you want to perform what task
Based on the setup of my Arduino Code and buton / Joystick setup, this is what I went with"""

#Main loop for all controls
while loop:
    #Variable to keep track of curren time
    current_time = time.time()

    #When last time since received data is > 0 seconds and greater than a timeout
    if last_data_time > 0 and (current_time - last_data_time) > data_timeout:
        release_all_keys() #release all the keys
        last_data_time = 0 #reset time to 0

    #button to close script when done
    if keyboard.is_pressed('`'):    
        serialInst.close()
        release_all_keys()
        loop = False
        break

    #Receive data from Serial Port
    latest_packet = None
    while serialInst.in_waiting:
        packet = serialInst.readline()
        if packet:
            latest_packet = packet

    #if the latest packet is valid
    if latest_packet is not None:
        #decode the packet into a 13 integer list
        try:
            keystroke = packet.decode('utf-8').strip('\n')
            decode = list(map(int, keystroke.split()))
            if len(decode) != 13: #if length isnt 13, wont use the line of data
                continue
        except (UnicodeDecodeError, ValueError): #catch unicode decoding errors or value errors 
            continue
        
        #print list for debugging
        print(decode)

        #variables to determine if W or S should be pressed
        w_should_press = decode[0] > deadzone1
        s_should_press = decode[0] < deadzone2
        #set keys accordingly
        set_key('w', w_should_press)
        set_key('s', s_should_press)
        
        #variables to determine if A or D should be pressed
        d_should_press = decode[1] > deadzone1
        a_should_press = decode[1] < deadzone2
        #set keys accordingly
        set_key('d', d_should_press)
        set_key('a', a_should_press)

        # Shift (crouch/sprint)
        if decode[7] != 1 and (current_time - last_shift_press_time) > shift_cooldown:
            keyboard.press('shift')
            time.sleep(0.05)
            keyboard.release('shift')
            last_shift_press_time = current_time

        # Jump (space), Hold while button pressed
        set_key('space', decode[10] != 1)

        # Drop item (Q)
        if decode[11] != 1 and (current_time - last_q_press_time) > q_cooldown:
            keyboard.press('q')
            time.sleep(0.05)
            keyboard.release('q')
            last_q_press_time = current_time

        # Inventory (E)
        if decode[6] != 1 and (current_time - last_e_press_time) > e_cooldown:
            keyboard.press('e')
            time.sleep(0.05)
            keyboard.release('e')
            last_e_press_time = current_time

        # Escape
        if decode[12] != 1 and (current_time - last_esc_press_time) > esc_cooldown:
            keyboard.press('esc')
            time.sleep(0.05)
            keyboard.release('esc')
            last_esc_press_time = current_time

        # Mouse wheel (scrolling) - Throttled
        if (current_time - last_scroll_time) > scroll_cooldown:
            if decode[8] != 1:
                mous.scroll(0, -1)  # Scroll down
                last_scroll_time = current_time
            elif decode[9] != 1:
                mous.scroll(0, 1)   # Scroll up
                last_scroll_time = current_time

        #Mouse / Camera movement
        if(abs(decode[2]) > 2 or abs(decode[3]) > 2):
            move_camera(decode[3], decode[2])
        
        if decode[4] == 0:  # Button pressed (pullup = 0 when pressed)
            if right_state != 0:
                mous.press(Button.right)
                right_state = 0
        else:  # Button released
            if right_state != 1:
                mous.release(Button.right)
                right_state = 1
        
        # Left mouse button - hold while pressed
        if decode[5] == 0:  # Button pressed (pullup = 0 when pressed)
            if left_state != 0:
                mous.press(Button.left)
                left_state = 0
        else:  # Button released
            if left_state != 1:
                mous.release(Button.left)
                left_state = 1




