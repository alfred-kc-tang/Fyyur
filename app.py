#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from datetime import datetime
import json
import dateutil.parser

import babel
from flask import render_template, request, Response, flash, redirect, url_for, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

import logging
from logging import Formatter, FileHandler

from forms import *
from models import setup_app, setup_db, setup_venue_model, setup_artist_model, setup_show_model

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
app = setup_app()
db = setup_db(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
Venue = setup_venue_model(db)
Artist = setup_artist_model(db)
Show = setup_show_model(db)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  unique_cities = []
  unique_states = []
  area = {}
  data = []
  venues = Venue.query.all()
  # Group the venues into cities and states.
  for venue in venues:
    num_upcoming_shows = 0
    if (venue.city not in unique_cities) & (venue.city not in unique_states):
      unique_cities.append(venue.city)
      unique_states.append(venue.state)
      for show in venue.show:
        if show.start_time > datetime.now():
          num_upcoming_shows += 1
      area[venue.city + ', ' + venue.state] = [{"id": venue.id, 
                                                "name": venue.name,
                                                "num_upcoming_shows": num_upcoming_shows}]
    else:
      area[venue.city + ', ' + venue.state].append({"id": venue.id, 
                                                    "name": venue.name,
                                                    "num_upcoming_shows": num_upcoming_shows})
  for key in area:
    data.append({"city": key[:-4],
                 "state": key[-2:],
                 "venues": area[key]})
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  data = []
  search_term = request.form.get('search_term')
  # Case-insensitive search terms
  results = Venue.query.filter(Venue.name.ilike("%" + search_term + "%")).all()
  # Count the number of upcoming shows for each venue returned
  for result in results:
    num_upcoming_shows = 0
    for show in result.show:
      if show.start_time > datetime.now():
        num_upcoming_shows += 1
    data.append({"id": result.id, "name": result.name, "num_upcoming_shows": num_upcoming_shows})
  response = {
    "count": len(results),
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, 
    search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get(venue_id)

  upcoming_shows = []
  past_shows = []

  # Filter Show table by artist_id and join its filtered version with Venue table
  upcoming_shows_query = Show.query.filter_by(venue_id=venue_id).filter(
    Show.start_time > datetime.now()).join(Artist, Show.artist_id == Artist.id).add_columns(
      Artist.id, Artist.name, Artist.image_link, Show.start_time).all()
  past_shows_query = Show.query.filter_by(venue_id=venue_id).filter(
    Show.start_time <= datetime.now()).join(Artist, Show.artist_id == Artist.id).add_columns(
      Artist.id, Artist.name, Artist.image_link, Show.start_time).all()

  for row in upcoming_shows_query:
    upcoming_shows.append({
      "artist_id": row[1],
      "artist_name": row[2],
      "artist_image_link": row[3],
      "start_time": str(row[4])
    })
  
  for row in past_shows_query:
    past_shows.append({
      "artist_id": row[1],
      "artist_name": row[2],
      "artist_image_link": row[3],
      "start_time": str(row[4])
    })

  # An alternative without using joined query:
  # for show in venue.show:
  #     if show.start_time > datetime.now():
  #       upcoming_shows.append({
  #         "artist_id": show.artist_id,
  #         "artist_name": show.artist.name,
  #         "artist_image_link": show.artist.image_link,
  #         "start_time": str(show.start_time)
  #       })
  #     else:
  #       past_shows.append({
  #         "artist_id": show.artist_id,
  #         "artist_name": show.artist.name,
  #         "artist_image_link": show.artist.image_link,
  #         "start_time": str(show.start_time)
  #       })

  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
  }
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  try:
    name = request.form.get('name')
    genres = request.form.getlist('genres')
    address = request.form.get('address')
    city = request.form.get('city')
    state = request.form.get('state')
    phone = request.form.get('phone')
    website = request.form.get('website')
    image_link = request.form.get('image_link')
    facebook_link = request.form.get('facebook_link')
    seeking = request.form.get('seeking_talent')
    seeking_talent = True if seeking == 'y' else False
    seeking_description = request.form.get('seeking_description')
    venue = Venue(name=name, genres=genres, address=address, city=city, state=state,
                  phone=phone, website=website, image_link=image_link,
                  facebook_link=facebook_link, seeking_talent=seeking_talent,
                  seeking_description=seeking_description)
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')
  '/venues/<int:venue_id>'

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    flash('Venue ID ' + str(venue_id) + ' was successfully deleted!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ID ' + str(venue_id) + ' could not be deleted.')
  finally:
    db.session.close()
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = []
  artists = Artist.query.all()
  for artist in artists:
    data.append({"id": artist.id, "name": artist.name})
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  data = []
  search_term = request.form.get('search_term')
  # Case-insensitive search terms
  results = Artist.query.filter(Artist.name.ilike("%" + search_term + "%")).all()
  # Count the number of upcoming shows for each artist returned
  for result in results:
    num_upcoming_shows = 0
    for show in result.show:
      if show.start_time > datetime.now():
        num_upcoming_shows += 1
    data.append({"id": result.id, "name": result.name, "num_upcoming_shows": num_upcoming_shows})
  response = {
    "count": len(results),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.get(artist_id)

  upcoming_shows = []
  past_shows = []

  # Filter Show table by artist_id and join its filtered version with Venue table
  upcoming_shows_query = Show.query.filter_by(artist_id=artist_id).filter(
    Show.start_time > datetime.now()).join(Venue, Show.venue_id == Venue.id).add_columns(
      Venue.id, Venue.name, Venue.image_link, Show.start_time).all()
  past_shows_query = Show.query.filter_by(artist_id=artist_id).filter(
    Show.start_time <= datetime.now()).join(Venue, Show.venue_id == Venue.id).add_columns(
      Venue.id, Venue.name, Venue.image_link, Show.start_time).all()

  for row in upcoming_shows_query:
    upcoming_shows.append({
      "venue_id": row[1],
      "venue_name": row[2],
      "venue_image_link": row[3],
      "start_time": str(row[4])
    })
  for row in past_shows_query:
    past_shows.append({
      "venue_id": row[1],
      "venue_name": row[2],
      "venue_image_link": row[3],
      "start_time": str(row[4])
    })
  
  # An alternative without using joined query:
  # for show in artist.show:
  #     if show.start_time > datetime.now():
  #       upcoming_shows.append({
  #         "venue_id": show.venue_id,
  #         "venue_name": show.venue.name,
  #         "venue_image_link": show.venue.image_link,
  #         "start_time": str(show.start_time)
  #       })
  #     else:
  #       past_shows.append({
  #         "venue_id": show.venue_id,
  #         "venue_name": show.venue.name,
  #         "venue_image_link": show.venue.image_link,
  #         "start_time": str(show.start_time)
  #       })
  
  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres.strip('}{').split(','),
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
  }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)
  form = ArtistForm(obj=artist)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  try:
    artist = Artist.query.get(artist_id)
    artist.name = request.form.get('name')
    artist.genres = request.form.getlist('genres')
    artist.address = request.form.get('address')
    artist.city = request.form.get('city')
    artist.state = request.form.get('state')
    artist.phone = request.form.get('phone')
    artist.website = request.form.get('website')
    artist.image_link = request.form.get('image_link')
    artist.facebook_link = request.form.get('facebook_link')
    artist.seeking = request.form.get('seeking_talent')
    artist.seeking_venue = True if artist.seeking == 'y' else False
    artist.seeking_description = request.form.get('seeking_description')
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully updated!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.')
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get(venue_id)
  form = VenueForm(obj=venue)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  try:
    venue = Venue.query.get(venue_id)
    venue.name = request.form.get('name')
    venue.genres = request.form.getlist('genres')
    venue.address = request.form.get('address')
    venue.city = request.form.get('city')
    venue.state = request.form.get('state')
    venue.phone = request.form.get('phone')
    venue.website = request.form.get('website')
    venue.image_link = request.form.get('image_link')
    venue.facebook_link = request.form.get('facebook_link')
    venue.seeking = request.form.get('seeking_talent')
    venue.seeking_talent = True if venue.seeking == 'y' else False
    venue.seeking_description = request.form.get('seeking_description')
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully updated!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')
  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  try:
    name = request.form.get('name')
    genres = request.form.getlist('genres')
    city = request.form.get('city')
    state = request.form.get('state')
    phone = request.form.get('phone')
    website = request.form.get('website')
    image_link = request.form.get('image_link')
    facebook_link = request.form.get('facebook_link')
    seeking = request.form.get('seeking_venue')
    seeking_venue = True if seeking == 'y' else False
    seeking_description = request.form.get('seeking_description')
    artist = Artist(name=name, genres=genres, city=city, state=state, phone=phone,
                    website=website, image_link=image_link, facebook_link=facebook_link,
                    seeking_venue=seeking_venue, seeking_description=seeking_description)
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.route('/artists/<artist_id>', methods=['POST'])
def delete_artist(artist_id):
  try:
    artist = Artist.query.get(artist_id)
    db.session.delete(artist)
    db.session.commit()
    flash('Artist ID ' + str(artist_id) + ' was successfully deleted!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ID ' + str(artist_id) + ' could not be deleted.')
  finally:
    db.session.close()
  return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  data = []
  shows = Show.query.all()
  for show in shows:
    data.append({"venue_id": show.venue_id,
                 "venue_name": show.venue.name,
                 "artist_id": show.artist_id,
                 "artist_name": show.artist.name,
                 "artist_image_link": show.artist.image_link,
                 "start_time": str(show.start_time)})
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  try:
    venue_id = request.form.get('venue_id')
    artist_id = request.form.get('artist_id')
    start_time = request.form.get('start_time')
    show = Show(venue_id=venue_id, artist_id=artist_id, start_time=start_time)
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
