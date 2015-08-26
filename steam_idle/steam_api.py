import os
import sys
from ctypes import CDLL, c_bool, c_void_p

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
        raise EnvironmentError('Unsupported operating system')
    # Load the library
    api = CDLL(os.path.join(os.path.dirname(__file__), 'libs', so))
    # Define return typed of "exported" functions
    api.SteamAPI_IsSteamRunning.restype = c_bool
    api.SteamAPI_Init.restype = c_bool
    api.SteamAPI_Shutdown.restype = c_void_p
except Exception as e:
    print('Loading steam library failed: {}'.format(e))
    raise

SteamAPI_Init = api.SteamAPI_Init
IsSteamRunning = api.SteamAPI_IsSteamRunning
SteamAPI_Shutdown = api.SteamAPI_Shutdown
