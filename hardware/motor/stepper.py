import time


class Stepper():
    def __init__(self, board, number_of_steps, motor_pin_1, motor_pin_2, motor_pin_3, motor_pin_4):
        
        self.board = board                      # Change to your port

        self.step_numer = 0                     # which step the motor is on
        self.direction = 0                      # motor direction
        self.last_step_time = 0                 # time stamp in us of the last step taken
        self.number_of_steps = number_of_steps; # total number of steps for this motor

        # Arduino pins for the motor control connection:
        self.motor_pin_1 = motor_pin_1
        self.motor_pin_2 = motor_pin_2
        self.motor_pin_3 = motor_pin_3
        self.motor_pin_4 = motor_pin_4

        # pin_count is used by the stepMotor() method:
        self.pin_count = 4


    def setSpeed(self, whatSpeed):
        self.step_delay = 60 * 1000 * 1000 / self.number_of_steps / whatSpeed


    def step(self, steps_to_move):
        step_left = abs(steps_to_move)
        if (steps_to_move > 0): self.direction = 1
        if (steps_to_move < 0): self.direction = 0
        
        while (step_left > 0):
            # current_time = datetime.datetime.now().time()
            now = time.perf_counter_ns() / 1000
            if (now - self.last_step_time >= self.step_delay):
                self.last_step_time = now
                if (self.direction == 1):
                    self.step_numer += 1
                    if (self.step_numer == self.number_of_steps):
                        self.step_numer = 0
                else:
                    if (self.step_numer == 0):
                        self.step_numer = self.number_of_steps
                    self.step_numer -= 1
                    
                step_left -= 1
                
                self.stepMotor(self.step_numer % 4)
    

    def stepMotor(self, thisStep):
        if (thisStep == 0):
            self.board.digital[self.motor_pin_1].write(1)
            self.board.digital[self.motor_pin_2].write(0)
            self.board.digital[self.motor_pin_3].write(1)
            self.board.digital[self.motor_pin_4].write(0)
        elif (thisStep == 1):
            self.board.digital[self.motor_pin_1].write(0)
            self.board.digital[self.motor_pin_2].write(1)
            self.board.digital[self.motor_pin_3].write(1)
            self.board.digital[self.motor_pin_4].write(0)
        elif (thisStep == 2):
            self.board.digital[self.motor_pin_1].write(0)
            self.board.digital[self.motor_pin_2].write(1)
            self.board.digital[self.motor_pin_3].write(0)
            self.board.digital[self.motor_pin_4].write(1)
        elif (thisStep == 3):
            self.board.digital[self.motor_pin_1].write(1)
            self.board.digital[self.motor_pin_2].write(0)
            self.board.digital[self.motor_pin_3].write(0)
            self.board.digital[self.motor_pin_4].write(1)
