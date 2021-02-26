# Import Dependencies
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import datetime as dt

#################################
# Database Setup
#################################
engine = create_engine("sqlite:///./Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()

# Reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################
# Flask Setup
#################################
app = Flask(__name__)


#################################
# Flask Routes endpoints
#################################

# Set the home page,and List all routes that are available. For easy to use I hyperlink the list

@app.route("/")
def welcome():
    return (
        f"<h1>Welcome to the Hawaii Climate App API!</h1>"
        f"This is a Flask API for Climate Analysis.<br/><br/>"
        f"<h2>Here are the available routes:</h2>"
        f"Date and precipitation:<br/>"
        f"/api/v1.0/precipitation<br/><br/>"
        f"List of all stations:<br/>"
        f"/api/v1.0/stations<br/><br/>"
        f"Temperature Observations for the most active station for the last one year:<br/>"
        f"/api/v1.0/tobs<br/><br/>"
        f"Temp stats: select a start date as 2016-08-23 or later:<br/>"
        f"/api/v1.0/start_date<br/><br/>"
        f"Temp stats: select a start date as 2016-08-23 or later, and end date as 2017-08-23 or earlier:<br/>"
        f"/api/v1.0/start_date/end_date<br/>"
    )

# Precipitation Route
# Query the last 12 months of precipitation data and return the results as dictionary

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Calculate the date one year from the last date in data set
    last_twelve_months = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    
    # Query to retrieve the date and precipitation for the last 12 months
    prec_data = session.query(Measurement.date, Measurement.prcp).\
                  filter(Measurement.date >= last_twelve_months).all()
    
    session.close()

    # Convert the query results to a dictionary using date as the key and prcp as the value
    all_precipication = {date: prcp for date, prcp in prec_data}

    # Return the JSON representation of dictionary
    return jsonify(all_precipication)


# Station Route
# Return a JSON list of stations from the dataset

@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.station, Station.name).all()
    all_stations = list(np.ravel(results))
    
    session.close()

    # Return the JSON representation of dictionary
    return jsonify(all_stations)


# TOBS Route
# Query the dates and temperature observations of the most active station for the last year of data

@app.route("/api/v1.0/tobs")
def tobs():
    # Calculate the date 1 year ago from the last data point in the database
    last_twelve_months = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    
    # Find the most active station
    most_active_station = session.query(Measurement.station).\
                            group_by(Measurement.station).\
                            order_by(func.count().desc()).first()

    # Get the station id of the most active station
    (most_active_station_id, ) = most_active_station

    # Query to retrieve the date and temperature for the most active station for the last one year.
    tobs_data = session.query(Measurement.date, Measurement.tobs).\
                    filter(Measurement.station == most_active_station_id).\
                    filter(Measurement.date >= last_twelve_months).all()
    
    session.close()

    # Convert the query results to a dictionary using date as the key and temperature as the value.
    all_temp = list(np.ravel(tobs_data))
    
    # Return the JSON representation of dictionary
    return jsonify(all_temp)     


# Start Date, and Start-End date range routes
# For a given start date or start-end date range, return a JSON list of the minimum temp, average temp, and the maximum temperature

@app.route('/api/v1.0/<start>')
@app.route("/api/v1.0/<start>/<end>")
def start_date_stats(start, end=None):
    if end != None:
        temp_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                            filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    else:
        temp_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).all()

    session.close()

    # Convert the query results to a list.
    temp_list = []
    no_temp_data = False
    for tmin, tavg, tmax in temp_data:
        if tmin == None or tavg == None or tmax == None:
            no_temp_data = True
        temp_list.append(tmin)
        temp_list.append(tavg)
        temp_list.append(tmax)
        
    # Return the JSON representation of dictionary.
    if no_temp_data == True:
        return f"No temperature data found for the given date range. Try another date range."
    else:
        return jsonify(temp_list)

if __name__ == '__main__':
    app.run(debug=True)
