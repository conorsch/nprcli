import termios, fcntl, sys, os
import requests
from bs4 import BeautifulSoup

def lazyproperty(fn):
    # Yanked from http://stackoverflow.com/a/3013910/140800
    attr_name = '_lazy_' + fn.__name__
    @property
    def _lazyproperty(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, fn(self))
        return getattr(self, attr_name)
    return _lazyproperty

def get_next_item(playlist, item):
    """Accepts playlist and optional current item, returns next item in playlist."""
    try:
        return playlist[playlist.index(item) + 1]
    except (IndexError, ValueError) as e:
        return playlist[0]

def get_previous_item(playlist, item):
    """Accepts playlist and optional current item, returns previous item in playlist."""
    try:
        return playlist[playlist.index(item) - 1]
    except (IndexError, ValueError) as e:
        return playlist[0]

def download_file(url):
    # Thanks http://stackoverflow.com/questions/16694907/how-to-download-large-file-in-python-with-requests-py
    print("Downloading URL: %s" % url)
    local_filename = url.split('/')[-1]
    r = requests.get(url, stream=True)
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024): 
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
                f.flush()
    return local_filename

def listen_for_keypress(dispatch_table):
    # Straight out of the docs: https://docs.python.org/2/faq/library.html#how-do-i-get-a-single-keypress-at-a-time
    fd = sys.stdin.fileno()

    oldterm = termios.tcgetattr(fd)
    newattr = termios.tcgetattr(fd)
    newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
    termios.tcsetattr(fd, termios.TCSANOW, newattr)

    oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)

    try:
        while 1:
            try:
                c = sys.stdin.read(1)
                f = dispatch_table[c]
                f()
            except IOError: pass
            except KeyError: pass
    finally:
        termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
        fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)

