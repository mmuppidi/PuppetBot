import botocore
from base import BaseClass

class ChatBotAgent(BaseClass):

    def __init__(self, ctx):
        super(ChatBotAgent, self).__init__(ctx)
        self._lex_client = self._ctx.authenticator.get_client('lex-runtime')
        self._polly_client = self._ctx.authenticator.get_client('polly')
        

    def communicate(self, audioStream):
        try :
            state = {}
            lex_response = self._lex_client.post_content(
                                                    inputStream=audioStream,
                                                    botName=self._lex_config['bot_name'],
                                                    botAlias= self._lex_config['bot_alias'],
                                                    userId= self._lex_config['user_id'],
                                                    contentType= self._lex_config['content_type'])

            with open(self._ctx.response_audio_file, 'w') as respFileObj:
                respFileObj.write(lex_response['audioStream'].read())

            state['dialogState'] = lex_response['dialogState']

            polly_response = self._polly_client.synthesize_speech(
                                                    OutputFormat='json',
                                                    SpeechMarkTypes=['viseme'],
                                                    Text=lex_response['message'],
                                                    VoiceId=self._polly_config['voice_id'])

            state['phonemes'] = polly_response['AudioStream']

            return state

        except botocore.exceptions.ClientError as err:
            logger.error('Error communicating to lex/polly service : {}'.format(str(err)))

    def synthesize_speech(self, message):
        response = self._polly_client.synthesize_speech(
                                                    OutputFormat='mp3',
                                                    Text=message,
                                                    VoiceId=self._polly_config['voice_id'])
        with open(self._ctx.response_audio_file, 'w') as respFileObj:
            respFileObj.write(response['AudioStream'].read())

        response = self._polly_client.synthesize_speech(
                                                    OutputFormat='json',
                                                    SpeechMarkTypes=['viseme'],
                                                    Text=message,
                                                    VoiceId=self._polly_config['voice_id'])
        return response['AudioStream']

