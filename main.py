from settings import *
import os
import requests
import json
from utils import download_track, download_track_from_s3
from pymongo import MongoClient
from urlparse import urlparse
from flask import (Flask, request, session, g, redirect, 
				   url_for, abort, render_template, flash)
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from rq import Queue
from tasks import get_track_data
from worker import conn


DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
boto_conn = S3Connection(AWS_ACCESS_KEY, AWS_SECRET_KEY)
bucket = boto_conn.get_bucket('only-the-hooks')
s3_url_format = 'https://twilio-rapper.s3.amazonaws.com/{end_path}'
q = Queue(connection=conn)

# Make sure to set this url
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


@app.route('/')
def index():
	return 'Hey there'

@app.route('/view_track/<track_id>')
def view_track(track_id):
	track = track_collection.find({'track_id': track_id})
	if track.count() > 0:
		return str(track[0])
	else:
		return "none"

@app.route('/kickoff_grace_analysis')
def count_dem_words():
	all_tracks = track_collection.find()
	print track['track_id']
	for track in all_tracks:
		if int(track['track_id']) == 63807:
			continue
		result = q.enqueue(get_track_data, track['track_id'])
	return 'Analyzing...'

@app.route('/view_grace_data')
def view_grace_data():
	grace = grace_collection.find()
	al = []
	for g in grace:
		al.append(g)
	print al
	return str([(a['BPM'], a['track_id']) for a in al])

def download_page_helper(page):
	limit = 50
	hiphop_id = 21
	track_url = 'http://freemusicarchive.org/api/get/tracks.json?api_key={0}&limit={1}&genre_id={2}&page={3}'.format(
					MUSIC_ARCHIVE_API_KEY, limit, hiphop_id, page)
	response = requests.get(track_url)
	response_dict = json.loads(response.content)
	if response_dict['dataset'] and len(response_dict['dataset']) > 0:
		for track in response_dict['dataset']:
			s3_path = 'tracks/{}'.format(track['track_file'])
			track['s3_path'] = s3_path
			track_collection.insert(track)
	return "Got them :)"

@app.route('/download_page/<page>')
def download_page(page):
	return download_page_helper(int(page))

@app.route('/view_all_tracks')
def view_tracks():
	track_names = [unicode(t['track_title']).encode('ascii', errors='ignore') for t in track_collection.find()]
	return 'Total of {0} tracks.<br/>  \n{1}'.format(len(track_names), '<br/>'.join(track_names))



if not MONGO_URL:
	if __name__ == '__main__':
		app.run(port=8000)
