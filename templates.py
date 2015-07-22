import os

import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
							   autoescape = True)

class Handler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)

	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))

#Guestbook code came from Google App Engine tutorial 
DEFAULT_GUESTBOOK_NAME = 'default_guestbook'

def guestbook_key(guestbook_name=DEFAULT_GUESTBOOK_NAME):
    """Constructs a Datastore key for a Guestbook entity.

    We use guestbook_name as the key.
    """
    return ndb.Key('Guestbook', guestbook_name)


class Author(ndb.Model):
    """Sub model for representing an author."""
    identity = ndb.StringProperty(indexed=False)
    email = ndb.StringProperty(indexed=False)


class Greeting(ndb.Model):
    """A main model for representing an individual Guestbook entry."""
    author = ndb.StructuredProperty(Author)
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)


class MainPage(Handler):
	def get(self):
		self.render("stage4.html")

		



class Guestbook(Handler):#  added try 5
    def get(self):
    	
    	error = self.request.get('no_text')

    	guestbook_name = self.request.get('guestbook_name',
                                          DEFAULT_GUESTBOOK_NAME)
        greetings_query = Greeting.query(
            ancestor=guestbook_key(guestbook_name)).order(-Greeting.date)
        posts_to_pull = 10 
        greetings = greetings_query.fetch(posts_to_pull)
        


        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        template_values = {
            'user': user,
            'greetings': greetings,
            'guestbook_name': urllib.quote_plus(guestbook_name),
            'url': url,
            'url_linktext': url_linktext,
            'no_text': error#added
        }

        #template = jinja_env.get_template('index.html') #this puts error in url
        self.render('index.html', **template_values) #add try 5 error still in url
        #self.response.write(template.render(template_values)) #this puts error in url
        



    def post(self):
    	no_text = ""
    	guestbook_name = self.request.get('guestbook_name',
                                          DEFAULT_GUESTBOOK_NAME)
        greeting = Greeting(parent=guestbook_key(guestbook_name))

        if users.get_current_user():
            greeting.author = Author(
                    identity=users.get_current_user().user_id(),
                    email=users.get_current_user().email())

        greeting.content = self.request.get('content')
        if greeting.content =="":#added
        	no_text ='Oops, are you using an invisibility cloak?'#added.  do i need a redirect?
        else:#added
        	greeting.put()#unindent for fall back

        query_params = {'guestbook_name': guestbook_name, 'no_text': no_text}#added no_text
        self.redirect('/?' + urllib.urlencode(query_params))



		

app = webapp2.WSGIApplication([('/', MainPage),
							   ('/sign', Guestbook)
							   ],
							   debug=True)