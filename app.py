#------------------------------------------------------------------------------------------------------------#
# Imports
#------------------------------------------------------------------------------------------------------------#

from unittest.util import strclass
from flask import Flask
from flask_migrate import Migrate
from flask_moment import Moment
import json
import dateutil.parser
import babel
from datetime import datetime
import logging
from babel import Locale
from flask import (
    Flask, 
    render_template, 
    request, 
    Response, 
    flash, 
    redirect, 
    url_for
)
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm
from forms import *
from models import *

#------------------------------------------------------------------------------------------------------------#
# App Config.
#------------------------------------------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app) #Just initialize it here
migrate = Migrate(app, db)

#------------------------------------------------------------------------------------------------------------#
# Filters.
#------------------------------------------------------------------------------------------------------------#

#Formatting date and time
def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

# Convert string with specific format to datetime / used to compare datetime to get upcoming shows
def str_to_datetime(date):
    return datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
#------------------------------------------------------------------------------------------------------------#
# Controllers.
#------------------------------------------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')

#------------------------------------------------------------------------------------------------------------#
#  Venues Section
#------------------------------------------------------------------------------------------------------------#

#  Create Venue
#  ----------------------------------------------------------------------------------------------------------#

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  
    error = False
    
    # Apply the FlaskForm object to validate fields
    form = VenueForm(request.form)
    try:
        newVenue = Venue(
            # Get data from HTML forms
            name = form.name.data,
            city = form.city.data,
            state = form.state.data,
            address = form.address.data,
            phone = form.phone.data,
            genres = form.genres.data,
            facebook_link = form.facebook_link.data,
            image_link = form.image_link.data,
            website_link = form.website_link.data,
            seeking_artist = form.seeking_talent.data,
            seeking_description = form.seeking_description.data
        )
        
        #add the venue object to db session
        db.session.add(newVenue)
        db.session.commit()

        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
        
    except:
        #When error occur rollback the session
        error = True
        db.session.rollback()

        #display message
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
            
    finally:
        db.session.close()
  
    #Redirect to homepage
    return render_template('pages/home.html')

# List all the venues created
#------------------------------------------------------------------------------------------------------------#
@app.route('/venues')
def venues():

    data=[]

    upcoming_shows = 0
    
    # Get a record of the distinct city and state that define the places where the venues are located
    places = Venue.query.distinct(Venue.city, Venue.state).all()
    
    #Loop through every place with venues
    for place in places:

        venue_details = []
        
        # Get all venues in that specific city and state
        venues = Venue.query.filter(Venue.city.like(place.city))\
        .filter(Venue.state.like(place.state)).all()
        
        # Loop through every venue in that city and state
        for venue in venues:

          # Add venue record to the empty venue_details list
          venue_details.append({'id':venue.id, 'name':venue.name})
                
        #add each city to the data list
        data.append({'city':place.city, 'state':place.state, 'venues':venue_details})

    # Redirect to venues page            
    return render_template('pages/venues.html', areas=data)


# Show the details of the selected venue
#------------------------------------------------------------------------------------------------------------#
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):

    data = {}
    
    # Get venue object using (venue_id) / return an error if not found
    venue = Venue.query.get_or_404(venue_id)

    # Add data to dictionary
    data = {
        'id': venue.id,
        'name': venue.name,
        'genre': venue.genres,
        'city': venue.city,
        'state': venue.state,
        'address': venue.address,
        'phone':  venue.phone,
        'website_link': venue.website_link,
        'facebook_link': venue.facebook_link,
    }

    # Find the past and upcoming shows for the selected venue.
    past_shows = []
    upcoming_shows = []

    for show in venue.shows:
        temp_show = {
            'artist_id': show.artist_id,
            'artist_name': show.artist.name,
            'artist_image_link': show.artist.image_link,
            'start_time': show.start_time.strftime("%m/%d/%y, %H:%M")
        }
        if show.start_time <= datetime.now():
            past_shows.append(temp_show)
        else:
            upcoming_shows.append(temp_show)
    
    # Cannot append to a dictionary thus return the dictionary attribute of the venue object
    data = vars(venue)

    # Update the dictionary
    data['past_shows'] = past_shows
    data['upcoming_shows'] = upcoming_shows
    data['past_shows_count'] = len(past_shows)
    data['upcoming_shows_count'] = len(upcoming_shows)

    #Redirect to the show_venue page
    return render_template('pages/show_venue.html', venue=data)


# Search venues
# -----------------------------------------------------------------------------------------------------------#

@app.route('/venues/search', methods=['POST'])
def search_venues():

    search_word = request.form['search_term']

    results = Venue.query.filter(Venue.name.ilike(f'%{search_word}%')).all()

    data = []

    for result in results:

        # Add the result to the data list
        data.append({'id': result.id, 'name': result.name})

    # Create response to display with search results
    response = {
        "count": len(results),
        "data": data
    } 
    
    # Redirect to search_venues page
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

