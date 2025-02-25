// #include <Arduino.h>
// #include <stdio.h>

// // put function declarations here:
// unsigned char incoming[14];
// unsigned char term = 255;

// void setup() {
//   // put your setup code here, to run once:
//   Serial.begin(115200);
//   Serial.println("Connected");
// }

// void loop() {
//   // put your main code here, to run repeatedly:
//   if (Serial.available() > 0) {

//     // read the incoming byte:

//      Serial.readBytesUntil(term, incoming, 9);

//     // say what you got:

//     Serial.print("I received: ");

//     char i;
//     for (i = 0; i<8; ++i){
//       Serial.print(incoming[i], DEC);
//       Serial.print(",");
//     }
//     Serial.print('\n');
//   }
// }


#include <Arduino.h>

#define dirH1   16
#define pwmH1   4

#define dirH2   0
#define pwmH2   2

#define dirH3   15
#define pwmH3   23

#define dirH4   17
#define pwmH4   13

#define enV1    32
#define pwmV1_1 33
#define pwmV1_2 25

#define enV2    26
#define pwmV2_1 27
#define pwmV2_2 14

int HorizontalThrusterPinsDir[4]={dirH1,dirH2,dirH3,dirH4} ;
int HorizontalThrusterPinsSpeed[4]={pwmH1 , pwmH2 ,pwmH3 ,pwmH4} ;

int VerticalThrusterSp1[2] = {pwmV1_1 , pwmV2_1} ;
int VerticalThrusterSp2[2] = {pwmV1_2 , pwmV2_2} ;

float outputHorizontalThrusters[4] = {0, 0, 0, 0};
float outputVerticalThrusters[2] = {0, 0};



// Control Code for ROV Motion
// using 6 thruster configurations (4 horizontal, 2 vertical)

float Fx, Fy, Ty; // ROV forces and torque (Surge force, sway force, Yaw torque)
float F1, F2, F3, F4; // Thruster forces (FR,FL,BR,BL)

float Fz,Tp ; // ROV forces and torque (Heave force, Pitch torque)
float F5, F6; // Thruster forces

unsigned char incoming [10];
unsigned char term = 255;

// // Cytron Motor driver pins
// int pwm_pin1, dir_pin1;
// int pwm_pin2, dir_pin2;
// int pwm_pin3, dir_pin3;
// int pwm_pin4, dir_pin4;

void setup_H_motors(){

  pinMode(dirH1,OUTPUT);
  pinMode(pwmH1,OUTPUT);

  pinMode(dirH2,OUTPUT);
  pinMode(pwmH2,OUTPUT);

  pinMode(dirH3,OUTPUT);
  pinMode(pwmH3,OUTPUT);

  pinMode(dirH4,OUTPUT);
  pinMode(pwmH4,OUTPUT);

}

void setup_V_motors(){

  pinMode(pwmV1_1,OUTPUT);
  pinMode(pwmV1_2,OUTPUT);
  pinMode(enV1,OUTPUT);

  digitalWrite(enV1,HIGH);

  pinMode(pwmV2_1,OUTPUT);
  pinMode(pwmV2_2,OUTPUT);
  pinMode(enV2,OUTPUT);

  digitalWrite(enV2,HIGH);

}

void controlHmotors(float speed){
  for (int num = 0 ; num <=3 ; num++ ){
     digitalWrite(HorizontalThrusterPinsDir[num], (outputHorizontalThrusters[num] >= 0) ? HIGH : LOW );
     analogWrite(HorizontalThrusterPinsSpeed[num] , abs(outputHorizontalThrusters[num]) ) ;
  }

}
// Pseudoinverse matrix T_inverse
double T_inverse_Horizontal[4][3] = {
    {0.25, 0.25, 0.5},
    {0.25, -0.25, -0.5},
    {-0.25, 0.25, -0.5},
    {-0.25, -0.25, 0.5}
};

// Pseudoinverse matrix T_inverse
double T_inverse_Vertical[2][2] = {
    {0.5,  1},
    {0.5, -1}
};

// Output thruster forces

