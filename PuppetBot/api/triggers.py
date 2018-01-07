
from base import BaseClass
from camera import Camera


class Trigger(BaseClass):

    def __init__(self, ctx):
        super(Trigger, self).__init__(ctx)

    def wait_for_trigger(self):
        raise NotImplementedError()

class TimerTrigger(Trigger):
    def __init__(self, ctx):
        super(TimerTrigger, self).__init__(ctx)

    def wait_for_trigger(self):
        time.sleep(self._delay)

class RokgnitionTrigger(Trigger):

    def __init__(self, ctx):
        super(RokgnitionTrigger, self).__init__(ctx)
        self._rekognition_client = self._ctx.authenticator.get_client('rekognition')
        self._camera = Camera(self._ctx)

    def wait_for_trigger(self):

        while True:
            # https://projects.raspberrypi.org/en/projects/getting-started-with-picamera
            image = self._camera.capture().getvalue()

            with open('/home/pi/test.jpg','wb') as img :
                img.write(image)

            response = self._rekognition_client.detect_faces(
                                                    Image={
                                                        'Bytes': image
                                                    },
                                                    Attributes=['Default']
                                                )

            if response['FaceDetails']:
                self._logger.info('Face detected')
                break
            time.sleep(self._check_interval)