# Update venue details
#------------------------------------------------------------------------------------------------------------#   

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):

  form = VenueForm()

  # Get the selected venue object to update or return error message
  venue = Venue.query.get_or_404(venue_id)
  
  # Redirect to the edit_venue page
  return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):

  # Use the FlaskForm object to validate user input data
  form = VenueForm(request.form)

  # Get the selected venue to update or return error
  venue = Venue.query.get_or_404(venue_id)

  try:
    # Update the venue data in the database
    venue.name = form.name.data
    venue.genres = form.genres.data
    venue.city = form.city.data
    venue.state = form.state.data
    venue.address = form.address.data
    venue.phone = form.phone.data
    venue.facebook_link = form.facebook_link.data
    venue.website_link = form.website_link.data
    venue.image_link = form.image_link.data
    venue.seeking_talent = form.seeking_talent.data
    venue.seeking_description = form.seeking_description.data

    db.session.commit()

    # Flash success message
    flash('Venue ' + request.form['name'] + ' has been updated')

  except:
    db.session.rollback()
    # Flash error message
    flash('An error occured while trying to update Venue')

  finally:
    db.session.close()
  
  # Redirect to the show_venue page
  return redirect(url_for('show_venue', venue_id=venue_id))

# Delete venue
#------------------------------------------------------------------------------------------------------------#

@app.route('/venues/<venue_id>/delete', methods={"GET"})
def delete_venue(venue_id):

  # Get the venue object to be deleted
  venue = Venue.query.get_or_404(venue_id)

  try:
    #Add venue object to db.session. 
    db.session.delete(venue) 
    db.session.commit()

    #display success message
    flash('Venue ' + venue.name + ' deleted successfully!')

  except:
    db.session.rollback()
    flash('Venue ' + venue.name + ' not deleted.')

  finally:
    db.session.close()

  #Redirect user to home page.
  return render_template('pages/home.html')
 

#------------------------------------------------------------------------------------------------------------#
#  Artists section
#------------------------------------------------------------------------------------------------------------#

# Create Artist
#------------------------------------------------------------------------------------------------------------#

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():

  # Apply FlaskForm object to validate fields
  form = ArtistForm(request.form)

  try:
    newArtist = Artist(
            # Get data from HTML forms
            name = form.name.data,
            city = form.city.data,
            state = form.state.data,
            phone = form.phone.data,
            genres = form.genres.data,
            facebook_link = form.facebook_link.data,
            image_link = form.image_link.data,
            website_link = form.website_link.data,
            seeking_venue = form.seeking_venue.data,
            seeking_description = form.seeking_description.data
    )

    # Add the artist object to db session
    db.session.add(newArtist)
    db.session.commit()

    # Display success message when new venue is added to the database
    flash('Artist ' + request.form['name'] + ' was successfully listed!')

  except:
    # When error occur rollback the session
    db.session.rollback()

    # Display message
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')

  finally:
    db.session.close()
  
  #Redirect user to homepage
  return render_template('pages/home.html')


# List the artists added
#------------------------------------------------------------------------------------------------------------#

@app.route('/artists')
def artists():
  
  data = []
  
  artists = Artist.query.all()

  #Loop through the artists list
  for artist in artists:

    #Add the artists details to the data list
    data.append({
      "id": artist.id,
      "name": artist.name
    })
  
  #Redirect user to artist page
  return render_template('pages/artists.html', artists=data)

# Search artists
#------------------------------------------------------------------------------------------------------------#

@app.route('/artists/search', methods=['POST'])
def search_artists():
  
  data=[]
  
  #Define word used for search
  search_word = request.form['search_term']

  #Artist search results
  results = Artist.query.filter(Artist.name.ilike(f'%{search_word}%')).all()

  #Loop through the results to get artist match
  for result in results:
    data.append({"id":result.id, "name":result.name, "num_upcoming_shows":0})

  #Create a response to display with search results
  response = {
        "count": len(results),
        "data": data
  }

  # Redirect to the search page
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


