import feedparser
import requests
from BeautifulSoup import BeautifulSoup

morningEdition = 'http://www.npr.org/rss/rss.php?id=3'

feed = morningEdition

d = feedparser.parse(feed)





def getArticles(feed):
    #    print d.feed.title
    return [e.link for e in d.entries]

def getMp3(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, convertEntities=BeautifulSoup.HTML_ENTITIES)
    m = soup.find('a', attrs={'class': 'download'}, href=True)
    mp3 = m.get('href')
    return mp3

urls = getArticles(morningEdition)
u = urls[0]

mp3s = [getMp3(u) for u in urls]
for m in mp3s:
    print m

