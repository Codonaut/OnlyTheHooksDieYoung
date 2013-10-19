from pymongo import MongoClient
import requests
from urlparse import urlparse
from settings import *
from time import sleep
import os
from utils import download_track_to_disk

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
	print track_id
	# url = "http://devapi.gracenote.com/v1/timeline/"
	url = 'http://54.214.42.167/audio/'
	track = track_collection.find({'track_id': track_id})[0]
	print str(track)
	audio_file = download_track_to_disk(track['track_url'], track['track_file'].split('.')[-1])

	resp = requests.post(url,files={'audiofile': open(audio_file, 'rb')})
	jresp = resp.json()
	print jresp.keys()
	file_id = jresp['id']
	progress = float(jresp['progress'])

	while progress < 1:
	    sleep(10)
	    resp = requests.get(url + str(file_id) +'/')
	    jresp = resp.json()
	    progress = float(jresp['progress'])
	    print progress

	feats = jresp['features']
	feats['track_id'] = track_id
	grace_collection.insert(feats)
	return "Saved the info"
