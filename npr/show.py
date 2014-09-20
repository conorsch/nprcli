#!/usr/bin/env python3
import requests
import arrow
import sys
import os
import subprocess
import signal
from bs4 import BeautifulSoup
import xmltodict

from . import utils
from .utils import lazyproperty


class Show(object):

    def __init__(self, *args, **kwargs):
        self.feed = kwargs.get('feed', self.find_todays_show())
        self.program = kwargs.get('program', None)

    def feeds(self):
        return {
            'morning_edition': 'http://www.npr.org/rss/rss.php?id=3',
            'weekend_edition_sunday': 'http://www.npr.org/rss/rss.php?id=10',
            'weekend_edition_saturday': 'http://www.npr.org/rss/rss.php?id=7',
        }

    @lazyproperty
    def _stew(self):
        r = requests.get(self.feed)
        if not r.ok:
            raise Exception("Could not retrieve URL. Check internet connection")
        return xmltodict.parse(r.content)['rss']['channel']

    @lazyproperty
    def date(self):
        return self._stew['lastBuildDate'].strip()

    @lazyproperty
    def title(self):
        return self._stew['title'].strip()

    @lazyproperty
    def articles(self):
        return [a['link'] for a in self._stew['item']]

    @lazyproperty
    def episodes(self):
        articles = self.articles
        episodes = [Episode(a, program=self.title) for a in articles]
        return episodes

    def find_todays_show(self):
        today = arrow.now().format('dddd')
        feeds = self.feeds()

        if today == 'Saturday':
            feed = feeds['weekend_edition_saturday']
        elif today == 'Sunday':
            feed = feeds['weekend_edition_sunday']
        else:
            feed = feeds['morning_edition']
        return feed

    def __str__(self):
        return "{} ({})".format(self.title, self.date)

class Episode(object):

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
        return self._soup.find('a', attrs={'class': 'download'}, href=True)['href'].strip()

    @lazyproperty
    def program(self):
        return self._soup.find('a', attrs={'class': 'program'}).getText().strip()

    @lazyproperty
    def date(self):
        return self._soup.find('span', attrs={'class': 'date'}).getText().strip()

    def __str__(self):
        return "{0} ({1}) - {2}".format(self.program, self.date, self.title)

class Player(object):

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
        if not episode:
            self.next_track()
        self.now_playing = episode

        cmd = ['/usr/bin/mplayer', '-noconsolecontrols', '-cache-min', '20', episode.mp3]

        FNULL = open(os.devnull, 'w')
        self.kill()
        self.pid = subprocess.Popen(cmd, stdout=FNULL, stderr=FNULL).pid

        self.pretty_info()
        utils.listen_for_keypress(self.keybindings)
        
    @lazyproperty
    def playlist(self):
        return self.show.episodes

    def pretty_info(self):
        if self.now_playing:
            msg = "\n - '{e.title}'".format(e=self.now_playing)
            print(msg, end='')

    def kill(self, exit=None):
        if self.pid:
            os.kill(self.pid, signal.SIGTERM)
            sys.stdout.write("")
            sys.stdout.flush()

    def quit(self):
        self.kill()
        print("\nExit")
        os.system('stty sane')
        sys.exit(0)

    def next_track(self):
        next_item = utils.get_next_item(self.playlist, self.now_playing)
        self.now_playing = next_item
        self.play(next_item)

    def previous_track(self):
        previous_item = utils.get_previous_item(self.playlist, self.now_playing)
        self.now_playing = previous_item
        self.play(previous_item)

