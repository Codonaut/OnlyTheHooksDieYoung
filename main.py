from settings import *
import os
import requests
import json
import random 
from utils import download_track, download_track_from_s3
from pymongo import MongoClient
from urlparse import urlparse
from flask import (Flask, request, session, g, redirect, 
				   url_for, abort, render_template, jsonify, flash)
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from rq import Queue
from tasks import get_track_data, push_track_to_s3
from worker import conn


DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
boto_conn = S3Connection(AWS_ACCESS_KEY, AWS_SECRET_KEY)
bucket = boto_conn.get_bucket('only-the-hooks')
s3_url_format = 'https://only-the-hooks.s3.amazonaws.com/{end_path}'
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

@app.route('/clear_queue')
def clear_queue():
	q.queue.clear()
	return "cleared"

@app.route('/')
def index():
	tracks = track_collection.find()
	return render_template('track_select.html', tracks=tracks)

@app.route("/test_audio")
def test_audio():
	return render_template('test_audio.html')

@app.route('/view_track/<track_id>')
def view_track(track_id):
	track = track_collection.find({'track_id': track_id})
	if track.count() > 0:
		return str(track[0])
	else:
		return "None"

def get_track_url_and_intervals(track):
	if not track:
		return None
	url = s3_url_format.format(end_path=track['s3_path'])
	grace_data = grace_collection.find_one({'track_id': track['track_id']})
	if not grace_data:
		return None
	segments = grace_data['SEGMENT']
	beats = grace_data['BEATS']
	for i in xrange(len(beats)-1):
		for seg in segments:
			if beats[i] < seg['START'] and beats[i+1] > seg['START']:
				seg['START'] = beats[i] 
	return (url, segments)

@app.route('/get_a_track/<track_id>')
@app.route('/get_a_track')
def get_track_for_frontend(track_id=None):
	url_tuple = None
	i = 0
	while not url_tuple and i < 5:
		if not track_id:
			curr_track_id = random.randint(0, grace_collection.find().count())
			grace = grace_collection.find().limit(-1).skip(rand_number).next()
		else:
			grace = grace_collection.find_one({'track_id': track_id})
		url_tuple = get_track_url_and_intervals(track_collection.find_one({'track_id': grace['track_id']}))
		i += 1
	if i == 5:
		return "Not good enough."
	else:
		return jsonify(url=url_tuple[0], intervals=url_tuple[1])

@app.route('/kickoff_grace_analysis')
def count_dem_words():
	all_tracks = track_collection.find()
	for track in all_tracks:
		if int(track['track_id']) == 63807:
			continue
		elif grace_collection.find_one({'track_id': track['track_id']}):
			continue
		result = q.enqueue(get_track_data, track['track_id'])
	return 'Analyzing...'

@app.route('/kickoff_s3_upload')
def add_to_s3():
	all_grace = grace_collection.find()
	for grace in all_grace:
		result = q.enqueue(push_track_to_s3, grace['track_id'])
	return "getting dem tracks"

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