// Apply constraints to the thruster forces
// if the maximum absolute force exceeds the max allowed force, scale down
void applyConstraints(float* thruster_forces, int size, float max_force) {
    float max_abs_force = 0;

    // Find the maximum absolute value of the thruster forces
    for (int i = 0; i < size; i++) {
        if (abs(thruster_forces[i]) > max_abs_force) {
            max_abs_force = abs(thruster_forces[i]);
        }
    }

    // If the maximum absolute force exceeds the max allowed force, scale down
    if (max_abs_force > max_force) {
        float scaling_factor = max_force / max_abs_force;
        for (int i = 0; i < size; i++) {
            thruster_forces[i] *= scaling_factor; // Apply the scaling factor
          }
    }
}

void ComputeHorrizontalThrustForces(double* input, double T_inverse[4][3], float* outputThrusters){

  // Perform matrix multiplication outputThrusters = T_inverse * input

  for (int i = 0; i < 4; i++) {
    outputThrusters[i] = 0;
    for (int j = 0; j < 3; j++) {
      outputThrusters[i] += T_inverse[i][j] * input[j];
    }

  }

  float max_force=255 ;
  applyConstraints(outputThrusters, 4,max_force);

}

void ComputeVerticalThrustForces(double* input, double T_inverse[2][2], float* outputThrusters){

  // Perform matrix multiplication outputThrusters = T_inverse * input

  for (int i = 0; i < 2; i++) {
    outputThrusters[i] = 0;
    for (int j = 0; j < 2; j++) {
      outputThrusters[i] += T_inverse[i][j] * input[j];
    }

  }

  float max_force=255 ;
  applyConstraints(outputThrusters, 2,max_force);
}


// Configure the motor driver.

// CytronMD motor_FR(PWM_DIR, pwm_pin1, dir_pin1);                  // front_right thruster
// CytronMD motor_FL(PWM_DIR, pwm_pin2, dir_pin2);                  // front_left thruster
// CytronMD motor_BR(PWM_DIR, pwm_pin3, dir_pin3);
// CytronMD motor_BL(PWM_DIR, pwm_pin4, dir_pin4);

// void Move_Horizontal(float* outputHorizontalThrusters){


//   motor_FR.setSpeed(outputHorizontalThrusters[0]);
//   motor_FL.setSpeed(outputHorizontalThrusters[1]);
//   motor_BR.setSpeed(outputHorizontalThrusters[2]);
//   motor_BL.setSpeed(outputHorizontalThrusters[3]);

// }


void setup() {
  Serial.begin(115200);
}



void loop() {

  double inputH[3] = {1020, 0, 0};
  double inputV[2] = {510, 510};

  if (Serial.available()) {
    /*
      l-stick vert: surge (forward)
      l-stick horz: sway (right)

      r-stick vert: pitch
      r-stick horz: yaw

      L2, R2: elevation

    */

    Serial.print("test  ");

    Serial.readBytesUntil(term, incoming, 9);

    inputH [0] = (float) incoming [0] / 254.0 * 1023.0 * ((incoming [5] & 1)? -1 : 1);  // Fx
    inputH [1] = (float) incoming [1] / 254.0 * 1023.0 * ((incoming [5] & 2)? -1 : 1);  // Fy
    inputH [2] = (float) incoming [3] / 254.0 * 510.0 * ((incoming [5] & 8)? -1 : 1);  // Tau

    inputV [0] = (float) incoming [4] / 254.0 * 510.0 * ((incoming [5] & 16)? -1 : 1); // Fz
    inputV [1] = (float) incoming [2] / 254.0 * 255.0 * ((incoming [5] & 4)? -1 : 1);  // Tpitch

    for (int counter = 0 ; counter <=4  ; counter++){
      Serial.print(incoming [counter]) ;
      Serial.print(" ");
    }

  ComputeHorrizontalThrustForces(inputH, T_inverse_Horizontal, outputHorizontalThrusters);
  ComputeVerticalThrustForces(inputV, T_inverse_Vertical, outputVerticalThrusters);

  // Print the results
  Serial.println("Thruster Forces:");
  for (int i = 0; i < 4; i++) {
    Serial.print(" F");
    Serial.print(i + 1);
    Serial.print(": ");
    Serial.print(outputHorizontalThrusters[i], 2); // Print with 2 decimal places
  }

  for (int i = 0; i < 2; i++) {
    Serial.print(" F");
    Serial.print(i + 5);
    Serial.print(": ");
    Serial.print(outputVerticalThrusters[i], 2); // Print with 2 decimal places
  }

  Serial.println();

  }

  // Input vector R
  // Compute the thruster forces

  // delay(10000); // Wait for 1 second before repeating

}