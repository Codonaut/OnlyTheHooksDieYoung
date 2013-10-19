import requests
from time import sleep
from pymongo import MongoClient

mongo_client = MongoClient()
mongo_db = mongo_client['HookDB']
collection = mongo_db['gracenote_data']

'''
BPM: [153.125]
Start/end Chorus: 50.4 66.72
'''
url = "http://devapi.gracenote.com/v1/timeline/"
file_path = 'heresy.mp3'
resp = requests.post(url,files={'audiofile':open(file_path,'rb')})
jresp = resp.json()
file_id = jresp['id']

progress = float(jresp['progress'])

while progress < 1:
    sleep(10)
    resp = requests.get(url + str(file_id) +'/')
    jresp = resp.json()
    progress = float(jresp['progress'])

feats = jresp['features']

with open('features.json', 'w') as fn:
	fn.write(str(feats))

collection.insert(feats)


# print the tempo                                                                                                                                               
print feats['BPM']

# find the first chorus                                                                                                                                          
for i in feats['SEGMENT']:
    if i['TYPE'] == 'Chorus':
    		break
print i['START'], i['END']

