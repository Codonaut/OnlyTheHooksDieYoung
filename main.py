from settings import *
import os
import requests
import json
from pymongo import MongoClient
from flask import (Flask, request, session, g, redirect, 
				   url_for, abort, render_template, flash)
from boto.s3.connection import S3Connection
from boto.s3.key import Key

DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
boto_conn = S3Connection(AWS_ACCESS_KEY, AWS_SECRET_KEY)
bucket = boto_conn.get_bucket('only-the-hooks')
s3_url_format = 'https://twilio-rapper.s3.amazonaws.com/{end_path}'

# Make sure to set this url
MONGO_URL = os.environ.get('MONGOHQ_URL')
if MONGO_URL:
	conn = MongoClient(MONGO_URL)
	db = conn['HookDB']
	track_collection = db['track_collection']
else:
	# Not on an app with the MongoHQ add-on, do some localhost action
	conn = MongoClient()
	db = conn['HookDB']
	track_collection = db['track_collection']


def download_track(track_url, s3_path):
	''' Downloads a track at track_url from free music archive and sends to s3 '''
	audio_file = request.get(track_url + '/download')
	s3_key = Key(bucket)
	s3_key.key = s3_path
	s3_key.set_contents_from_string(audio_file)

@app.route('/')
def index():
	return 'Hey there'

@app.route('/download_all')
def download_all_free_tracks():
	limit = 50
	hiphop_id = 21
	page = 1
	track_url = 'http://freemusicarchive.org/api/get/tracks.json?api_key={0}&limit={1}&genre_id={2}&page={3}'.format(
					MUSIC_ARCHIVE_API_KEY, limit, hiphop_id, '{0}')
	response = requests.get(track_url.format(page))
	response_dict = json.loads(response.content)

	total = int(response_dict['total'])
	all_hiphop = []
	while True:
		if response_dict['dataset'] and len(response_dict['dataset']) > 0:
			for track in response_dict['dataset']:
				s3_path = 'tracks/{}'.format(track['track_file'])
				track['s3_path'] = s3_path
				track_collection.insert(track)
		else:
			break
		page += 1
		response = requests.get(track_url.format(page))
		response_dict = json.loads(response.content)
	return "Got them :)"


if not MONGO_URL:
	if __name__ == '__main__':
		app.run(port=8000)
