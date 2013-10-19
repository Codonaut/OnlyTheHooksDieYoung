import requests 
from settings import MUSIC_ARCHIVE_API_KEY
import json

limit = 50
hiphop_id = 21
page = 1
track_url = 'http://freemusicarchive.org/api/get/tracks.json?api_key={0}&limit={1}&genre_id={2}&page={3}'.format(
				MUSIC_ARCHIVE_API_KEY, limit, hiphop_id, '{0}')
response = requests.get(track_url.format(page))
response_dict = json.loads(response.content)
print response_dict['dataset'][0]

'''
total = int(response_dict['total'])
print type(total)
all_hiphop = []
while True:
	if response_dict['dataset'] and len(response_dict['dataset']) > 0:
		all_hiphop += response_dict['dataset']
	else:
		break
	page += 1
	response = requests.get(track_url.format(page))
	response_dict = json.loads(response.content)

outfile = open('hiphop.json', 'w')
outfile.write(json.dumps(all_hiphop))
'''