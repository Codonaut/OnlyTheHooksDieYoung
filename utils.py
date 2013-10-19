from boto.s3.connection import S3Connection
from boto.s3.key import Key
from settings import *	
import requests

boto_conn = S3Connection(AWS_ACCESS_KEY, AWS_SECRET_KEY)
bucket = boto_conn.get_bucket('only-the-hooks')
s3_url_format = 'https://twilio-rapper.s3.amazonaws.com/{end_path}'

def download_track(track_url, s3_path):
	''' Downloads a track at track_url from free music archive and sends to s3 '''
	return  requests.get(track_url + '/download').content


def download_track_to_disk(track_url, filetype):
	track_content = download_track(track_url)
	filename = 't1.{}'.format(filetype)
	with open(filename, 'wb') as fn:
		fn.write(track_content)
	return filename


'''s3_key = Key(bucket)
s3_key.key = s3_path
s3_key.set_contents_from_string(audio_file)
return audio_file
'''

def download_track_from_s3(s3_path):
	s3_key = Key(bucket)
	s3_key.key = s3_path
	return s3_key.get_contents_as_string()