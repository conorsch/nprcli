# -*- coding: utf-8 -*-
import sys, os, subprocess, signal

import requests
import arrow
from bs4 import BeautifulSoup
import xmltodict

from . import utils
from .utils import lazyproperty
from .exceptions import AudioNotAvailable


class Show(object):
    """Represents a collection of content from NPR, e.g. Morning Edition."""

    def __init__(self, *args, **kwargs):
        self.feeds = {
            'morning_edition': 'http://www.npr.org/rss/rss.php?id=3',
            'weekend_edition_sunday': 'http://www.npr.org/rss/rss.php?id=10',
            'weekend_edition_saturday': 'http://www.npr.org/rss/rss.php?id=7',
        }
        self.program = kwargs.get('program', None)
        self.feed = kwargs.get('feed', self.find_todays_show())

    @lazyproperty
    def _raw_feed(self):
        r = requests.get(self.feed)
        if not r.ok:
            raise Exception("Could not retrieve URL. Check internet connection")
        return xmltodict.parse(r.content)['rss']['channel']

    @lazyproperty
    def date(self):
        return self._raw_feed['lastBuildDate'].strip()

    @lazyproperty
    def title(self):
        return self._raw_feed['title'].strip()

    @lazyproperty
    def articles(self):
        return [a['link'] for a in self._raw_feed['item']]

    @lazyproperty
    def episodes(self):
        articles = self.articles
        episodes = [Episode(a, program=self.title) for a in articles]
        return episodes

    def find_todays_show(self):
        """Finds most recent Show available now."""
        today = arrow.now().format('dddd')

        if today == 'Saturday':
            feed = self.feeds['weekend_edition_saturday']
        elif today == 'Sunday':
            feed = self.feeds['weekend_edition_sunday']
        else:
            feed = self.feeds['morning_edition']
        return feed

    def __str__(self):
        return "{} ({})".format(self.title, self.date)

class Episode(object):
    """Represents a single audio story from an NPR show."""

    def __init__(self, url, *args, **kwargs):
        self.url = url

    @lazyproperty
    def _soup(self):
        r = requests.get(self.url)
        if not r.ok:
            raise Exception("Could not retrieve URL. Check internet connection")
        return BeautifulSoup(r.content)

    @lazyproperty
    def title(self):
        return self._soup.find('div', attrs={'class': 'storytitle'}).getText().strip()

    @lazyproperty
    def mp3(self):
        try:
            url = self._soup.find('a', attrs={'class': 'download'}, href=True)['href'].strip()
        except TypeError:
            raise AudioNotAvailable
        return url
    @lazyproperty
    def program(self):
        return self._soup.find('a', attrs={'class': 'program'}).getText().strip()

    @lazyproperty
    def date(self):
        return self._soup.find('span', attrs={'class': 'date'}).getText().strip()

    def __str__(self):
        return "{0} ({1}) - {2}".format(self.program, self.date, self.title)

class Player(object):
    """Handler for navigating audio files for a given show."""

    def __init__(self, *args, **kwargs):
        self.show = kwargs.get('show', Show())
        self.verbose = kwargs.get('verbose', True)

        if self.verbose:
            print("Now playing: {}".format(self.show))

        self.now_playing = None
        self.pid = None

        self.keybindings = {
            'n': self.next_track,
            'p': self.previous_track,
            'q': self.quit,
        }

        #signal.signal(signal.SIGINT, clean_up_terminal)

    def play(self, episode=None):
        """Start mplaying music with mplayer."""
        if not episode:
            self.next_track()
        self.now_playing = episode

        cmd = ['/usr/bin/mplayer', '-noconsolecontrols', '-cache-min', '20', episode.mp3]

        self.kill()
        self._proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.pid = self._proc.pid

        self.pretty_info()
        utils.listen_for_keypress(self.keybindings, self._proc)
        
    @lazyproperty
    def playlist(self):
        return self.show.episodes

    def pretty_info(self):
        """Prints title of currently playing story."""
        if self.now_playing:
            msg = "\n - {e.title}".format(e=self.now_playing)
            print(msg, end='')

    def kill(self, exit=None):
        """Kills currently running process of mplayer, if any."""
        if self.pid:
            try:
                os.kill(self.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass

            self.pid = None

    def quit(self):
        """Kills currently running process of mplayer, if any, then exits."""
        self.kill()
        print("\n\nExit")
        sys.exit(0)

    def next_track(self):
        """Plays next track in playlist."""
        next_item = utils.get_next_item(self.playlist, self.now_playing)
        self.now_playing = next_item
        self.play(next_item)

    def previous_track(self):
        """Plays previous track in playlist."""
        previous_item = utils.get_previous_item(self.playlist, self.now_playing)
        self.now_playing = previous_item
        self.play(previous_item)

