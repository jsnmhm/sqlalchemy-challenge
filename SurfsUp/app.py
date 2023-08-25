# Import the dependencies.
import sqlalchemy
import numpy as np
import pandas as pd
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
from datetime import datetime
from dateutil.relativedelta import relativedelta 


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)


# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#get the max date and the date 12 months prior
end_date_str = session.query(func.max(measurement.date)).scalar()

end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()

start_date = end_date - relativedelta(years = 1)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precip():
    session = Session(engine)

    qry = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date.between(start_date, end_date)).\
            order_by(measurement.date)
    
    session.close()
    
    results = qry.all()

    precip = []
    
    for date, prcp in results:
        precip_dict = {}
        precip_dict[date] = prcp
        precip.append(precip_dict)

    return jsonify(precip)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    qry = session.query(station.name).all()
    session.close()
    stations = list(np.ravel(qry))
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    qry = session.query(measurement.date, measurement.tobs).\
    filter(
        measurement.station == "USC00519281",
        measurement.date.between(start_date, end_date)
    )

    session.close()
    
    results = qry.all()    

    all_tobs = []

    for date, tobs in results:
        tobs_dict = {}
        tobs_dict[date] = tobs
        all_tobs.append(tobs_dict)

    return jsonify(all_tobs)

@app.route("/api/v1.0/<start>")
def from_date(start):
    session = Session(engine)

    converted_date = datetime.strptime(start, "%Y-%m-%d").date()
    

    qry = session.query(measurement.date, measurement.tobs).\
    filter(measurement.date >= converted_date)

    results = qry.all()

    df = pd.DataFrame(results, columns=["date", "tobs"])

    TMIN = df["tobs"].min()
    TMAX = df["tobs"].max()
    TAVG = df["tobs"].mean()

    temp_stats = [TMIN, TMAX, TAVG]

    return jsonify(temp_stats)

@app.route("/api/v1.0/<start>/<end>")
def to_date(start, end):
    session = Session(engine)

    converted_start_date = datetime.strptime(start, "%Y-%m-%d").date()
    converted_end_date = datetime.strptime(end, "%Y-%m-%d").date()
    print(converted_start_date, converted_end_date)
    

    qry = session.query(measurement.date, measurement.tobs).\
    filter(measurement.date.between(converted_start_date, converted_end_date))

    results = qry.all()

    df = pd.DataFrame(results, columns=["date", "tobs"])

    TMIN = df["tobs"].min()
    TMAX = df["tobs"].max()
    TAVG = df["tobs"].mean()

    temp_stats = [TMIN, TMAX, TAVG]

    return jsonify(temp_stats)




if __name__ == "__main__":
    app.run(debug=True)

