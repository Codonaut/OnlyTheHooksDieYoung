import requests

song = requests.get('https://s3.amazonaws.com/wire_jam/uploads/02_Franklins_Tower.mp3')
print song
