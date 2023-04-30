# Import the dependencies.
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect= True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################

# Welcome page listing the available routes
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Hawaii's Climate<br/>"
        f"<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

# Converting query results to dictionary with "date" as the key and "prcp" as the value
@app.route("/api/v1.0/precipitation")
def precipitation():
    
    # Retrieve date and prcp scores
    one_year = dt.date(2017,8,23)-dt.timedelta(days=365)
    d_p_scores = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year).all()

    # Convert into dictionary
    scores_dict = dict(d_p_scores)
    session.close()
    return jsonify(scores_dict)

# Return a JSON list of stations from the dataset
@app.route("/api/v1.0/stations")
def stations():
    
    # Get stations
    stations = session.query(Station.station).all()
    
    # put into list
    station_list = list(np.ravel(stations))
    session.close()
    return jsonify(station_list)

# Query the dates and temperature observations of the most-active station for the previous year of data.
@app.route("/api/v1.0/tobs")
def temp_observations():
    # Find most active station
    active_station = session.query(Measurement.station, func.count(Measurement.date)).\
    group_by(Measurement.station).order_by(func.count(Measurement.date).desc()).first()

    # query for most active stations observations for past year
    one_year = dt.date(2017,8,23)-dt.timedelta(days=365)
    temps = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == active_station[0]).\
        filter(Measurement.date >= one_year).all()

    observations = list(np.ravel(temps))
    session.close()
    return jsonify(observations)

# Return a JSON list of the minimum temperature, the average temperature, 
# and the maximum temperature for a specified start or start-end range
@app.route("/api/v1.0/<start>")
def start(start):
    temp_stats = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    start_stats = session.query(*temp_stats).filter(Measurement.date >= start).all()
    start_list = list(np.ravel(start_stats))
    session.close()
    return jsonify(start_list)
    
    

# @app.route("/api/v1.0/<start>/<end>")


if __name__ == "__main__":
    app.run(debug=True)