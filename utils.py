from boto.s3.connection import S3Connection
from boto.s3.key import Key

boto_conn = S3Connection(AWS_ACCESS_KEY, AWS_SECRET_KEY)
bucket = boto_conn.get_bucket('only-the-hooks')
s3_url_format = 'https://twilio-rapper.s3.amazonaws.com/{end_path}'

def download_track(track_url, s3_path):
	''' Downloads a track at track_url from free music archive and sends to s3 '''
	audio_file = request.get(track_url + '/download')
	s3_key = Key(bucket)
	s3_key.key = s3_path
	s3_key.set_contents_from_string(audio_file)

def download_track_from_s3(s3_path):
	s3_key = Key(bucket)
	s3_key.key = s3_path
	return s3_key.get_contents_as_string()