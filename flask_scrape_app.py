import numpy as np

import pymongo
import json

from flask import Flask, jsonify, render_template, redirect, url_for
import scrape_mars as sm


#################################################
# Database Setup
#################################################


#flask app setup
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
@app.route("/home")
def mars_info():

     # Create connection variable
    conn = 'mongodb://localhost:27017'

    # Pass connection to the pymongo instance.
    client = pymongo.MongoClient(conn)

    # Connect to a database. Will create one if not already available.
    db = client.mars_db
   
    mars_info = list(db.mars.find())

    return render_template('index.html', mars_info=mars_info)


@app.route("/scrape")
def scrape():
    """Initiate the scraping procedure and store results in mongo"""
    # Query all passengers
    latest_mars_info = sm.scrape()

    # Create connection variable
    conn = 'mongodb://localhost:27017'

    # Pass connection to the pymongo instance.
    client = pymongo.MongoClient(conn)

    # Connect to a database. Will create one if not already available.
    db = client.mars_db

    # Drops collection if available to remove duplicates
    db.mars.drop()

    # Creates a collection in the database and inserts two documents
    db.mars.insert_many(latest_mars_info)
    
    return redirect("/home", code=302)


if __name__ == '__main__':
    app.run(debug=True)
