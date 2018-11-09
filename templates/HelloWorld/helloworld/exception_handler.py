import os
import logging
import skygear
from skygear.error import SkygearException
from raven import Client as RavenClient

logger = logging.getLogger(__name__)

DEBUG_MODE = os.getenv('DEV_MODE', 'false') == 'true'

SENTRY_DNS = os.getenv('SENTRY_DNS', '')
raven_client = None
if SENTRY_DNS:
    raven_client = RavenClient(SENTRY_DNS)


def includeme():
    @skygear.exception_handler(Exception)
    def exception_handler(e):
        logger.error('Unexpected exception: ', exc_info=True)
        if raven_client:
            raven_client.captureException()
        if DEBUG_MODE:
            return e
        return SkygearException('Unexpected error')

    @skygear.exception_handler(SkygearException)
    def skygear_exception_handler(e):
        logger.error('SkygearException: ', exc_info=True)
        return e
