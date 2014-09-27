# -*- coding: utf-8 -*-

class NetworkError(Exception):
    def __init__(self):
        pass

    def __str__(self):
        return "Could not retrieve articles. Check network connection."

class AudioNotAvailable(Exception):
    def __init__(self):
        pass

    def __str__(self):
        return "Audio is not yet available for this show."
