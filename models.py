#------------------------------------------------------------------------------------------------------------#
# Imports
#------------------------------------------------------------------------------------------------------------#

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Define db object
db = SQLAlchemy()

#------------------------------------------------------------------------------------------------------------#
# Models.
#------------------------------------------------------------------------------------------------------------#

# Many to many relationship -- Association table
#------------------------------------------------------------------------------------------------------------#

class Show(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True)
    artist_id =  db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
      return f'<Show {self.id}, Artist {self.artist_id}, Venue {self.venue_id}>'


# Venue Model
#------------------------------------------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    # Missing model properties
    genres = db.Column('genres', db.ARRAY(db.String()), nullable=False)
    website_link = db.Column(db.String(400))
    seeking_artist =db.Column(db.Boolean, default=True)
    seeking_description = db.Column(db.String(400), default='We are searching for a new artist')
    
    # To generate a new relationship
    shows = db.relationship('Show', backref='venue', lazy='joined', cascade="all, delete")

    def __repr__(self):
      return f'<Venue {self.id} name: {self.name}>'

# Artist Model
#------------------------------------------------------------------------------------------------------------#

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column('genres', db.ARRAY(db.String), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    # Missing model properties
    website_link = db.Column(db.String(400))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(400), default='Searching for shows to perform')

    # Generate a new relationship
    shows = db.relationship('Show', backref='artist', lazy='joined', cascade="all, delete")

    def __repr__(self):
      return f'<Artist {self.id} name: {self.name}>'