#include <Wire.h>
#include "BluetoothSerial.h"

BluetoothSerial SerialBT;
char cmd;


float RateRoll, RatePitch, RateYaw;
float RateCalibrationRoll, RateCalibrationPitch, RateCalibrationYaw;
int RateCalibrationNumber, TotalCalibrations = 2000;
int ledpin = 2;







void gyro_signals(void){
  // Start the I2C communication with the gyro
  Wire.beginTransmission(0x68); // 0x68 is the default path of the register of MPU 6050

  // Digital low pass filter (DLPF) to filter out the vibrations caused by the motors
  Wire.write(0x1A); // Address of the register to set the low pass filter
  Wire.write(0x05); // Set it to 5 to choose the DLPF with a cutoff frequency of 10 Hz
  Wire.endTransmission();

  // Sensitivity scale factor
  Wire.beginTransmission(0x68);
  Wire.write(0x1B); // Address of the register to set the sensitivity scale
  Wire.write(0x8); // The measurements of the MPU 6050 are recorded in lsb
  // Choose a sensitivity settings of 65.5 LSB/degrees/second 
  // This corresponds to the FS_SEL setting of one
  // https://youtu.be/yhz3bRQLvBY?list=PLeuMA6tJBPKsAfRfFuGrEljpBow5hPVD4&t=280
  Wire.endTransmission();

  // Import the measurement values of the gyro
  Wire.beginTransmission(0x68);
  // These are located in the registers that holds the gyroscope measurements
  // These register have the hexadecimal numbers 43 to 48
  Wire.write(0x43); // Start writing to 0x43 to indicate the first register you will use
  Wire.endTransmission();

  // Now request 6 bytes from the MPU 6050, such that you can pull the information of the six registers 43 - 48 from the MPU 6050
  Wire.requestFrom(0x68, 6);
  // The gyro measurements are the result of unsigned 16-bit measurement
  int16_t GyroX = Wire.read()<<8 | Wire.read();  
  int16_t GyroY = Wire.read()<<8 | Wire.read();
  int16_t GyroZ = Wire.read()<<8 | Wire.read();

  // Convert the measurement units to degrees/second
  RateRoll = (float)GyroX/65.5;
  RatePitch = (float)GyroY/65.5;
  RateYaw = (float)GyroZ/65.5;
}

void setup(){
  Serial.begin(57600);
  SerialBT.begin("Gesture");
  pinMode(ledpin, OUTPUT);

  Wire.setClock(400000);
  Wire.begin();
  delay(250);

  // Activating MPU 6050
  Wire.beginTransmission(0x68);
  // Write to the Power Management Register (0x6B)
  Wire.write(0x6B);
  // All bits in this register have to be set to zero in order for the device to start and continue in power mode
  Wire.write(0x00);
  Wire.endTransmission();

  Serial.println("Calibrating");
  digitalWrite(ledpin, HIGH);
  for (RateCalibrationNumber=0; RateCalibrationNumber < TotalCalibrations; RateCalibrationNumber++)
  {
    gyro_signals();
    RateCalibrationRoll += RateRoll;
    RateCalibrationPitch += RatePitch;
    RateCalibrationYaw += RateYaw;
    delay(1);
  }

  RateRoll -= RateCalibrationRoll;
  RatePitch -= RateCalibrationPitch;
  RateYaw -= RateCalibrationYaw;
  RateCalibrationRoll /= TotalCalibrations;
  RateCalibrationPitch /= TotalCalibrations;
  RateCalibrationYaw /= TotalCalibrations;
  Serial.println("Calibration Finished");
  digitalWrite(ledpin, LOW);



}

void loop() {
  gyro_signals();
  
  Serial.print("Roll Rate [°/s] = ");
  Serial.print(RateRoll);
  Serial.print(" Pitch Rate [°/s] = ");
  Serial.print(RatePitch);
  Serial.print(" Yaw Rate [°/s] = ");
  Serial.println(RateYaw);

  SerialBT.print("Roll: ");
  SerialBT.print(RateRoll);
  SerialBT.print(", Pitch: ");
  SerialBT.print(RatePitch);
  SerialBT.print(", Yaw: ");
  SerialBT.println(RateYaw);

  delay(50);  
}