import os
import sys
import logging
from ctypes import CDLL, c_bool, c_void_p

logger = logging.getLogger(__name__)

try:
    if sys.platform.startswith('win'):
        so = 'steam_api.dll'
    elif sys.platform.startswith('darwin'):
        so = 'libsteam_api.dylib'
    elif sys.platform.startswith('linux'):
        if sys.maxsize > 2**32:
            so = 'libsteam_api_64.so'
        else:
            so = 'libsteam_api.so'
    else:
        logger.error('Unsupported operating system')
        raise EnvironmentError('Unsupported operating system')
    libpath = os.path.join(os.path.dirname(__file__), 'libs', so)
    logger.debug('Looking for libsteam in "{}"'.format(libpath))
    # Load the library
    api = CDLL(libpath)
    # Define return typed of "exported" functions
    api.SteamAPI_IsSteamRunning.restype = c_bool
    api.SteamAPI_Init.restype = c_bool
    api.SteamAPI_Shutdown.restype = c_void_p
except Exception as e:
    logger.exception('Loading steam library failed')
    print('Loading steam library failed: {}'.format(e))
    raise

SteamAPI_Init = api.SteamAPI_Init
IsSteamRunning = api.SteamAPI_IsSteamRunning
SteamAPI_Shutdown = api.SteamAPI_Shutdown
