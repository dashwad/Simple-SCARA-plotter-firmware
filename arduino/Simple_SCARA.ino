#include <AccelStepper.h>
#include <MultiStepper.h>

#define HOMING_SPEED       500

#define X_STEP_PIN         54
#define X_DIR_PIN          55
#define X_ENABLE_PIN       38
#define X_ENDSTOP           3
#define X_HOMING_OFFSET  -600 //CHANGe KLATER

#define Y_STEP_PIN     60
#define Y_DIR_PIN      61
#define Y_ENABLE_PIN   56
#define Y_ENDSTOP      14
#define Y_HOMING_OFFSET  -600 //CHANGe KLATER

#define Z_STEP_PIN     46
#define Z_DIR_PIN      48
#define Z_ENABLE_PIN   62
#define Z_ENDSTOP      18
#define Z_HOMING_OFFSET  -600 //CHANGe KLATER

AccelStepper motorx(AccelStepper::DRIVER, X_STEP_PIN, X_DIR_PIN);
AccelStepper motory(AccelStepper::DRIVER, Y_STEP_PIN, Y_DIR_PIN);
AccelStepper motorz(AccelStepper::DRIVER, Z_STEP_PIN, Z_DIR_PIN);

MultiStepper wholeArm;

String fromSerial = "";
bool commandReady = false;



void setup() {
  fromSerial.reserve(200);

  Serial.begin(9600);
  Serial.println("");
  Serial.println("--------------------");
  Serial.println("--------------------");
  Serial.println("--------------------");
  Serial.println("");

  pinMode(X_ENABLE_PIN, OUTPUT);
  digitalWrite(X_ENABLE_PIN, LOW);

  pinMode(Y_ENABLE_PIN, OUTPUT);
  digitalWrite(Y_ENABLE_PIN, LOW);

  pinMode(Z_ENABLE_PIN, OUTPUT);
  digitalWrite(Z_ENABLE_PIN, LOW);

  pinMode(X_ENDSTOP, INPUT_PULLUP);
  pinMode(Y_ENDSTOP, INPUT_PULLUP);
  pinMode(Z_ENDSTOP, INPUT_PULLUP);

  motorx.setMaxSpeed(1000);
  motorx.setAcceleration(500); // safe default accel

  motory.setMaxSpeed(1000);
  motory.setAcceleration(500); // safe default accel

  motorz.setMaxSpeed(1000);
  motorz.setAcceleration(2000);

  wholeArm.addStepper(motorx);             // Add motorx into the arm system
  wholeArm.addStepper(motory);             // Add motory into the arm system

  Serial.println("Arduino Booted!");  

  printMenu();
}

void loop() {

  if (commandReady) {

    if (fromSerial.charAt(0) == 'W' || fromSerial.charAt(0) == 'H' || fromSerial.charAt(0) == 'Z') {
      processWaypoint(fromSerial);
    }
    else {
      splitCommand(fromSerial);
    }

    fromSerial = "";
    commandReady = false;

  }

  motorx.run();
  motory.run();
  motorz.run();

}

void serialEvent() {
  while (Serial.available() /*This means while there is stuff being recieved from serial*/) {
    char serialChar = (char)Serial.read(); //copying char from serial

    if (serialChar == '\n') {
      commandReady = true;
    } 
    else {
      fromSerial += serialChar;
    }
    //Adding chars into raw command and comleting if newline

  }
}

void splitCommand(String unsplitCommand) {
  int splitting = 0;
  bool stillLeft = true;

  while (stillLeft) {

    int commaLocation = unsplitCommand.indexOf(',', splitting); //-1 will if none are left

    String command;

    if (commaLocation == -1) { 
      // no more commas left — this is the final command
      command = unsplitCommand.substring(splitting);
      
      stillLeft = false;

    } 
    else {
      command = unsplitCommand.substring(splitting, commaLocation); //Grabs text from the start of the current split to the next comma

      splitting = commaLocation + 1; // moves the currently splitting index to in front of the next command

    }

    Serial.println("Sent: " + command);

    processCommand(command);

  }
  Serial.println("----------");

    
}

void processCommand(String command) {

  char commandLetter = command.charAt(0); //reads first char
  char axisLetter = command.charAt(1); //reads first char


  AccelStepper* motor = nullptr;

  if (axisLetter == 'x'){
    motor = &motorx;
  }
  else if (axisLetter == 'y'){
    motor = &motory;
  }
  else if (axisLetter == 'z'){
    motor = &motorz;
  }
  else if (commandLetter == '?') {
    printMenu();
  }
  else {
    Serial.println("Invalid Command (unknown axis)");
    return;
  }



  if (commandLetter == 's'){ // /btw that checks what the string starts with
    int speed = command.substring(2).toInt(); //and .substring(1) cuts off the first char if the string. and converts to int
    (*motor).setMaxSpeed(speed); //btw this only changes max speed. Speed is generally defined by accel unless accel is really high
  }

  else if (commandLetter == 'a'){ //same for rest
    int accel = command.substring(2).toInt(); 
    (*motor).setAcceleration(accel);
  }

  else if (commandLetter == 'm'){
    int move = command.substring(2).toInt();
    (*motor).moveTo(move);
  }

  else if (commandLetter == 'j'){
    int jog = command.substring(2).toInt();
    (*motor).move(jog);
  }
  else if (commandLetter == 'p'){
    (*motor).setCurrentPosition(0);
  }

  else if (commandLetter == 'h'){
    (*motor).moveTo(0);
  }

  else if (commandLetter == 'x'){
    (*motor).stop();
  }


  else {
    Serial.println("-------------------");
    Serial.println("Invalid Command (unknown command)");
    Serial.println("-------------------");
  }

}

