#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from distutils.log import error
import json
import dateutil.parser
import babel
import datetime
from flask import Flask, jsonify, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from pytz import timezone
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import Venue, Artist, Show, db
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

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
  venues = Venue.query.all()

  grouped_venues = Venue.query.distinct(Venue.city, Venue.state).all()

  data = []

  current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

  for grouped_venue in grouped_venues:
    venue_data =[]

    for venue in venues:
      if grouped_venue.city==venue.city:
        venue_data.append({
          "id": venue.id, "name": venue.name, "num_upcoming_shows": len([Show.query.filter(Show.start_time > current_time)])
        })

    data.append({
      "city": grouped_venue.city, "state": grouped_venue.state, "venues": venue_data
    })

  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

  return render_template('pages/venues.html', areas=data)

  #search from homepage
def venue_search_result(search_term):
  try:
    data = Venue.query.filter(db.func.lower(Venue.name).ilike(f"%{search_term.lower()}%")).order_by('name').all()
    return data
  except Exception as e:
    print(e)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  try:
    data = venue_search_result(request.form['search_term'])
    venues = []
    for venue in data:
      current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      parameter = {}
      parameter['id'] = venue.id
      parameter['name'] = venue.name
      parameter['num_upcoming_shows'] = Show.query.filter(db.and_(Show.start_time > current_time, Show.venue_id ==venue.id)).count()
      venues.append(parameter)
      response={
        "count": len(data),
        "data": venues 
      }
  except:
    flash(f'An error has occured, try again', category="error")
    abort(500)
  finally:
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  #try:
    data={}
    venue_data = Venue.query.filter(Venue.id==venue_id).first()
    data = {}
    data['id']=venue_data.id
    data['name']=venue_data.name
    data['address']=venue_data.address
    data['city']=venue_data.city
    data['state']=venue_data.state
    data['phone']=venue_data.phone
    data['genres']=venue_data.genres
    data['website']=venue_data.website
    data['facebook_link']=venue_data.facebook_link
    data['image_link']=venue_data.image_link
    data['seeking_talent']=venue_data.seeking_talent
    data['seeking_description']=venue_data.seeking_description
    past_shows =[]
    upcoming_shows=[]
    current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    past = db.session.query(Show).join(Artist).filter(
      db.and_(Show.start_time < current_time, Show.venue_id == venue_id)).all()
    for show in past:
      past_show={}
      past_show['artist_id']=show.artist.id
      past_show['artist_name']=show.artist.name
      past_show['artist_image_link']=show.artist.image_link
      past_show['start_time']=str(show.start_time)
      past_shows.append(past_show)

    upcoming=db.session.query(Show).join(Artist).filter(
      db.and_(Show.start_time > current_time, Show.venue_id == venue_id)).all()
    for show in upcoming:
      upcoming_show={}
      upcoming_show['artist_id']=show.artist.id
      upcoming_show['artist_name']=show.artist.name
      upcoming_show['artist_image_link']=show.artist.image_link
      upcoming_show['start_time']=str(show.start_time)
      upcoming_shows.append(upcoming_show)
    data['past_shows']=past_shows
    data['upcoming_shows']=upcoming_shows
    data['past_shows_count']=len(past_shows)
    data['upcoming_shows_count']=len(upcoming_shows)
    return render_template('pages/show_venue.html', venue=data)
  #except:
    flash (f'Error! {venue_id} does not exist')
    

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form)
  if request.method =='POST':
    if form.validate():
      try:
        venue = Venue(name=request.form['name'], city=request.form['city'], state=request.form['state'], address=request.form['address'],
        phone=request.form['phone'], genres=request.form.getlist('genres', type=str), website=request.form['website_link'], 
        facebook_link=request.form['facebook_link'], image_link=request.form['image_link'], seeking_description=request.form['seeking_description'],
         seeking_talent="seeking_talent" in request.form)
        
        db.session.add(venue)
        db.session.commit()
        flash(f"Venue   '{request.form['name']}' was successfully listed!")
        return redirect(url_for('show_venue', venue_id=Venue.query.order_by(Venue.id.desc()).first().id))
        
      except:
        flash(f"Venue  '{request.form['name']}'  could not be listed!", category="error")
        db.session.rollback()
        abort(500)
      finally:
        db.session.close()
    else:
      return error
  return redirect(url_for('index')) 


    
    


  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  
  Venue.query.filter(Venue.id == venue_id).delete()
  db.session.commit()
  flash(f'Venue with id {venue_id} has been deleted!')
  #else:
  #db.session.rollback()
  db.session.close()
  return jsonify({"homeUrl": '/'})



    
    

  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  #return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  #if:
    result = Artist.query.all()
    data = []
    for artist in result:
      match = {}
      match['id'] = artist.id
      match['name'] = artist.name
      data.append(match)
  #else:
  #  flash(f"Sorry, an error has occured!")
  #  abort(500)
    return render_template('pages/artists.html', artists=data)


