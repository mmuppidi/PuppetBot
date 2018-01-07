
from api.session import PuppetBotSession
from api.base import Context
from api.authenticator import CognitoAuthenticator
from api.triggers import RokgnitionTrigger
import logging
import click
import tempfile
import yaml
import os
import time 

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s')
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel('DEBUG')

@click.group()
@click.pass_context
def puppetbot(ctx):
    config = yaml.load(open('config.yaml'))
    ctx.obj = Context(config=config, logger=LOGGER)
    ctx.obj.tmp_dir = tempfile.mkdtemp()
    ctx.obj.request_audio_file = os.path.join(ctx.obj.tmp_dir, 'request.wav')
    ctx.obj.response_audio_file = os.path.join(ctx.obj.tmp_dir, 'response.mpeg')
    ctx.obj.authenticator = CognitoAuthenticator(ctx.obj)

@puppetbot.command()
@click.pass_obj
def start(ctx):
    bot_session = PuppetBotSession(ctx)
    trigger = RokgnitionTrigger(ctx)
    while True:
        trigger.wait_for_trigger()
        bot_session.start()

@click.group()
@click.pass_context
def audiobot(ctx):
    config = yaml.load(open('config.yaml'))
    ctx.obj = Context(config=config, logger=LOGGER)
    ctx.obj.tmp_dir = tempfile.mkdtemp()
    ctx.obj.request_audio_file = os.path.join(ctx.obj.tmp_dir, 'request.wav')
    ctx.obj.response_audio_file = os.path.join(ctx.obj.tmp_dir, 'response.mpeg')
    ctx.obj.authenticator = CognitoAuthenticator(ctx.obj)

@chatbot.command()
@click.pass_obj
def start(ctx):
    bot_session = AudioBotSession(ctx)
    bot_session.start()

cli = click.CommandCollection(sources=[puppetbot, cli2])

if __name__ == '__main__':
    cli()