void processWaypoint(String command){

  Serial.println("Sent: " + command);

  long xsteps; //long in case the step number is really high so like to prevent overflow that might happen with int
  long ysteps;

  if (command.startsWith("Z")){
    String direction = command.substring(1);
    if (direction == "UP"){
      Serial.println("Moving Z-Axis UP-----------------------------------------------------------------------------------------------------"); //Put UP logic here 
      motorz.moveTo(500);

      while (motorz.distanceToGo() != 0){
        motorz.run();
      }
    
    }
    else if (direction == "DOWN"){
      Serial.println("Moving Z-Axis DOWN-----------------------------------------------------------------------------------------------------"); //Put DOWN logivc here
      motorz.moveTo(0);

      while (motorz.distanceToGo() != 0){
        motorz.run();
      }

    }
    //put run here (ideally blocvking)

  }
  else {

    if (command.startsWith("H")){ //Double quotes cause command is a string
      String axis = command.substring(1);

      if (axis == "x"){
        homeX();
        return;
      }
      else if (axis == "y"){
        homeY();
        return;
      }
      else {
        Serial.println("-------------------");
        Serial.println("Invalid Command (unknown command)");
        Serial.println("-------------------");
        motorx.setSpeed(0);   
        motory.setSpeed(0);
        motorx.move(0);
        motory.move(0);
      }

    }
    else if (command.startsWith("W")){
      String waypoint = command.substring(1);

      int commaLocation = waypoint.indexOf(',');

      if (commaLocation == -1){
        Serial.println("Invalid waypoint command. Please format command in the way of w<xsteps>,<ysteps>");
        return;
      }


      xsteps = waypoint.substring(0, commaLocation).toInt(); 
      ysteps = waypoint.substring(commaLocation + 1).toInt();

      Serial.print("X steps: ");
      Serial.println(xsteps);
      Serial.print("Y steps: ");
      Serial.println(ysteps);

      long targets[2];

      targets[0] = xsteps;
      targets[1] = ysteps;

      wholeArm.moveTo(targets);
      wholeArm.runSpeedToPosition(); //IMPORTANT! The code WILL block here so when this line of code is running, nothing else can or will happen

      motorx.setSpeed(0);   
      motory.setSpeed(0);
      motorx.move(0);
      motory.move(0);
    }

  }

  Serial.println("MOVE COMPLETED");
}

void homeX() {
  motorx.setMaxSpeed(300);   
  motorx.setSpeed(300); 

  while (digitalRead(X_ENDSTOP) == HIGH) { // keep moving until is triggered
    motorx.runSpeed();
  }

  motorx.setSpeed(0);
  motorx.setCurrentPosition(0);         //temp set edstop point as 0

  motorx.setMaxSpeed(HOMING_SPEED);
  motorx.setSpeed(HOMING_SPEED);  

  motorx.setAcceleration(1500);
  motorx.moveTo(X_HOMING_OFFSET);

  while (motorx.distanceToGo() != 0) {   // block here until offset is done
    motorx.run();
  }

  motorx.setCurrentPosition(0);

}

void homeY() {
  motory.setMaxSpeed(300);   
  motory.setSpeed(300);       

  while (digitalRead(Y_ENDSTOP) == HIGH) { // keep moving until triggered
    motory.runSpeed();
  }

  motory.setSpeed(0);
  motory.setCurrentPosition(0);          //temp set edstop point as 0

  motory.setMaxSpeed(HOMING_SPEED);
  motory.setSpeed(HOMING_SPEED);  

  motory.setAcceleration(1500);
  motory.moveTo(Y_HOMING_OFFSET);

  while (motory.distanceToGo() != 0) {    // block here until offset is done
    motory.run();
  }

  motory.setCurrentPosition(0);
}

void printMenu() {

  Serial.println("---- Commands ----");
  Serial.println("a<axis><number>    -> sets accelaration of motor <axis> to <number>");
  Serial.println("s<axis><number>    -> sets maximum speed of motor <axis> to <number>");
  Serial.println("m<axis><number>    -> moves motor <axis> to <number> steps in absolute position");
  Serial.println("j<axis><number>    -> jogs motor <axis> <number> steps in either the positive or negative direction");
  Serial.println("p<axis>            -> sets current position of <axis> as 0")
  Serial.println("h<axis>            -> returns motor <axis> to 0 steps in absolute position");
  Serial.println("x<axis>            -> stops motor <axis>");
  Serial.println("?                  -> shows this menu");
  Serial.println("Add commas without whitespaces between commands to run simultaneously");
  Serial.println("---- Printing ----");
  Serial.println("W<xsteps>,<ysteps> -> synchronised waypoint move, both axes arrive together (for actual printing)");
  Serial.println("H<axus             -> home <axis> to the endstop and then offsets(for actual printing)");
  Serial.println("-------------------");

}