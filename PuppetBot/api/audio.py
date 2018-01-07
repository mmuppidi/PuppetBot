from abc import ABCMeta, abstractmethod
from base import BaseClass
import subprocess
import time
import logging
import cStringIO
import shutil


class AudioRecorder(BaseClass):

    def __init__(self, ctx):
        super(AudioRecorder, self).__init__(ctx)
        self._delay = 0.0

    @property
    def delay(self):
        return self._delay

    @delay.setter
    def delay(self, value):
        self._delay = value

    def record(self):
        # applying the delay 
        time.sleep(self._delay)
        # Don't record if listner is stopped
        self.recorder_logic()
        

    def recorder_logic(self):
        # recorder logic goes here
        raise NotImplementedError

    def get_recording(self):
        # return a file like or StringIO like object
        raise NotImplementedError

    def stop(self):
        # logic for stopping the recording
        raise NotImplementedError

    def reset(self):
        # logic for resetting the recorder
        raise NotImplementedError

    def clean_up(self):
        # logic for cleaning up any files or tmp files or objects created in during recording
        raise NotImplementedError

class AudioPlayer(BaseClass):

    def __init__(self, ctx):
        super(AudioPlayer, self).__init__(ctx)

    @property
    def player_offset(self):
        return self._player_offset

    @player_offset.setter
    def player_offset(self, value):
        self._player_offset = value

    def play(self):
        # applying the delay 
        time.sleep(self._player_offset/ 1000.0)
        # Don't record if listner is stopped
        self.player_logic()

    def player_logic(self, audio_file):
        # audio player play logic 
        raise NotImplementedError

    def stop(self):
        # logic for stopping the recording
        raise NotImplementedError

    def clean_up(self):
        # logic for cleaning up any tmp files or objects created in during recording
        raise NotImplementedError

class SoxAudioRecorder(AudioRecorder):

    SOX_COMMAND = "sox -d -t wavpcm -c 1 -b 16 -r 16000 -e signed-integer --endian little - silence 1 0 1% 5 0.3t 2%"

    def __init__(self, ctx):
        super(SoxAudioRecorder, self).__init__(ctx)
        self.stopped = False 

    def recorder_logic(self):
        try :
            self._logger.debug("Starting audio listner.")

            if self.stopped:
                self._logger.debug("Recorder in stop state cannot record.")
                return
            self.process = subprocess.Popen(self.SOX_COMMAND, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

            out, err = self.process.communicate()

            if self.process.returncode:
                self._logger.error('Error running listner : {}.'.format(err.decode()))
                return 

            self.audioObj = cStringIO.StringIO(out)
            self._logger.debug("Recording successful !")

        except OSError as err:
            self._logger.debug('Error running listner : {}.'.format(str(err).decode()))
            return

    def get_recording(self):
        return self.audioObj

    def stop(self):
        self.stopped = True
        if self.process and self.process.poll() is None:
            self.process.kill()

    def clean_up(self):
        self.stop()

    def reset(self):
        self.clean_up()
        self.stopped = False

class MPG321AudioPlayer(AudioPlayer):

    MPG321_COMMAND = 'sudo mpg321 -a hw:1,0 '

    def __init__(self, ctx):
        super(MPG321AudioPlayer, self).__init__(ctx)

    def player_logic(self):


        try :
            command = self.MPG321_COMMAND + self._ctx.response_audio_file

            self.process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            out, err = self.process.communicate()

            if self.process.returncode:
                logger.error('Error playing audio : {}'.format(err.decode()))

        except OSError as err:
            logger.warning('Error playing audio : {}'.format(str(err).decode()))

    def stop(self):
        if self.process and self.process.poll() is None:
            self.process.kill()

    def clean_up(self):
        self.stop()
        shutil.rmtree(self._ctx.response_audio_file)