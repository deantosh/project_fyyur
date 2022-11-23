#--------------------------------------------------------------------------#
# Imports
#--------------------------------------------------------------------------#
from flask import (
    Flask, 
    Blueprint,
    render_template, 
    request, 
    Response, 
    flash, 
    redirect, 
    url_for
)
from sqlalchemy import desc
from flask_wtf import FlaskForm

# Import model and forms module
from models import *
from form_validate.forms import *


# Create a artist blueprint object
artist_bp = Blueprint('artist_bp', __name__, template_folder='templates')


# Create Artist
#---------------------------------------------------------------------------#
@artist_bp.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@artist_bp.route('/artists/create', methods=['POST'])
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
#---------------------------------------------------------------------------#
@artist_bp.route('/artists')
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
#---------------------------------------------------------------------------#

@artist_bp.route('/artists/search', methods=['POST'])
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
  return render_template('pages/search_artists.html', 
    results=response, search_term=request.form.get('search_term', ''))


# Show details of the selected artist
#-----------------------------------------------------------------------------#
@artist_bp.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  
  # Get the artist object using the artist_id / if not found return an error
  artist = Artist.query.get_or_404(artist_id)
  
  # Get the details of the past shows
  past_shows_query = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id)\
    .filter(Show.start_time < datetime.now()).all()
  past_shows = []

  for show in past_shows_query:
    past_shows.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "venue_image_link": show.venue.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })
  
  # Get the details of the upcoming shows
  upcoming_shows_query = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id)\
    .filter(Show.start_time > datetime.now()).all()
  upcoming_shows = []

  for show in upcoming_shows_query:
    upcoming_shows.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "venue_image_link": show.venue.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })
  
  # Append details to data
  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website_link": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }

  # Redirect to show_artist page
  return render_template('pages/show_artist.html', artist=data)
    

#  Update artist details
#-----------------------------------------------------------------------------#
@artist_bp.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):

  form = ArtistForm()
  
  # Get the selected artist to update / return error
  artist = Artist.query.get_or_404(artist_id)
  
  # Redirect to edit_artist page
  return render_template('forms/edit_artist.html', form=form, artist=artist)
    

@artist_bp.route('/artists/<int:artist_id>/edit', methods=['POST'])
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
  return redirect(url_for('artist_bp.show_artist', artist_id=artist_id))


# Delete Artist
#-------------------------------------------------------------------------------#
@artist_bp.route('/artists/<artist_id>/delete', methods={"GET"})
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
 