#include <esp_now.h>
#include <WiFi.h>
#define wifi_channel 6

int decode[13]; //same integer array as in Controller (must be same size and variable for ESP32)

//callback function for receiving data with ESP-NOW
void onReceive(const esp_now_recv_info_t *recv_info, const uint8_t *data, int data_len){
  if(data_len == sizeof(decode)){ //only copy data into variable if received data is valid
    memcpy(decode, data, data_len);
    //print received array in serial port 
    for(int i = 0; i < 13; i++){
      Serial.print(decode[i]);
      Serial.print(" ");
    }
    Serial.println();
  } else { //if not valid, return and discard
    return;
  }
}

//Setup and intialization
void setup() {
  Serial.begin(115200); //start serial port
  WiFi.mode(WIFI_STA); //set wifi mode
  WiFi.setChannel(wifi_channel); //set wifi channel
  delay(1000); //delay for 1 second to ensure all is initialized

  Serial.println(WiFi.macAddress()); //print mac address for debugging (if needed)

  //if ESP-NOW does not initialize properly, return
  if(esp_now_init() != ESP_OK){
    Serial.println("Error initializing ESPNOW");
    return;
  }
  Serial.println("ESP-NOW slave ready to receive");
  esp_now_register_recv_cb(onReceive); //perform callback function when data is received (runs every time data is received)
}

void loop() {
  // put your main code here, to run repeatedly:

}
