from flask import Flask, render_template, redirect,jsonify
import os
import pandas as pd 
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

app= Flask(__name__)

db = os.path.join('belly_button_biodiversity.sqlite')
engine = create_engine((f"sqlite:///{db}"))
Base= automap_base()
Base.prepare(engine,reflect="True")

Metadata= Base.classes.samples_metadata
OTU= Base.classes.otu
Samples= Base.classes.samples


session=Session(engine)

@app.route("/")
def home():
  
  # return template and data
    return render_template("index.html")

@app.route('/names')

def names():
    names=session.query(Samples).statement
    df=pd.read_sql_query(names,session.bind)
    df.set_index("otu_id",inplace=True)
    
    return jsonify(list (df.columns))


@app.route('/otu')

def otu():
    otu_list =session.query(OTU.lowest_taxonomic_unit_found).all()
    otu_units = list(np.ravel(otu_list))
    
    return jsonify(otu_units)


@app.route('/metadata/<sample>')

def metadata(sample):
   
    Metadatas=session.query(Metadata.AGE,\
                            Metadata.BBTYPE,\
                            Metadata.ETHNICITY,\
                            Metadata.GENDER,\
                            Metadata.LOCATION,\
                            Metadata.SAMPLEID).\
        filter(Metadata.SAMPLEID == sample[3:]).all()
    
    list_metadata =[]
    
    for item in Metadatas:
        sample_dict = {}
        sample_dict["AGE"] = item.AGE
        sample_dict["BBTYPE"] =item.BBTYPE
        sample_dict["ETHNICITY"] =item.ETHNICITY
        sample_dict["GENDER"] = item.GENDER
        sample_dict["LOCATION"] = item.LOCATION
        sample_dict["SAMPLEID"] = item.SAMPLEID

        list_metadata.append(sample_dict)

    return jsonify(list_metadata)

@app.route('/wfreq/<sample>')

def Wfreq(sample):
   samples_metadatas=session.query(Metadata.WFREQ).\
                                    filter(Metadata.SAMPLEID==sample[3:]).all()

    
   return jsonify(samples_metadatas)

@app.route('/samples/<sample>')
def samples(sample):
    results=session.query(Samples.otu_id,getattr(Samples,sample)).\
        filter(getattr(Samples,sample) !=0).\
        order_by(getattr(Samples,sample).desc()).all()

    otu_ids={"otu_ids":list (x[0] for x in results)}
    sample_values= {"sample_values": list (x[1] for x in results)}


    
    return jsonify(otu_ids,sample_values)


if __name__ == "__main__":
    app.run(debug=True)

