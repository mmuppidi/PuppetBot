
from base import BaseClass
from chatbot import ChatBotAgent
from servo import ChocolateDispenser
from visemes import VisemePlayer, decode_viseme_stream
from audio import SoxAudioRecorder, MPG321AudioPlayer
from constants import DialogState
from threading import Thread
import time 



class Session(BaseClass):

    def __init__(self, ctx):
        super(Session, self).__init__(ctx)

    def start(self):
        self._logger.debug('Starting a session')
        self.start_session()
        self.session_logic()
        self.end_session()
        self._logger.debug('Session ended')

    def start_session(self):
        raise NotImplementedError

    def session_logic(self):
        raise NotImplementedError

    def end_session(self):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError

class AudioBotSession(Session):

    def __init__(self, ctx):
        super(AudioBotSession,self).__init__(ctx)
        self._audio_recorder = SoxAudioRecorder(self._ctx)
        self._audio_player = MPG321AudioPlayer(self._ctx)
        self._chatbot_agent = ChatBotAgent(self._ctx)
        self._session_is_live = False 
        self.session_state = {}

    def start_session(self):
        self.session_is_live = True
        self.session_state = {'dialogState': DialogState.ElicitIntent}
        self.session_state['phonemes'] = self._chatbot_agent.synthesize_speech(self._greeting_message)

    def session_logic(self):
        while self.session_is_live :
            self._logger.debug('Starting an iteration of the session')
            self._audio_recorder.record()
            self._audio_player.play()

            if self.session_state['dialogState'] in [DialogState.Fulfilled, DialogState.Failed] :
                self.session_is_live = False
                if self.session_state['dialogState'] == DialogState.Fulfilled :
                    # todo something 

            time.sleep(self._delay_between_dialogs)
            if self.session_is_live:
                req_audio_obj = self._audio_recorder.get_recording()

                if req_audio_obj:
                    self.session_state = self._chatbot_agent.communicate(req_audio_obj)
                else:
                    self.session_is_live = False

    def end_session(self):
        # nothing to do
        pass

    def stop(self):
        self.session_is_live = False

class PuppetBotSession(Session):

    def __init__(self, ctx):
        super(PuppetBotSession,self).__init__(ctx)

        self._audio_recorder = SoxAudioRecorder(self._ctx)
        self._audio_player = MPG321AudioPlayer(self._ctx)
        self._chatbot_agent = ChatBotAgent(self._ctx)
        self._puppet_controller = VisemePlayer(self._ctx)
        self._session_is_live = False 
        self.session_state = {}

    def start_session(self):
        self.session_is_live = True
        self.session_state = {'dialogState': DialogState.ElicitIntent}
        self.session_state['phonemes'] = self._chatbot_agent.synthesize_speech(self._greeting_message)

    def session_logic(self):
        while self.session_is_live :
            self._logger.debug('Starting an iteration of the session')
            self._puppet_controller.player_input = decode_viseme_stream(self.session_state['phonemes'])
            self._audio_recorder.delay = self._puppet_controller.get_input_lenght_estimate()
            
            puppet_controller_thread = Thread(target=self._puppet_controller.play)
            audio_player_thread = Thread(target=self._audio_player.play)
            audio_recorder_thread = Thread(target=self._audio_recorder.record)

            puppet_controller_thread.start()
            audio_player_thread.start()
            audio_recorder_thread.start()
            audio_player_thread.join()
            puppet_controller_thread.join()

            # check if session has ended 
            if self.session_state['dialogState'] in [DialogState.Fulfilled, DialogState.Failed] :
                if audio_recorder_thread.is_alive():
                    audio_recorder_thread.join()
                self.session_is_live = False
                if self.session_state['dialogState'] == DialogState.Fulfilled :
                    # todo something 
                    pass

            time.sleep(self._delay_between_dialogs)

            if self.session_is_live:
                audio_recorder_thread.join()
                
                req_audio_obj = self._audio_recorder.get_recording()

                if req_audio_obj:
                    self.session_state = self._chatbot_agent.communicate(req_audio_obj)
                else:
                    self.session_is_live = False

    def end_session(self):
        # nothing to do
        pass

    def stop(self):
        self.session_is_live = False



