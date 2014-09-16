
from BeautifulSoup import BeautifulSoup
import requests

# Yanked from http://stackoverflow.com/a/3013910/140800
def lazyproperty(fn):
    attr_name = '_lazy_' + fn.__name__
    @property
    def _lazyproperty(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, fn(self))
        return getattr(self, attr_name)
    return _lazyproperty

def get_next_item(playlist, item):
    """Accepts dict playlist and optional current item, returns next item in playlist."""
    try:
        return playlist[playlist.index(item) + 1]
    except (IndexError, ValueError) as e:
        return playlist[0]

def get_previous_item(playlist, item):
    """Accepts dict playlist and optional current item, returns previous item in playlist."""
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
