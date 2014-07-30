#!/usr/bin/python2.5
__author__ = 'no3z'

import cgi
import os

from google.appengine.api import images
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.api import urlfetch

import wsgiref.handlers
import random

template.register_template_library('templatetags.basetags')

#------------------------------------------------------------------------------
# Class definitions
#------------------------------------------------------------------------------

#An album class
class Album(db.Model):
  name = db.StringProperty()
  creator = db.UserProperty()

#A picture class
class Picture(db.Model):
  """
    submitter: Google Account of the person who submitted the picture
    submitted_date: DateTime the picture was submitted
    title: sanitized, user entered title for the picture
    caption: sanitized, user entered caption for the picture
    album: reference to album the picture is in
    tags: a StringListProperty of tags for the picture
    data: data for the original picture, converted into png format
    thumbnail_data: png format data for the thumbnail for this picture
  """
  submitter = db.UserProperty()
  submitted_date = db.DateTimeProperty(auto_now_add=True)
  title = db.StringProperty()
  caption = db.TextProperty()
  album = db.ReferenceProperty(Album, collection_name='pictures')
  tags = db.StringListProperty()
  data = db.BlobProperty()
  thumbnail_data = db.BlobProperty()
  url = db.StringProperty()
  comment = db.TextProperty()
  author = db.StringProperty()
  rand = db.FloatProperty()
  osize = db.BooleanProperty()
  portfolio = db.StringProperty()
  
#------------------------------------------------------------------------------
#Funtions
#------------------------------------------------------------------------------

class RequestBaseHandler(webapp.RequestHandler):
  def template_path(self, filename):    
    return os.path.join(os.path.dirname(__file__), filename)

  def render_to_response(self, filename, template_args):    
    template_args.setdefault('current_uri', self.request.uri)
    self.response.out.write(
        template.render(self.template_path(filename), template_args)
    )


#------------------------------------------------------------------------------        
    
class ListAlbums(RequestBaseHandler):  

  def get(self):
    albums = Album.all()
    self.render_to_response('html/list.html', {
        'albums': albums,
      })

#------------------------------------------------------------------------------

class CreateAlbum(RequestBaseHandler):
  def get(self):
    self.render_to_response('html/new.html', {})

  def post(self):
    Album(name=cgi.escape(self.request.get('albumname')),
          creator=users.get_current_user()).put()
    self.redirect('/list')

PICTURES_PER_ROW = 5

#------------------------------------------------------------------------------

class ViewAlbum(RequestBaseHandler):
  def get(self, album_key):
    album = db.get(album_key)
    pics = []
    num_results = 0

    for picture in album.pictures:
      if num_results % PICTURES_PER_ROW == 0:
        current_row = []
        pics.append(current_row)
      current_row.append(picture)
      num_results += 1

    self.render_to_response('html/album.html', {
        'num_results': num_results,
        'album_key': album.key(),
        'pics': pics,
        'album_name': album.name
      })

#------------------------------------------------------------------------------      
      
class ServeImage(webapp.RequestHandler):
  def get(self, display_type, pic_key):
    image = db.get(pic_key)

    if display_type == 'image':
      self.response.headers['Content-Type'] = 'image/png'
      self.response.out.write(image.data)
    elif display_type == 'thumbnail':
      self.response.headers['Content-Type'] = 'image/png'
      self.response.out.write(image.thumbnail_data)
    else:
      self.error(500)
      self.response.out.write('Couldn\'t determine what type of image to serve.')

#------------------------------------------------------------------------------

class ReturnRandomizedImages(RequestBaseHandler):
  def get(self):         
    pics = []
    pics = Picture.all()
    pics = Picture.all().filter('rand > ', random.random()).order('rand')
    self.render_to_response('html/index.html', {
        'updates': pics[:26],
      })

#------------------------------------------------------------------------------

class ReturnVideoAlbumImages(RequestBaseHandler):
  def get(self):       
    pics = []
    pics = Picture.all()
    pics.filter("portfolio =", "VIDEO")
    pics.order("-submitted_date")
    self.render_to_response('html/index.html', {
        'updates': pics[:26],
      })

#------------------------------------------------------------------------------

class ReturnLinksAlbumImages(RequestBaseHandler):
  def get(self):   
    pics = []
    pics = Picture.all()
    pics.filter("portfolio =", "LINKS")
    self.render_to_response('html/index.html', {
        'updates': pics[:26],
      })
    
#------------------------------------------------------------------------------

class ReturnAboutAlbumImages(RequestBaseHandler):
  def get(self):   
    pics = []
    pics = Picture.all()
    pics.filter("portfolio =", "ABOUT")
    self.render_to_response('html/index.html', {
        'updates': pics[:26],
      })
    
#------------------------------------------------------------------------------

