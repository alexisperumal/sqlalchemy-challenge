# Alexis Perumal, 2/5/20
# UCSD Data Science Bootcamp, HW 10

from flask import Flask, jsonify

import numpy as np
import pandas as pd
import datetime as dt

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy import and_

# SQLAlchemy Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# This function called `calc_temps` will accept start date and end date in the format '%Y-%m-%d' 
# and return the minimum, average, and maximum temperatures for that range of dates
def calc_temps(start_date, end_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    
    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()




#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&ltstart&gt<br/>"
        f"/api/v1.0/&ltstart&gt/&ltend&gt<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return Hawaii precipitation data as json."""
    prcp_data = {}
    for date, prcp in session.query(Measurement.date, Measurement.prcp).all():
        prcp_data[date] = prcp
    return jsonify(prcp_data)



@app.route("/api/v1.0/stations")
def stations():
    """Return the station list as json."""

    return jsonify(session.query(Station.station, Station.name, Station.latitude,\
        Station.longitude, Station.elevation).all())



@app.route("/api/v1.0/tobs")
def tobs():
    """Requery for the dates and temperature observations from a year from the last data point.
    Return a JSON list of Temperature Observations (tobs) for the previous year."""

    max_date = session.query(func.max(Measurement.date)).all()[0][0]
    start_date = str(int(max_date[:4])-1) + max_date[4:] # Pull the year, decrement it, and reubild the date
    tobs_data = session.query(Measurement.date, Measurement.station, Measurement.tobs).filter(Measurement.date>=start_date).order_by(Measurement.date).all()
    return jsonify(tobs_data)


@app.route("/api/v1.0/<start_date>")
def daily_start(start_date):
    """Return a JSON list of the minimum temperature, the average temperature, and the
    max temperature for a given start or start-end range. When given the start only,
    calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date."""

    results = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        group_by(Measurement.date).filter(Measurement.date >= start_date).all()

    return jsonify(results)



@app.route("/api/v1.0/<start_date>/<end_date>")
def daily_start_end(start_date, end_date):
    """Return a JSON list of the minimum temperature, the average temperature, and the
    max temperature for a given start or start-end range. When given the start and the end date, calculate the TMIN,
    TAVG, and TMAX for dates between the start and end date inclusive."""

    results = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        group_by(Measurement.date).filter(Measurement.date >= start_date).\
            filter(Measurement.date <= end_date).all()

    return jsonify(results)


if __name__ == "__main__":
    print('Before app.run()')
    app.run(debug=True)
    print('Bye!')
