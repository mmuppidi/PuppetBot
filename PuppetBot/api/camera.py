
from base import BaseClass
from cStringIO import StringIO
from picamera import PiCamera


class Camera(BaseClass):


    def __init__(self, ctx):
        super(Camera, self).__init__(ctx)
        self._camera = PiCamera

    def capture(self):
        camera = PiCamera()
        try:
            image = StringIO()
            camera.capture(image, 'jpeg')
            return image 
        finally:
            camera.close()
        



