from pymongo import MongoClient
import requests
import os
from utils import download_track_from_s3

MONGO_URL = os.environ.get('MONGOHQ_URL')
if MONGO_URL:
	conn = MongoClient(MONGO_URL)
	db = conn[urlparse(MONGO_URL).path[1:]]
	track_collection = db['track_collection']
	grace_collection = db['grace_data']
else:
	# Not on an app with the MongoHQ add-on, do some localhost action
	conn = MongoClient()
	db = conn['HookDB']
	track_collection = db['track_collection']
	grace_collection = db['grace_data']

'''
BPM: [153.125]
Start/end Chorus: 50.4 66.72
'''
def get_track_data(track_id):
	url = "http://devapi.gracenote.com/v1/timeline/"
	track = track_collection.find({'track_id': track_id})[0]
	audio_file = download_track_from_s3(track['s3_path'])

	resp = requests.post(url,files={'audiofile': audio_file})
	jresp = resp.json()
	file_id = jresp['id']
	progress = float(jresp['progress'])

	while progress < 1:
	    sleep(10)
	    resp = requests.get(url + str(file_id) +'/')
	    jresp = resp.json()
	    progress = float(jresp['progress'])

	feats = jresp['features']
	feats['track_id'] = track_id
	grace_collection.insert(feats)
	return "Saved the info"
