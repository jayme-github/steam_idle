import os
import sys
import logging
from ctypes import CDLL, c_bool, c_void_p

logger = logging.getLogger(__name__)
def module_path():
    if hasattr(sys, 'frozen'):
        fpath = sys.executable
    else:
        fpath = __file__
    return os.path.dirname(fpath)

try:
    arch = ''
    if sys.maxsize > 2**32:
        arch = '64'

    if sys.platform.startswith('win'):
        so = 'steam_api%s.dll' %arch
    elif sys.platform.startswith('linux'):
        so = 'libsteam_api%s.so' %arch
    elif sys.platform.startswith('darwin'):
        so = 'libsteam_api.dylib'
    else:
        logger.error('Unsupported operating system')
        raise EnvironmentError('Unsupported operating system')
    libpath = os.path.join(module_path(), 'libs', so)
    logger.debug('Looking for libsteam in "%s"', libpath)
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
