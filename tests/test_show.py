#!/usr/bin/env python3 

import sys
import os
import unittest
import requests

NEW_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.insert(0, NEW_PATH)
import npr
import npr.show

class TestNPRShow(unittest.TestCase):

    def setUp(self):
        # Print out name of method
        sys.stdout.write("\nRunning test '%s'..." % self._testMethodName)
        sys.stdout.flush()

        # Let's stock some data for the unittest obj...
        self.show = npr.show.Show()


    def test_fetch_feeds(self):
        r = requests.get(self.show.feed)
        self.assertTrue(r.ok)

    def ztest_find_mp3s(self):
        mp3s = self.show.mp3s
        for m in mp3s:
            r = requests.head(m)
            self.assertTrue(r.ok)

    def test_find_episodes(self):
        episodes = self.show.episodes
        for e in episodes:
            print(e)

    def ztest_next_track(self):
        mp3s = self.show.mp3s
        for i in range(1, 10): 
            print(self.show.next_track())


if __name__ == '__main__':
    unittest.main()
