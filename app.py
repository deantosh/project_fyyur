#--------------------------------------------------------------------------#
# Imports
#--------------------------------------------------------------------------#
from flask_migrate import Migrate
from flask_moment import Moment
from babel import Locale
from flask import Flask, render_template
import logging
from logging import Formatter, FileHandler
import dateutil.parser
from datetime import datetime
import babel

# Import user defined module
from models import *

# Import blueprints
from artist.artist import artist_bp
from venue.venue import venue_bp
from show.show import show_bp
from general.general import general_bp


# Config app to the database
#--------------------------------------------------------------------------#
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

# Initialiaze app
db.init_app(app)
with app.app_context():
    db.create_all()
#migrate = Migrate(app, db)

# Register the blueprint on app
app.register_blueprint(general_bp)
app.register_blueprint(artist_bp)
app.register_blueprint(venue_bp)
app.register_blueprint(show_bp)

# Filters.
#----------------------------------------------------------------------------#

# Format date and time
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

# Error handler
#--------------------------------------------------------------------------#
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


# Launch app
#---------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
