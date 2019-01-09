from google.appengine.ext import db

# User class with different user properties.
class User(db.Model):
	first_name = db.StringProperty(required=True)
	last_name = db.StringProperty(required=True)
	password = db.StringProperty(required=True)
	email = db.StringProperty(required=True)
	address = db.StringProperty(required=True)
	gender = db.StringProperty(required=False)
	birthday = db.StringProperty(required=False)
	interests = db.TextProperty(required=False)
	offensive_score = db.IntegerProperty(required=True)
	no_of_quotes = db.IntegerProperty(required=True)

# Posts class with different post properties.
class Posts(db.Model):
	quote = db.TextProperty(required=True)
	quote_posted_by = db.StringProperty(required=True)
	score = db.IntegerProperty(required=True)
	created = db.DateProperty(auto_now_add=True)