def artist_search_result(search_term):
  try:
    data = Artist.query.filter(db.func.lower(Artist.name).ilike(f"%{search_term.lower()}%")).order_by('name').all()
    return data
  except Exception as e:
    print(e)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  data = artist_search_result(request.form['search_term'])
  artists = []
  current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  for artist in data:
    match = {}
    match['id'] = artist.id
    match['name'] = artist.name
    match['num_upcoming_shows'] = Show.query.filter(
      db.and_(Show.start_time > current_time, Show.artist_id == artist.id)).count()
    artists.append(match)
  response = {
    "count": len(data),
    "data": artists
  }
    
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  data = {}
  artist_data = Artist.query.filter(Artist.id==artist_id).first()
  data = {}
  data['id'] = artist_data.id
  data['name'] = artist_data.name
  data['city'] = artist_data.city
  data['state'] = artist_data.state
  data['phone'] = artist_data.phone
  data['genres'] = artist_data.genres
  data['website'] = artist_data.website
  data['facebook_link'] = artist_data.facebook_link
  data['image_link'] = artist_data.image_link
  data['seeking_venue'] = artist_data.seeking_venue
  data['seeking_description'] = artist_data.seeking_description
  past_shows = []
  upcoming_shows = []
  current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

  past = db.session.query(Show).join(Venue).filter(
    db.and_(Show.start_time < current_time, Show.artist_id == artist_id)).all()
  for show in past:
    past_show = {}
    past_show['venue_id'] = show.venue.id
    past_show['venue_name'] = show.venue.name
    past_show['venue_image_link'] = show.venue.image_link
    past_show['start_time'] = str(show.start_time)
    past_shows.append(past_show)

  upcoming = db.session.query(Show).join(Venue).filter(
    db.and_(Show.start_time > current_time, Show.artist_id == artist_id)).all()
  for show in upcoming:
    upcoming_show = {}
    upcoming_show['venue_id'] = show.venue.id
    upcoming_show['venue_name'] = show.venue.name
    upcoming_show['venue_image_link'] = show.venue.image_link
    upcoming_show['start_time'] = str(show.start_time)
    upcoming_shows.append(upcoming_show)
  data['past_shows'] = past_shows
  data['upcoming_shows'] = upcoming_shows
  data['past_shows_count'] = len(past_shows)
  data['upcoming_shows_count'] = len(upcoming_shows)
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  #try:
  data = Artist.query.filter(Artist.id == artist_id).first()
  artist_form = ArtistForm(name=data.name, city=data.city, state=data.state, phone=data.phone, image_link=data.image_link, genres=data.genres,
    website_link=data.website, facebook_link=data.facebook_link, seeking_venue=data.seeking_venue, seeking_description=data.seeking_description)

  #except:
  #flash(f'Cannot load Artist edit form', category="error")
  #  abort(500)
  #finally:
  return render_template('forms/edit_artist.html', form=artist_form, artist=data)
    
  
  
  
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  form = ArtistForm(request.form)
  if form.validate():
    try:
      artist = Artist.query.filter(Artist.id == artist_id).first()
      artist.name = request.form['name']
      artist.city = request.form['city']
      artist.state = request.form['state']
      artist.phone = request.form['phone']
      artist.genres = request.form.getlist('genres', type=str)
      artist.website = request.form['website_link']
      artist.facebook_link = request.form['facebook_link']
      artist.image_link = request.form['image_link']
      artist.seeking_venue = 'seeking_venue' in request.form
      artist.seeking_description = request.form['seeking_description']
      db.session.commit()
      flash(f"Artist Updated!")
    except:
      flash(f"Error!, Artist could not be updated.", category=error)
      db.session.rollback()
      abort(500)
    finally:
      db.session.close()
  else:
    return redirect(url_for('show_artist', artist_id=artist_id))
  
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):

  data = Venue.query.filter(Venue.id == venue_id).first()
  venue_form = VenueForm(name=data.name, city=data.city, state=data.state, address=data.address, phone=data.phone, image_link=data.image_link, genres=data.genres,
    website_link=data.website, facebook_link=data.facebook_link, seeking_talent=data.seeking_talent, seeking_description=data.seeking_description)
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=venue_form, venue=data)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  form = VenueForm(request.form)
  if form.validate():
    try:
      venue = Venue.query.filter(Venue.id == venue_id).first()
      venue.name = request.form['name']
      venue.address = request.form['address']
      venue.city = request.form['city']
      venue.state = request.form['state']
      venue.phone = request.form['phone']
      venue.genres = request.form.getlist('genres', type=str)
      venue.website = request.form['website_link']
      venue.facebook_link = request.form['facebook_link']
      venue.image_link = request.form['image_link']
      venue.seeking_talent = 'seeking_talent' in request.form
      venue.seeking_description = request.form['seeking_description']
      db.session.commit()
      flash(f"Venue Updated!")
    except:
      flash(f"Error!, Venue could not be updated.")
      db.session.rollback()
      abort(500)
    finally:
      db.session.close()
  else:
    flash(f'An Error has occured')
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm(request.form)
  if form.validate():
    try:
      #phoneExists = False
      if not Artist.query.filter(Artist.phone == request.form['phone']).count() > 0:
        artist = Artist(name=request.form['name'], city=request.form['city'], state=request.form['state'], phone=request.form['phone'], 
        genres=request.form.getlist('genres',type=str), website=request.form['website_link'], image_link=request.form['image_link'], facebook_link=request.form['facebook_link'], seeking_venue='seeking_venue' in request.form, 
        seeking_description=request.form['seeking_description'])

        db.session.add(artist)
        db.session.commit()
        flash(f"Artist '{request.form['name']}' was successfully listed")
        return redirect(url_for('show_artist', artist_id=Artist.query.order_by(Artist.id.desc()).first().id))
      else:
        phoneExists = True
        raise
    except:
      flash(f"Error! Artist can not be listed because Phone Number exists")
      db.session.rollback()
      abort(500)
    finally:
      db.session.close()
  else:
    flash(f'An error has occured')
  return redirect(url_for('index'))
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  #flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  #return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  try:
    data = []
    shows = Show.query.all()

    for show in shows:
      match = {}
      match['venue_id'] = show.venue_id
      match['venue_name'] = Venue.query.filter(
        Venue.id == show.venue_id).first().name
      match['artist_id'] = show.artist_id
      match['artist_name'] = Artist.query.filter(
        Artist.id == show.artist_id).first().name
      match['artist_image_link'] = Artist.query.filter(
        Artist.id == show.artist_id).first().image_link
      match['start_time'] = str(show.start_time)
      data.append(match)
  except:
    flash(f"Can't display Records")
    abort(500)
  finally:
    return render_template('pages/shows.html', shows=data)
    

  # displays list of shows at /shows
  # TODO: replace with real venues data.
  
  #return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():

  show = Show(artist_id=request.form['artist_id'], venue_id=request.form['venue_id'], 
    start_time=datetime.fromisoformat(str(request.form['start_time'])))

  if (Artist.query.filter(Artist.id == request.form['artist_id']).count() == 0
    or 
     Venue.query.filter(Venue.id == request.form['venue_id']).count() == 0):
      flash('An error occurred. Show could not be listed. Confirm Venue or Show is Listed')
      db.session.rollback()
      db.session.close
  else:
    flash('Show was successfully listed!')
    db.session.add(show)
    db.session.commit()

  




  
    #else:
    #flash('An error occurred. Show could not be listed. Confirm Venue or Show is Listed')
  #else:
    
    #flash('An error occurred. Show could not be listed.')
    
  #  db.session.rollback()
  #  db.session.close()
  #  abort(500)
  return render_template('pages/home.html')

  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
  #flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  #return render_template('pages/home.html')

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
"""""
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
"""""
