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

		


class Guestbook(webapp2.RequestHandler):
    def get(self):
    	#check for blank entry, maybe this works? it's a base
    	#blank_entry = self.request.get('') this is me guessing
    	#check for error message, this is from webcast, does it go here or under
    	#get on main?pretty sure here???
    	#error = self.request.get('error','')
    	#to test
    	#print '#####'
    	#print error
    	#print '#####'
        guestbook_name = self.request.get('guestbook_name',
                                          DEFAULT_GUESTBOOK_NAME)
        greetings_query = Greeting.query(
            ancestor=guestbook_key(guestbook_name)).order(-Greeting.date)
        posts_to_pull = 10 #added to fix magic number
        greetings = greetings_query.fetch(posts_to_pull)
        #greetings = greetings_query.fetch(10) 10 is a magic no no
        
        #self.render('index.html') from andy example hanlers line 59


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
        }

        template = jinja_env.get_template('index.html')#this is where error generated?or base?
        #from webcast
        #rendered_html = ('index.html') % (table,error) don't think this is necessary since using template
        self.response.write(template.render(template_values))




    def post(self):
    	guestbook_name = self.request.get('guestbook_name',
                                          DEFAULT_GUESTBOOK_NAME)
        greeting = Greeting(parent=guestbook_key(guestbook_name))

        if users.get_current_user():
            greeting.author = Author(
                    identity=users.get_current_user().user_id(),
                    email=users.get_current_user().email())

        greeting.content = self.request.get('content')
        #if greeting.content =="":
        	#blank_entry ='Oops, are you using an invisibility cloak?'
        #else:
        greeting.put()#indent this to blank entry

        query_params = {'guestbook_name': guestbook_name}
        self.redirect('/?' + urllib.urlencode(query_params))



		

app = webapp2.WSGIApplication([('/', MainPage),
							   ('/sign', Guestbook)
							   ],
							   debug=True)