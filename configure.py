import json
from cryptography.fernet import Fernet

f = open('config.json','r+')
config  = json.load(f)
server_creds = config['WebPage'][0]

str = "Hello World"
key = b'VH5wkUrclI6AUkzm4-FuPPdRwsJC2vl1Obyz02BrFbQ='
fernet = Fernet(key)

config['WasServerUpdated'] = "true"

def update_json(object):
    f.seek(0)
    json.dump(object, f, indent=4, separators=(", ", ": "), sort_keys=True)
    f.truncate()

update_json(config)

