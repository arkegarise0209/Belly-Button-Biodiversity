# Dependencies
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, desc
from flask import Flask, jsonify, render_template

# Create App
app = Flask(__name__)

# Connect to sqlite database
engine = create_engine("sqlite:///belly_button_biodiversity.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
session = Session(engine)

# Create variables for tables in database
OTU = Base.classes.otu
Samples = Base.classes.samples
Samples_Metadata = Base.classes.samples_metadata

# Return the dashboard homepage
@app.route("/")
def home():
    return render_template("index.html")

# Return a list of sample names
@app.route("/names")
def names():

    # Empty list for sample ids
    sample_ids = []
    
    # Grab metadata from table
    results = session.query(Samples_Metadata.SAMPLEID)

    # Loop through query & grab ids
    for result in results:
        sample_ids.append("BB_" + str(result[0]))

    return jsonify(sample_ids)

# Return a list of OTU descriptions 
@app.route("/otu")
def otu():

    # Empty list for OTU descriptions
    OTU_desc = []

    # Grab metadata from table
    results = session.query(OTU.lowest_taxonomic_unit_found)

    # Loop through query and grab descriptions
    for result in results:
        OTU_desc.append(result[0])
    
    return jsonify(OTU_desc)

# Returns a json dictionary of sample metadata
@app.route("/metadata/<sample>")
def metadata(sample):
    
    # Grab input
    sample_id = sample.replace("BB_", "")

    # Empty dictionary for data
    sample_metadata = {}

    # Grab metadata from table
    results = session.query(Samples_Metadata)

    # Loop through query & grab data
    for result in results:
        if (sample_id == result.SAMPLEID):
            sample_metadata["AGE"] = result.AGE
            sample_metadata["BBTYPE"] = result.BBTYPE
            sample_metadata["ETHNICITY"] = result.ETHNICITY
            sample_metadata["GENDER"] = result.GENDER
            sample_metadata["LOCATION"] = result.LOCATION
            sample_metadata["SAMPLEID"] = result.SAMPLEID

    return jsonify(sample_metadata)

# Return an integer value for the weekly washing frequency 'WFREQ'
@app.route("/wfreq/<sample>")
def wfreq(sample):

    # Grab input
    sample_id = sample.replace("BB_", "")

    # Grab metadata from table
    results = session.query(Samples_Metadata)

    # Loop through query & grab data
    for result in results:
        if (sample_id == result.SAMPLEID):
            wfreq = result.WFREQ
        
    return jsonify(wfreq)

# Return a list of dictionaries containing sorted lists for "out_ids" and "sample_values"
@app.route("/samples/<sample>")
def samples(sample):

    # Create variable for sample to query for
    sample_query = "Sample." + sample

    # Create empty dictionary and lists to store data
    samples_info = {}
    otu_ids = []
    sample_values = []

    # Grab metadata from table
    results = session.query(Samples.otu_id, sample_query).order_by(desc(sample_query))

    # Loop through query and append results to specific lists
    for result in results:
        otu_ids.append(result[0])
        sample_values.append(result[1])
    
    # Add lists to dictionary
    samples_info = {
        "otu_ids": otu_ids,
        "sample_values": sample_values
    }

    return jsonify(samples_info)



if __name__ == "__main__":
    app.run(debug=True)