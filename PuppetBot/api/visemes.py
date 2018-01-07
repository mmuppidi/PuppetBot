import json
import time
from base import BaseClass
from servo import ServoController

class Visemes(object):
    # mouth opening percentage
    sil = 0
    a = 75
    o = 100
    O = 100
    e = 50
    E = 50
    i = 50
    u = 0
    aa = 25 # @
    r = 50
    s = 25
    S = 25
    T = 50
    f = 0
    t = 25
    k = 25
    p = 0

    def __getattr__(cls, item):
        #print item 
        if item == "@" :
            return cls.aa

        raise AttributeError('Attribute {} not found'.format(item))

# change time step to time interval


class VisemePlayer(BaseClass):

    VISEME_MAPPING = VISEME_MAPPING = Visemes()

    def __init__(self, ctx):
        super(VisemePlayer, self).__init__(ctx)
        self._controller = ServoController(logger=self._logger, **self._ServoController)
        self._player_input = []

    @property
    def player_input(self):
        return self._player_input

    @player_input.setter
    def player_input(self, phonemes):
        discrete_signal = self._get_discrete_signal(phonemes)
        continuous_signal = self._discrete_to_continuous(discrete_signal)
        self._player_input = self._apply_sliding_window(continuous_signal)


    def _discrete_to_continuous(self, data):
        # data =  [(time, value), (time, value),...]
        max_time = data[-1][0]
        continuous_signal = []
        current_discrete_signal_index = 0
        for time_step in range(0, max_time+self._time_interval, self._time_interval):
            if time_step >= max_time:
                continuous_signal.append(data[-1][1])
                return continuous_signal 
            elif time_step >= data[current_discrete_signal_index + 1][0]:
                current_discrete_signal_index += 1

            continuous_signal.append(data[current_discrete_signal_index][1])

    def _get_discrete_signal(self, phonemes):
        # retutns [(time, value), (time, value),...]
        return [(phoneme['time'],
         self._controller.get_servo_input(getattr(self.VISEME_MAPPING, phoneme['value'])))for phoneme in phonemes]

    def _apply_sliding_window(self, signal):
        current_index = 0
        modified_signal = []
        padding_len = (self._sliding_window/self._time_interval)/2
        padding_signal = [self._controller._lower_limit for _ in range(padding_len)]
        signal = padding_signal + signal + padding_signal
        for i in range(padding_len, len(signal)-padding_len):
            modified_signal.append(sum(signal[i-padding_len:i+padding_len])/len(signal[i-padding_len:i+padding_len]))
        return modified_signal

    def get_input_lenght_estimate(self):
        # len of input in time
        return (len(self._player_input) * self._time_interval / 1000.0) - 0.1

    def play(self):
        time.sleep(self._player_offset)
        start_time = time.time()
        sleep_time = self._time_interval/1000.0
        for i, _input in enumerate(self._player_input):
            if time.time() < (i * sleep_time + start_time):
                time.sleep(sleep_time)
            self._controller.run(_input)

def decode_viseme_stream(stream):
    return [json.loads(viseme) for viseme in stream.read().split()]