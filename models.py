from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import ARRAY

db = SQLAlchemy()



###############################
########## MODELS ############
###############################

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable = False)
    city = db.Column(db.String(120), nullable = False)
    state = db.Column(db.String(120), nullable = False)
    address = db.Column(db.String(120), nullable = False)
    phone = db.Column(db.String(120), nullable = False)
    genres = db.Column(ARRAY(db.String), nullable = False)
    website = db.Column(db.String(500), nullable = True)
    image_link = db.Column(db.String(500), nullable = True)
    facebook_link = db.Column(db.String(120), nullable = True)
    seeking_talent = db.Column(db.Boolean, default = False, nullable = False)
    seeking_description = db.Column(db.String(200), nullable = True)
    show = db.relationship('Show', backref=db.backref('venue'), lazy=True )

    def __repr__(self):
       return f'<Venue ID: {self.id} Venue Name: {self.name} \n Venue Address: {self.address} {self.city}, {self.state} \n Venue Phone: {self.phone}, Venue Website: {self.website}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(100), nullable=False)
    genres = db.Column(ARRAY(db.String()), nullable=False)
    website = db.Column(db.String(500), nullable=True)
    image_link = db.Column(db.String(500), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=True)
    seeking_venue = db.Column(db.Boolean, default = False, nullable = False)
    seeking_description = db.Column(db.String(200), nullable = True)
    show = db.relationship('Show', backref=db.backref('artist'), lazy=True)

    def __repr__(self):
       return f'<Artist ID: {self.id} Artist Name: {self.name} \n Artist Contact: {self.phone} {self.city}, {self.state}>'

class Show(db.Model):
  __tablename__ = 'show'
  id = db.Column(db.Integer, primary_key = True)
  venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable = False)
  artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable = False)
  start_time = db.Column(db.DateTime(timezone=True), nullable = False)