# Show details of the selected artist
#------------------------------------------------------------------------------------------------------------#

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

    data = {}

    # Get the artist object using the artist_id / if not found return an error
    artist = Artist.query.get_or_404(artist_id)

    # Add the artist details to data dict
    data = {
        'id': artist.id,
        'name': artist.name,
        'genre': artist.genres,
        'city': artist.city,
        'state': artist.state,
        'phone': artist.phone,
        'website_link': artist.website_link,
        'facebook_link': artist.facebook_link
    }

    # Find the upcoming and past shows of the selected artist

    upcoming_shows = []
    past_shows = []

    for show in artist.shows:
        temp_show = {
            'venue_id': show.venue_id,
            'venue_name': show.venue.name,
            'venue_image_link': show.venue.image_link,
            'start_time': show.start_time.strftime("%m/%d/%y, %H:%M")
        }

        if show.start_time <= datetime.now():
            past_shows.append(temp_show)
        else:
            upcoming_shows.append(temp_show)

    # Cannot append to a dictionary thus return the dictionary attribute of the venue object
    data = vars(artist)

    # Update the dictionary
    data['upcoming_shows'] = upcoming_shows
    data['past_shows'] = past_shows
    data['upcoming_shows_count'] =  len(upcoming_shows)
    data['past_shows_count'] = len(past_shows)

    return render_template('pages/show_artist.html', artist=data)
    

#  Update artist details
#------------------------------------------------------------------------------------------------------------#
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):

  form = ArtistForm()
  
  # Get the selected artist to update / return error
  artist = Artist.query.get_or_404(artist_id)
  
  # Redirect to edit_artist page
  return render_template('forms/edit_artist.html', form=form, artist=artist)
    

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    
  # Use FlaskForm object to validate user data
  form = ArtistForm()
    
  # Get the selected artist to update / return error
  artist = Artist.query.get_or_404(artist_id)
  
  try:
    # Update artist data
    artist.name = form.name.data
    artist.state = form.state.data
    artist.city = form.city.data
    artist.phone = form.phone.data
    artist.genres = form.genres.data
    artist.image_link = form.image_link.data
    artist.facebook_link = form.facebook_link.data
    artist.website_link = form.website_link.data
    artist.seeking_venue = form.seeking_venue.data
    artist.seeking_description = form.seeking_description.data
    
    db.session.commit()
    # Flash success message
    flash('The Artist ' + request.form['name'] + ' has been successfully updated!')

  except:
    db.session.rolback()
    # Flash error message
    flash('An Error has occured and the update unsuccessful')

  finally:
    db.session.close()

  # Redirect to show_artist page
  return redirect(url_for('show_artist', artist_id=artist_id))

# Delete venue
#------------------------------------------------------------------------------------------------------------#

@app.route('/artists/<artist_id>/delete', methods={"GET"})
def delete_artist(artist_id):

  # Get the venue object to be deleted
  artist = Artist.query.get_or_404(artist_id)

  try:
    #Add venue object to db.session. 
    db.session.delete(artist) 
    db.session.commit()

    #display success message
    flash('Artist ' + artist.name + ' deleted successfully!')

  except:
    db.session.rollback()
    flash('Artist ' + artist.name + ' not deleted.')

  finally:
    db.session.close()

  #Redirect user to home page.
  return render_template('pages/home.html')
 
   
#------------------------------------------------------------------------------------------------------------#
#  Shows
#  ----------------------------------------------------------------------------------------------------------#


# Create show
#------------------------------------------------------------------------------------------------------------#

@app.route('/shows/create')
def create_shows():
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():

    error = False

    # Apply FlaskForm object to validate fields.
    form = ShowForm(request.form)
    
    #Get data from form submitted
    try:
        newShow = Show(
          artist_id = form.artist_id.data,
          venue_id = form.venue_id.data, 
          start_time = form.start_time.data
        )

        #Add new show object to the db session
        db.session.add(newShow)
        db.session.commit()

        #If show is successfully added to database
        flash('Show was successfully listed!')

    except:
        #Error handler
        error = True
        db.session.rollback()

        #display message
        flash('An error occured. Show could not be listed.')
        
    finally:
        #close the session
        db.session.close()
  
    #redirect to homepage    
    return render_template('pages/home.html')


# List all the shows created
#------------------------------------------------------------------------------------------------------------#

@app.route('/shows')
def shows():

    data = []

    # Get the list of all venues
    venues = Venue.query.all()

    # For every venue get artist and show details
    for venue in venues:

        # Get the shows in this venue
        show_records = Show.query.filter(Show.venue_id==venue.id).all()

        for show in show_records:

            # Get the artist object / every show has a performing artist
            artist = Artist.query.get(show.artist_id)

            # Append show details to the data list
            data.append({
            "artist_id": show.artist_id,
            "artist_name": artist.name,
            "venue_id": show.venue_id,
            "venue_name": venue.name,
            "artist_image_link": artist.image_link,
            "start_time": show.start_time.strftime("%m/%d/%y, %H:%M")
            })

    #Redirect user to the shows page
    return render_template('pages/shows.html', shows=data)

#------------------------------------------------------------------------------------------------------------#
# Error handler
#------------------------------------------------------------------------------------------------------------#
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

#------------------------------------------------------------------------------------------------------------#
# Launch
#------------------------------------------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
