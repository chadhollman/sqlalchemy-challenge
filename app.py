# Import the dependencies.
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create the Flask app
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available API routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create session from Python to the DB
    session = Session(engine)
    
    # Get the most recent date and one year ago
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    one_year_ago = dt.datetime.strptime(most_recent_date, '%Y-%m-%d') - dt.timedelta(days=365)

    # Query precipitation data
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()
    session.close()

    # Convert to dictionary and return JSON
    precipitation_dict = {date: prcp for date, prcp in results}
    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    # Create session
    session = Session(engine)

    # Query station list
    results = session.query(Station.station).all()
    session.close()

    # Return station list as JSON
    station_list = [station[0] for station in results]
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create session
    session = Session(engine)

    # Query the most active station
    most_active_station = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).first()[0]

    # Get the most recent date and one year ago
    one_year_ago = dt.datetime.strptime(session.query(func.max(Measurement.date)).scalar(), '%Y-%m-%d') - dt.timedelta(days=365)

    # Query temperature observations for the most active station
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station, Measurement.date >= one_year_ago).all()

    session.close()

    # Convert to dictionary and return JSON
    tobs_dict = {date: tobs for date, tobs in results}
    return jsonify(tobs_dict)

@app.route("/api/v1.0/<start>")
def temperature_from_start(start):
    """Returns the min, max, and average temperatures from the given start date to the end of the dataset."""
    session = Session(engine)

    # Query to calculate min, max, and avg temperature from the start date onwards
    results = session.query(func.min(Measurement.tobs), 
                            func.avg(Measurement.tobs), 
                            func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    session.close()

    # Create a dictionary for the results
    temp_stats = {
        "Start Date": start,
        "Min Temperature": results[0][0],
        "Avg Temperature": results[0][1],
        "Max Temperature": results[0][2]
    }

    return jsonify(temp_stats)

@app.route("/api/v1.0/<start>/<end>")
def temperature_between_dates(start, end):
    """Returns the min, max, and average temperatures between the given start and end dates."""
    session = Session(engine)

    # Query to calculate min, max, and avg temperature between the start and end dates
    results = session.query(func.min(Measurement.tobs), 
                            func.avg(Measurement.tobs), 
                            func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

    session.close()

    # Create a dictionary for the results
    temp_stats = {
        "Start Date": start,
        "End Date": end,
        "Min Temperature": results[0][0],
        "Avg Temperature": results[0][1],
        "Max Temperature": results[0][2]
    }

    return jsonify(temp_stats)

# To run the application
if __name__ == "__main__":
    app.run(debug=True)
