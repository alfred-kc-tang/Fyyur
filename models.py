from datetime import datetime

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_moment import Moment

# Initialize flask app.
def setup_app():
    app = Flask(__name__)
    moment = Moment(app)
    return app

# Connect app and database.
def setup_db(app):
    app.config.from_object('config')
    db = SQLAlchemy(app)
    return db

# Create model for venue.
def setup_venue_model(db):
    class Venue(db.Model):
        __tablename__ = 'Venue'

        id = db.Column(db.Integer, primary_key=True, nullable=False)
        name = db.Column(db.String, nullable=False)
        genres = db.Column(db.ARRAY(db.String(120)))
        address = db.Column(db.String(120))
        city = db.Column(db.String(120))
        state = db.Column(db.String(120))
        phone = db.Column(db.String(120))
        website = db.Column(db.String(500))
        image_link = db.Column(db.String(500))
        facebook_link = db.Column(db.String(120))
        seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
        seeking_description = db.Column(db.String(280))
        shows = db.relationship("Show", backref="venue")
    return Venue

# Create model for artist.
def setup_artist_model(db):
    class Artist(db.Model):
        __tablename__ = 'Artist'
    
        id = db.Column(db.Integer, primary_key=True, nullable=False)
        name = db.Column(db.String, nullable=False)
        genres = db.Column(db.String(120))
        city = db.Column(db.String(120))
        state = db.Column(db.String(120))
        phone = db.Column(db.String(120))
        website = db.Column(db.String(500))
        image_link = db.Column(db.String(500))
        facebook_link = db.Column(db.String(120))
        seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
        seeking_description = db.Column(db.String(280))
        shows = db.relationship("Show", backref="artist")
    return Artist

# Create model for show.
# The same pair of venue and artist could have multiple shows: many-to-many relationship.
# Association object instead of table is used for storing shows' starting times
def setup_show_model(db):
    class Show(db.Model):
        __tablename__ = 'Show'
        
        show_id = db.Column(db.Integer, primary_key=True)
        venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
        artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
        start_time = db.Column(db.DateTime, default=datetime.utcnow)
        venues = db.relationship("Venue", backref="show")
        artists = db.relationship("Artist", backref="show")
    return Show
