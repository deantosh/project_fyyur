#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
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


# Create a show blueprint object
show_bp = Blueprint('show_bp', __name__, template_folder='templates')


# Create show
#-----------------------------------------------------------------------------#
@show_bp.route('/shows/create')
def create_shows():
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@show_bp.route('/shows/create', methods=['POST'])
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
#-------------------------------------------------------------------------#
@show_bp.route('/shows')
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
