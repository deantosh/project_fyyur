#--------------------------------------------------------------------#
# Imports
#--------------------------------------------------------------------#
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
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm
import logging

# Import model and forms module
from models import *
from form_validate.forms import *

# Create a venue blueprint object
venue_bp = Blueprint('venue_bp', __name__, template_folder='templates')


#  Create Venue
#  -------------------------------------------------------------------#
@venue_bp.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@venue_bp.route('/venues/create', methods=['POST'])
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
#------------------------------------------------------------------------#
@venue_bp.route('/venues')
def venues():

    data=[]
    
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
#-----------------------------------------------------------------------#
@venue_bp.route('/venues/<int:venue_id>')
def show_venue(venue_id):

    data = {}
    
    # Get venue object using (venue_id) / return an error if not found
    venue = Venue.query.get_or_404(venue_id)

    # Get details of past shows for the selected venue
    past_shows_query = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id)\
      .filter(Show.start_time < datetime.now()).all()
    past_shows = []

    for show in past_shows_query:
      past_shows.append({
        "artist_id": show.artist_id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
      })
    
    # Get details of upcoming shows for the selected venue
    upcoming_shows_query = db.session.query(Show).filter(Show.venue_id==venue_id)\
      .filter(Show.start_time > datetime.now()).all()
    upcoming_shows = []

    for show in upcoming_shows_query:
      upcoming_shows.append({
        "artist_id": show.artist_id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S")    
    })

    # Add data to dictionary
    data = {
        'id': venue.id,
        'name': venue.name,
        'genres': venue.genres,
        'city': venue.city,
        'state': venue.state,
        'address': venue.address,
        'phone':  venue.phone,
        'website_link': venue.website_link,
        'facebook_link': venue.facebook_link,
        'image_link': venue.image_link,
        "seeking_talent": venue.seeking_artist,
        "seeking_description": venue.seeking_description,
        'past_shows': past_shows,
        'upcoming_shows': upcoming_shows,
        'past_shows_count': len(past_shows),
        'upcoming_shows_count': len(upcoming_shows),
    }

    #Redirect to the show_venue page
    return render_template('pages/show_venue.html', venue=data)


# Search venues
# -------------------------------------------------------------------------#
@venue_bp.route('/venues/search', methods=['POST'])
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
    return render_template('pages/search_venues.html', 
      results=response, search_term=request.form.get('search_term', ''))


# Update venue details
#------------------------------------------------------------------------#   
@venue_bp.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):

  form = VenueForm()

  # Get the selected venue object to update or return error message
  venue = Venue.query.get_or_404(venue_id)
  
  # Redirect to the edit_venue page
  return render_template('forms/edit_venue.html', form=form, venue=venue)


@venue_bp.route('/venues/<int:venue_id>/edit', methods=['POST'])
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
  return redirect(url_for('venue_bp.show_venue', venue_id=venue_id))


# Delete venue
#----------------------------------------------------------------------------#
@venue_bp.route('/venues/<venue_id>/delete', methods={"GET"})
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
