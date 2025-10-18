#include <WiFi.h>
#include <esp_now.h>

uint8_t peer_mac[] = {0x3C, 0x8A, 0x1F, 0x5D, 0xD0, 0xE0}; //MAC address of peer ESP32
#define wifi_channel 6

esp_now_peer_info_t peerinfo; //ESP-NOW peer info for peer ESP32

//Pin declaration for joysticks
const int SW1 = 32;
const int X1 = 36;
const int Y1 = 39;

const int SW2 = 33;
const int X2 = 34;
const int Y2 = 35;

//Pin declaration for pushbutton (Labeled according to Minecraft controls)
const int shift = 23;
const int dropper = 22;
const int inv = 19;
const int jump = 25;
const int down = 26;
const int up = 27;
const int esc = 18;

//Array of pushbutton pins
const int buttons[9] = {23, 22, 19, 25, 26, 27, 18, 32, 33};

//Deadzone and center for joysticks
const int deadzone = 100;
const int center =  489;

int decode[13]; //integer array to be sent through ESP32

bool first_send = true; //Boolean to see if data sent is new

int last_movement_decode[2] = {0}; //empty array to compare previous analog values from movement joystick
int last_button_state[9] = {1, 1, 1, 1, 1, 1, 1, 1, 1};

bool MovementStateChanged() {
  // Check if movement joystick has changed from last transmission
  if (first_send) return true;
  
  int current_x1 = analogRead(X1);
  int current_y1 = analogRead(Y1);
  
  // Check for changes with a small tolerance for analog values
  if(abs(current_x1 - last_movement_decode[0]) > 10) return true;
  if(abs(current_y1 - last_movement_decode[1]) > 10) return true;
  
  return false;
}

bool ButtonStateChanged() {
  // Check if any button state has changed
  for(int i = 0; i < 9; i++){
    int current_state = digitalRead(buttons[i]);
    if(current_state != last_button_state[i]) {
      return true;
    }
  }
  return false;
}

bool OtherInputActive() {
  // Check if camera, buttons, or other inputs are active
  for(int i = 0; i < 9; i++){
    if(digitalRead(buttons[i]) == LOW){
      return true;
    }
  }

  int x2 = analogRead(X2); 
  int y2 = analogRead(Y2);

  // Check if camera joystick is being moved
  if(abs(x2-center) > deadzone) return true;
  if(abs(y2-center) > deadzone) return true;

  return false;
}

//Setup and initialization
void setup() {
  Serial.begin(115200); //begin serial port for debugging
  WiFi.mode(WIFI_STA); //begin and set wifi channel for ESP-NOW
  WiFi.setChannel(wifi_channel);
  esp_now_init(); //start ESP-NOW

  memcpy(peerinfo.peer_addr, peer_mac, 6); //Copy the peer mac address into the peerinfo 
  peerinfo.channel = wifi_channel; //set wifi channel of peer info
  peerinfo.encrypt = false; //optional to encrypt ESP-NOW protocol

  esp_now_add_peer(&peerinfo); //add peer ESP32 according to peerinfo 
  Serial.println("ESP-NOW master ready to send");

  analogReadResolution(10); //change analog resolution to 10-bit (0-1023)

  //intialize all buttons
  pinMode(SW1, INPUT_PULLUP);
  pinMode(SW2, INPUT_PULLUP);
  pinMode(inv, INPUT_PULLUP);
  pinMode(shift, INPUT_PULLUP);
  pinMode(down, INPUT_PULLUP);
  pinMode(up, INPUT_PULLUP);
  pinMode(dropper, INPUT_PULLUP);
  pinMode(jump, INPUT_PULLUP);
  pinMode(esc, INPUT_PULLUP);

}

void loop() {
  if(MovementStateChanged() || OtherInputActive() || ButtonStateChanged()){
    decode[0] = analogRead(X1); //Xvalue1
    decode[1] = analogRead(Y1); //Yvalue1
    decode[2] = map(analogRead(X2), 0, 1023, -15, 15); //Xvalue2
    decode[3] = map(analogRead(Y2), 0, 1023, -15, 15); //Yvalue2
    decode[4] = digitalRead(SW1); //Right click pushbutton
    decode[5] = digitalRead(SW2); //left click pushbutton
    decode[6] = digitalRead(inv); //Inventory pushbutton
    decode[7] = digitalRead(shift); //crouch pushbutton
    decode[8] = digitalRead(down); //Scroll down pushbutton
    decode[9] = digitalRead(up); //Scroll up pushbutton
    decode[10] = digitalRead(jump); //Jump pushbutton
    decode[11] = digitalRead(dropper); //drop bushbutton
    decode[12] = digitalRead(esc); //escape pushbutton

    //store new movement analog values as previous values for comparison
    last_movement_decode[0] = decode[0]; 
    last_movement_decode[1] = decode[1];

    //store pushbutton states into array for comparison
    for(int i = 0; i < 9; i++){
      last_button_state[i] = digitalRead(buttons[i]);
    }
    
    first_send = false; //set boolean to false as data is no longer new

    esp_now_send(peerinfo.peer_addr, (uint8_t*)decode, sizeof(decode)); //send data to peer ESP32
    delay(10);
  }
}
