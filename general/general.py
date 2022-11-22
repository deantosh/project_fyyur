from flask import (
    Flask, 
    Blueprint,
    render_template,
    redirect, 
    url_for
)
from models import *
from sqlalchemy import desc


# Create a artist blueprint object
general_bp = Blueprint('general_bp', __name__)


@general_bp.route('/')
def index():
  # Get the first 10 venues
  venues = Venue.query.order_by(desc(Venue.id)).limit(5).all()

  # Get the first 10 arists
  artists = Artist.query.order_by(desc(Artist.id)).limit(5).all()

  #Redirect to home page
  return render_template('pages/home.html', venues=venues, artists=artists)
