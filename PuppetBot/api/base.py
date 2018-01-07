from abc import ABCMeta
import logging
import sys

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s')
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel('DEBUG')

class BaseClass(object):
    __metaclass__ = ABCMeta

    def __init__(self, ctx):
        self._ctx = ctx
        self._logger = ctx.logger
        self._populate_attributes_from_config(self._ctx.config)

    def _populate_attributes_from_config(self, config):
        if (config and self.__class__.__name__ in config and 
                                config[self.__class__.__name__]):
            for key in config[self.__class__.__name__]:
                setattr(self, '_'+key, config[self.__class__.__name__][key])


class Context(object):

    def __init__(self, config=None, logger=LOGGER):
        self.config = config
        self.logger = logger
        self.authenticator = None 

    def set_authenticator(self, authenticator):
        self.authenticator = authenticator
