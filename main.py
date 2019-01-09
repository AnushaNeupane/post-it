import database
import hashlib
import helper
import hmac
import jinja2
import os
import webapp2

from google.appengine.api import mail
from google.appengine.ext import db

# Concatenates this secret string to cookies to make it more secure
secret = "njdkasndlkasndlasdlknadlka" 

# Joins the path of current direcotry with template
temp_dir = os.path.join(os.path.dirname(__file__),'templates')

# Loads the file in jinja environment from temp_dir path
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(temp_dir), autoescape=True)

def render_str(template,**params):
    t = jinja_env.get_template(template)
    return t.render(params)

# Hashes the password.
def hash_str(s):            
    return hashlib.sha224(s).hexdigest()

def make_secure_val(val):
    return "%s|%s" % (val, hmac.new(secret, val).hexdigest())

def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val

# Handler class
class Handler(webapp2.RequestHandler):
    def __init__(self, request=None, response=None):
        super(Handler, self).__init__(request=None, response=None)
        self.request = request
        self.response = response
        uid = self.read_secure_cookie('user_id')
        self.loged_user =  uid and database.User.get_by_id(int(uid)) 

    # Renders strings.
    def write(self,*a,**kw):
        self.response.out.write(*a,**kw)

    # Renders the string with <html></html> tags
    def render_str(self, template, **params):
        params['user'] = self.loged_user
        t = jinja_env.get_template(template)
        return t.render(params)

    # Reads the file and passes to render_str as parameter.
    def render(self,template,**kw):
        self.write(self.render_str(template,**kw))

    # Sets the cookie.
    def set_secure_cookie(self, name, val):
        cookie_val = str(make_secure_val(val))
        self.response.headers.add_header('Set-Cookie','%s=%s; Path=/'%(name, cookie_val))

    # Reads the hashes cookie form the browser.
    def read_secure_cookie(self,name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    # Logs the user in and sets cookies.
    def login(self,user):
        self.set_secure_cookie('user_id',str(user.key().id()))

    # Clears all the cookies after log out.
    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

# All the classes below inherits from the Handler class.
class MainHandler(Handler):
    def get(self):
        # Get current logged user and render main.html
        user = self.loged_user
        self.render("main.html", logged_user = user)
"""
    Renders signup.html and get information from the post and stores 
    in database.
"""
class SignupHandler(Handler):
    def get(self):
        user = self.loged_user
        self.render("signup.html", logged_user = user)

    def post(self):
        # Get information from the signup forms.
        first_name = self.request.get('firstname')
        last_name = self.request.get('lastname')
        email = self.request.get('email')
        password = self.request.get('password')
        address = self.request.get('address')
        gender = self.request.get('gender')
        birthday = self.request.get('birthday')
        interests = self.request.get('interests')

        # Use mail API to check if the email is valid.
        if not mail.is_email_valid(email):
            error = "The provided email is not valid."
            self.render("signup.html", error = error)

        # Check if the email is in user database.
        user = database.User.all().filter('email =', email).get()
        if user:
            error = "You have already signed up. Please go to login page."
            self.render("signup.html", error = error)
        # Store new user in the database and send email to the user.
        else:
            self.send_signup(email, first_name)
            database.User(first_name = first_name, last_name=last_name, email = email, 
                password = hash_str(password.strip()), address = address, gender = gender,
                birthday = birthday, interests = interests, offensive_score = 0,
                no_of_quotes = 0).put()
            self.redirect('/login')

    # Sends signup email.
    def send_signup(self, email, first_name):
        mail.send_mail(sender='neupaneanushaa@gmail.com',
                       to = email,
                       subject = "Welcome to Post-it",
                       body = '''Dear ''' + first_name + ''',''' +'''
                Thank you for signing up for Post-it. Please visit our page
                 for inspirational quotes.

        Post-it
        https://post-it-219419.appspot.com/''')  

"""
    Renders login.html and get information from the forms and checks 
    if the email and password are correct.
"""
class LoginHandler(Handler):
    def get(self):
        usr = self.loged_user
        self.render("login.html", logged_user = usr)

    def post(self):
        email = self.request.get('email')
        password = self.request.get('password')

        if email and password:
            # Check if the email exists in database.
            user = database.User.all().filter('email =', email).get()
            # If user exists, check password.
            if user:
                if hash_str(password) == user.password:
                    self.login(user)
                    self.redirect('/')
                else:
                    error = "Incorrect Password."
                    self.render("login.html", error=error)
            else:
                error = "User not found."
                self.render("login.html", error=error)
        else:
            error = "Required email or the password is not provided."
            self.render("login.html", error=error)
            self.redirect('/')

"""
    Clears the cookies and redirects to the main page.
"""
class LogoutHandler(Handler):
    def post(self):
        self.logout()
        self.redirect('/')

"""
    Renders the post.html page and gets the post information,
    checks for the standard, censors the offensive words,
    and stores in the database.
"""
class PostHandler(Handler):
    def get(self):
        user = self.loged_user
        self.render("post.html", logged_user = user)

    def post(self):
        user = self.loged_user
        # Get quote from the front end
        quote = self.request.get('quote')
        if quote == "":
            error = "You cannot leave the quote blank."
            self.render("post.html", logged_user = user, error = error)
        else:
            # Check if the quote is within Post-it's standard.
            if helper.check_standard(quote):
                # Censor offensive words.
                updated_quote = helper.censor(quote)
                # Get offensive score to store in User database.
                negative_score = helper.get_offensive_score(quote)
                if user:
                    first_name = user.first_name
                    last_name = user.last_name
                    # Save first and last name as posted by for posts.
                    posted_by = first_name + ' ' + last_name
                    email = user.email
                    # Send email to the user with the quote.
                    self.send_email(email, first_name, quote)
                    self.loged_user.offensive_score += negative_score
                    self.loged_user.no_of_quotes += 1
                    self.loged_user.put()
                # If user is not logged in, save posted_by as Sneaky Ninja.
                else:
                    posted_by = "Sneaky Ninja"

                # Store the post in the database.
                database.Posts(quote = updated_quote, 
                    score = negative_score, quote_posted_by = posted_by).put()
                self.redirect('/quotes')
            else:
                error = "Your quote is too offensive for our standard."
                self.render("post.html", logged_user = user, error = error)

    # Sends email after posting quotes.
    def send_email(self, email, first_name, quote):
        mail.send_mail(sender='neupaneanushaa@gmail.com',
                       to = email,
                       subject = "Posted on Post-It",
                       body = '''Dear ''' + first_name + ''',''' +'''
                
                Thank you for posting a quote on Post-It. 
                Here is your quote: ''' + quote + '''

        Post-it
        https://post-it-219419.appspot.com/''')

"""
    Renders quotes.html and displays all the quotes.
"""
class DisplayHandler(Handler):
    # Display the quotes.
    def get(self):
        usr = self.loged_user
        # Query the database for all teh posts.
        posts = db.GqlQuery("SELECT * FROM Posts "
                                "ORDER BY created DESC ")
        self.render("quotes.html", logged_user = usr, posts = posts)

"""
    Renders myquotes.html and shows information about all the
    posts made by the user.
"""
class MyQuotesHandler(Handler):
    # Display the quotes.
    def get(self):
        usr = self.loged_user
        name = usr.first_name + ' ' + usr.last_name
        posts = db.GqlQuery("SELECT * FROM Posts "
                                "ORDER BY created DESC ")
        # From posts, filter out posts posted by the current logged user.
        quotes = []
        for post in posts:
            if post.quote_posted_by == name:
                quote = post.quote
                quotes.append(quote)
        self.render("myquotes.html", logged_user = usr, quotes = quotes)

"""
    Renders frequency.html and shows information about the words in the
    quotes and their frequencies.
"""
class FrequencyHandler(Handler):
    # Display the frequency of words in all the quotes.
    def get(self):
        usr = self.loged_user
        posts = db.GqlQuery("SELECT * FROM Posts "
                                "ORDER BY created DESC ")

        # Call frequency function from helper to get the frequency of words.
        frequencies = helper.frequency(posts)
        self.render("frequency.html", logged_user = usr, frequencies = frequencies)

"""
    Renders profile.html with information about the user.
"""
class MyProfileHandler(Handler):
    # Load my profile page with information about logged user.
    def get(self):
        usr = self.loged_user
        self.render("profile.html", logged_user=usr)

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/signup', SignupHandler),
    ('/login', LoginHandler),
    ('/logout', LogoutHandler),
    ('/post', PostHandler),
    ('/quotes', DisplayHandler),
    ('/myquotes', MyQuotesHandler),
    ('/frequency', FrequencyHandler),
    ('/myprofile', MyProfileHandler),
 
], debug=True)