import serial.tools.list_ports
import keyboard
from pynput.mouse import Button, Controller
import time
import win32api
import win32con

def move_camera(dx, dy):
    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int(dx), int(-dy), 0, 0)

def release_all_keys():
    keyboard.release('w')
    keyboard.release('s')
    keyboard.release('a')
    keyboard.release('d')
    keyboard.release('space')
    mous.release(Button.right)
    mous.release(Button.left)

def set_key(key, should_press):
    #Only press/release if state actually changes"""
    if key_states[key] != should_press:
        if should_press:
            keyboard.press(key)
        else:
            keyboard.release(key)
        key_states[key] = should_press

key_states = {
    'w': False,
    's': False,
    'a': False,
    'd': False,
    'space': False,
    'shift': False
}

loop = True
deadzone1 = 540
deadzone2 = 460
btn = ''
mous = Controller()

debounce_time = 0.05 
last_left_change = 0
last_right_change = 0
left_state = 1
right_state = 1

last_scroll_time = 0
scroll_cooldown = 0.15  # 150ms between scrolls
last_e_press_time = 0
e_cooldown = 0.5  # 300ms between inventory toggles
last_q_press_time = 0
q_cooldown = 0.1
last_shift_press_time = 0
shift_cooldown = 0.5
last_esc_press_time = 0
esc_cooldown = 0.3
last_f_press_time = 0
f_cooldown = 0.3
last_r_press_time = 0
r_cooldown = 0.3

last_data_time = 0
data_timeout = 0.1

ports = serial.tools.list_ports.comports()
serialInst = serial.Serial(port = 'COM4', baudrate= 115200, timeout= 0.001)

portList = []

for onePort in ports:
    portList.append(str(onePort))
    print(str(onePort))


while loop:
    current_time = time.time()

    if last_data_time > 0 and (current_time - last_data_time) > data_timeout:
        release_all_keys()
        last_data_time = 0

    if keyboard.is_pressed('`'):    
        serialInst.close()
        release_all_keys()
        loop = False
        break

    latest_packet = None
    while serialInst.in_waiting:
        packet = serialInst.readline()
        if packet:
            latest_packet = packet

    if latest_packet is not None:
        try:
            keystroke = packet.decode('utf-8').strip('\n')
            decode = list(map(int, keystroke.split()))
            if len(decode) != 13:
                continue
        except (UnicodeDecodeError, ValueError):
            continue
        
        print(decode)

        w_should_press = decode[0] > deadzone1
        s_should_press = decode[0] < deadzone2
        set_key('w', w_should_press)
        set_key('s', s_should_press)
        
        # Left/Right (A/D)
        d_should_press = decode[1] > deadzone1
        a_should_press = decode[1] < deadzone2
        set_key('d', d_should_press)
        set_key('a', a_should_press)

        # Shift (crouch/sprint)
        set_key('shift', decode[10] != 1)
        # Jump (space) - Hold while button pressed
        set_key('space', decode[8] != 1)

        # Drop item (Q)
        if decode[11] != 1 and (current_time - last_q_press_time) > q_cooldown:
            keyboard.press('q')
            time.sleep(0.05)
            keyboard.release('q')
            last_q_press_time = current_time

        # Inventory (E)
        if decode[7] != 1 and (current_time - last_e_press_time) > e_cooldown:
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

        if decode[6] != 1 and (current_time - last_r_press_time) > r_cooldown:
            keyboard.press('r')
            time.sleep(0.05)
            keyboard.release('r')
            last_r_press_time = current_time

        if decode[9] != 1 and (current_time - last_f_press_time) > f_cooldown:
            keyboard.press('f')
            time.sleep(0.05)
            keyboard.release('f')
            last_f_press_time = current_time

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


