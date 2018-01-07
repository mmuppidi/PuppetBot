import Adafruit_PCA9685
from base import BaseClass

class ServoController(object):

    PWM = Adafruit_PCA9685.PCA9685()

    def __init__(self, channel=0, frequency=60, upper_limit=500, lower_limit=450, logger=None): # pulse length out of 4096
        self._channel = channel
        self.set_pwm_frequency(frequency)
        self._upper_limit = upper_limit
        self._lower_limit = lower_limit
        self._logger = logger
        self._range = self._upper_limit - self._lower_limit
        
    def set_pwm_frequency(self, value):
        self.PWM.set_pwm_freq(value)

    def get_servo_input(self, percentage):
        servo_input = self._lower_limit + int(percentage*self._range/100.0)
        return servo_input 

    def run(self,_input):
        if _input < self._lower_limit:
            _input = self._lower_limit
        elif _input > self._upper_limit:
            _input = self._upper_limit

        self.PWM.set_pwm(self._channel, 0, _input)

    def run_raw(self,_input):
        self.PWM.set_pwm(self._channel, 0, _input)

class ChocolateDispenser(BaseClass):

    def __init__(self, ctx):
        super(ChocolateDispenser, self).__init__(ctx)
        self._controller = ServoController(logger=self._logger, **self._ServoController)

    def _collect(self):
        self._controller.run_raw(self._collect_input)

    def _dispence(self):
        self._controller.run_raw(self._dispense_input)

    def dispense(self,count=None):
        count = count or self.count or 1
        for _ in range(count):
            self._collect()
            time.sleep(0.7)
            self._dispence()
            time.sleep(0.7)