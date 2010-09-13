import wsgiref.handlers
import os
import xml.dom.minidom
import feedparser
import datetime
import time
from BeautifulSoup import BeautifulSoup, Tag, NavigableString, BeautifulStoneSoup
import re

from operator import attrgetter
from time import strftime, strptime, gmtime
from xml.dom.minidom import Node
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.api import urlfetch
from google.appengine.api import images

class Account(db.Expando):
    user = db.UserProperty()
    
class Entry:
    def __init__(self=None, title=None, link=None, timestamp=None, img=None, content=None,
                 author = None, tags=None, service=None):
        self.title = title
        self.link = link
        self.content = content
        self.service = service
        self.timestamp = timestamp
        self.img = img
        self.author = author
        self.tags = tags
        
    def printTime(self):
        return strftime('%B %d,%Y at %I:%M:%S %p',self.timestamp)            

def images_from_html(html):
    soup = BeautifulSoup(html)
    tags = soup.findAll('img')
    # for img in images_from_html():
    # print img['src']
    return tags

def remove_html_tags(data):
    p = re.compile(r'<.*?>')
    return p.sub('', data)

class GenericFeed:
    def __init__(self, url, name):
        self.url = url
        self.name = name
    def entries(self):
        result = urlfetch.fetch(self.url)
        updates = []
        if result.status_code == 200:
            feed = feedparser.parse(result.content)
            for entry in feed['entries']:
                x = Entry()
                x.service = self.name
                x.title = entry['title']
                x.link = entry['link']
                x.author = entry['author']
                x.tags = entry['tags']
                x.summary = remove_html_tags(entry['summary'])
                addr = None
                try:
                    if entry.summary:
                        x.content = entry.summary
                        try:
                            imgs = images_from_html(x.content)
                            for img in imgs:
                                x.img = img['src']
                                if x.img != None:
                                    break
                        except:
                            print 'No image header'
                except:
                    x.content = entry['title']
                    
                if x.img == None:
                    continue
                
                x.timestamp = entry.updated_parsed
                updates.append(x)
        return updates          

class MainPage(webapp.RequestHandler):
  def get(self):

    url_linktext = 'nope'

    services = []
    services.append("http://del.icio.us/rss/no3z")
    services.append("http://www.youtube.com/rss/user/no3productionz/videos.rss")
    services.append("http://vigilantcitizen.com/?feed=rss2")
    services.append("http://documentaryheaven.com/feed/")
    
    updates = []
    for service in services:
        url = service
        feed = GenericFeed(url, service)
        updates.extend(feed.entries())
    
    updates.sort(key=attrgetter('timestamp'), reverse=True)

    template_values = {
      'updates': updates,
      'url': url,
      'url_linktext': url_linktext,
      }

    path = os.path.join(os.path.dirname(__file__), 'index.html')
    self.response.out.write(template.render(path, template_values))


def main():
  application = webapp.WSGIApplication(
                                       [('/', MainPage)],
                                        debug=True)
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
  main()