#!/usr/bin/env python3
import feedparser
import requests
import arrow
import sys
import os
import subprocess
import signal

from BeautifulSoup import BeautifulSoup
from audioread import audio_open
from .utils import lazyproperty, get_next_item, get_previous_item, listen_for_keypress


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
    def _raw_feed(self):
        d = feedparser.parse(self.feed)
        if not d.entries:
            raise Exception("Could not retrieve RSS feed. Check internet connection.")
        return d

    @lazyproperty
    def date(self):
        return self._raw_feed['feed']['updated']

    @lazyproperty
    def title(self):
        return self._raw_feed['feed']['title']

    @lazyproperty
    def title(self):
        return self._raw_feed['feed']['title']
    @lazyproperty
    def articles(self):
        return [e.link for e in self._raw_feed.entries]

    @lazyproperty
    def episodes(self):
        articles = self.articles
        episodes = [Episode(a, program=self.title) for a in articles]
        return episodes

    def find_todays_show(self):
        now = arrow.now()
        today = now.format('dddd')
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
        return BeautifulSoup(r.content, convertEntities=BeautifulSoup.HTML_ENTITIES)

    @lazyproperty
    def title(self):
        return self._soup.find('div', attrs={'class': 'storytitle'}).getText()

    @lazyproperty
    def mp3(self):
        return self._soup.find('a', attrs={'class': 'download'}, href=True)['href']

    @lazyproperty
    def program(self):
        return self._soup.find('a', attrs={'class': 'program'}).getText()

    @lazyproperty
    def date(self):
        return self._soup.find('span', attrs={'class': 'date'}).getText()

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

    def play(self, episode=None):
        if not episode:
            self.next_track()
        self.now_playing = episode

        cmd = ['/usr/bin/mplayer', '-cache-min', '20', episode.mp3]
        self.kill()
        self.pid = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE).pid

        self.pretty_info()
        listen_for_keypress(self.keybindings)
        
    @lazyproperty
    def playlist(self):
        return self.show.episodes

    def pretty_info(self):
        if self.now_playing:
            msg = "{e.title}".format(e=self.now_playing)
            sys.stdout.write(msg+"\r")

    def kill(self, exit=None):
        if self.pid:
            os.kill(self.pid, signal.SIGTERM)
            sys.stdout.write("")
            sys.stdout.flush()

    def quit(self):
        self.kill()
        sys.stdout.write("\nExit.\n")
        sys.stdout.flush()
        sys.exit(0)

    def next_track(self):
        next_item = get_next_item(self.playlist, self.now_playing)
        self.now_playing = next_item
        self.play(next_item)

    def previous_track(self):
        previous_item = get_previous_item(self.playlist, self.now_playing)
        self.now_playing = previous_item
        self.play(previous_item)