class ShowImage(RequestBaseHandler):
  def get(self, pic_key):
    pic = db.get(pic_key)
    self.render_to_response('html/show_image.html', {
        'pic': pic,
        'image_key': pic.key(),
    })

  def post(self, pic_key):
    pic = db.get(pic_key)    
    if pic is None:
      self.error(400)
      self.response.out.write('Couldn\'t find specified pic')
    
    title = cgi.escape(self.request.get('title'))
    caption = cgi.escape(self.request.get('caption'))
    url = cgi.escape(self.request.get('url'))
    comment = cgi.escape(self.request.get('caption'))
    author = cgi.escape(self.request.get('author'))
    osize =   cgi.escape(self.request.get('osize'))    
    portfolio =   cgi.escape(self.request.get('portfolio')) 
    tags = cgi.escape(self.request.get('tags'))
    isdelete = cgi.escape(self.request.get('delete'))
    
    if isdelete:
        pic.delete()
        self.redirect('/list')
        return
    
    pic.title = title
    pic.caption = caption
    pic.comment = caption
    pic.author = author
    pic.url = url
    pic.portfolio = portfolio
    pic.osize = False
    if osize:
        pic.osize = True
        
    pic.put()
    
    self.redirect('/show_image/%s' % pic_key)
      

#------------------------------------------------------------------------------

class ImportRSSFeed(RequestBaseHandler):
  def get(self, album_key):
    album = db.get(album_key)
    self.render_to_response('rss.html', {
        'album_key': album.key(),
        'album_name': album.name
      })
        
  def post(self, album_key):    
    feed_name = cgi.escape(self.request.get('feed_name')) 

    album = db.get(album_key)
    if album is None:
      self.error(400)
      self.response.out.write('Couldn\'t find specified album')
      
    #feed = GenericFeed(feed_name,feed_name)
    
    updates = []
    updates.extend(feed.entries())
    
    for feed in updates:                
        img_data = db.Blob(urlfetch.Fetch(feed.img).content)
        if img_data == None:
            continue
        
        pic = db.Query(Picture)
        pic = Picture.all().filter('title=', feed.title)
        num = pic.count()
    
        if num == 0:
            try:
                img = images.Image(img_data)
                img.im_feeling_lucky()
                png_data = img.execute_transforms(images.PNG)
                img.resize(120,90)
                thumbnail_data = img.execute_transforms(images.PNG)
                Picture(submitter=users.get_current_user(),
                      title=feed.title,
                      comment=feed.summary,
                      album=album,
                      url=feed.link,
                      data=png_data,
                      caption=feed.summary[0:140],
                      author=feed.author,
                      rand = random.random(),
                      osize = False,
                      portfolio = album.name,
                      thumbnail_data=thumbnail_data).put()
                      
            except images.LargeImageError:
                self.error(400)
                self.response.out.write('Sorry, the image provided was too large for us to process.')
              
    self.redirect('/album/%s' % album.key())
        
#------------------------------------------------------------------------------

class UploadImageToAlbum(RequestBaseHandler):
  def get(self, album_key):
    album = db.get(album_key)
    self.render_to_response('upload.html', {
        'album_key': album.key(),
        'album_name': album.name
      })

  def post(self, album_key):    
    album = db.get(album_key)
    if album is None:
      self.error(400)
      self.response.out.write('Couldn\'t find specified album')

    title = cgi.escape(self.request.get('title'))
    caption = cgi.escape(self.request.get('caption'))
    url = cgi.escape(self.request.get('url'))
    comment = cgi.escape(self.request.get('caption'))
    caption = comment[0:144]
    author = cgi.escape(self.request.get('author'))
    tags = cgi.escape(self.request.get('tags')).split(',')
    tags = [tag.strip() for tag in tags]
    # Get the actual data for the picture
    img_data = self.request.POST.get('picfile').file.read()
    osize = cgi.escape(self.request.get('osize'))

    isosize = False
    if osize:
       isosize = True

    try:
      img = images.Image(img_data)
      img.im_feeling_lucky()
      png_data = img.execute_transforms(images.PNG)
      img.resize(60, 100)
      thumbnail_data = img.execute_transforms(images.PNG)
      Picture(submitter=users.get_current_user(),
              title=title,
              caption=caption,
              comment=comment,
              album=album,
              tags=tags,
              url=url,
              author=author,
              rand = random.random(),
              data=png_data,
              osize=isosize,
              portfolio=album.name,
              thumbnail_data=thumbnail_data).put()
                                    
      self.redirect('/album/%s' % album.key())
    except images.BadImageError:
      self.error(400)
      self.response.out.write(
          'Sorry, we had a problem processing the image provided.')
    except images.NotImageError:
      self.error(400)
      self.response.out.write(
          'Sorry, we don\'t recognize that image format.'
          'We can process JPEG, GIF, PNG, BMP, TIFF, and ICO files.')
    except images.LargeImageError:
      self.error(400)
      self.response.out.write(
          'Sorry, the image provided was too large for us to process.')



#------------------------------------------------------------------------------
# URI handler
#------------------------------------------------------------------------------

    
def main():
  url_map = [('/list', ListAlbums),
             ('/new', CreateAlbum),
             ('/album/([-\w]+)', ViewAlbum),
             ('/upload/([-\w]+)', UploadImageToAlbum),
             ('/rss/([-\w]+)', ImportRSSFeed),
             ('/show_image/([-\w]+)', ShowImage),
             ('/update/([-\w]+)', ShowImage),
             ('/(thumbnail|image)/([-\w]+)', ServeImage),
             ('/about', ReturnAboutAlbumImages),
             ('/links', ReturnLinksAlbumImages),
             ('/video', ReturnVideoAlbumImages),
             ('/', ReturnRandomizedImages)]
  
  application = webapp.WSGIApplication(url_map,debug=True)
  
  wsgiref.handlers.CGIHandler().run(application)

#------------------------------------------------------------------------------

if __name__ == '__main__':
  main()
