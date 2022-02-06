from flask import Flask, request, redirect, session, url_for, Response, json, render_template, send_from_directory
from werkzeug.utils import secure_filename
from flask.json import jsonify
import json
import os
import random
import time
import requests
from pprint import pprint
from google.cloud import datastore
from google.cloud import storage
from flask_cors import CORS
from bson import ObjectId


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)




app = Flask(__name__)
app.config.from_object(__name__)
CORS(app)



def uploadtogcp(filename):
    # Explicitly use service account credentials by specifying the private key
    # file.
    storage_client = storage.Client.from_service_account_json('gc.json')

    # Make an authenticated API request
    ##buckets = list(storage_client.list_buckets())
    ##print(buckets)

    bucketname = "thegjar"
    # filename = sys.argv[2]


    bucket = storage_client.get_bucket(bucketname)

    destination_blob_name = filename
    source_file_name = filename

    blob = bucket.blob(destination_blob_name)
    blob.cache_control = "no-cache"

    blob.upload_from_filename(source_file_name)
    #blob.make_public()
    blob.cache_control = "no-cache"

    print('File {} uploaded to {}.'.format(source_file_name, destination_blob_name))
    return destination_blob_name




@app.route("/upload", methods=["POST"])
def fileupload2():

    if 'file' not in request.files:
          return "No file part"
    file = request.files['file']
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
      return "No selected file"
    if file:
        
  
        filename = secure_filename(file.filename+str(int(time.time()))[:-5]+".m4a")
        file.save(filename)
        blob = uploadtogcp(filename)

        getnft(blob)


        retjson = {}

        return json.dumps({"status":"Success!","uri":"https://storage.googleapis.com/thegjar/"+blob})



        # return 'file uploaded successfully'
    
    return 'file not uploaded successfully'





if __name__ == "__main__":
    app.run(debug=True, host = 'localhost', port = 8002)