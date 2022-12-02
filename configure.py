import json
from cryptography.fernet import Fernet


host = b'sql6.freesqldatabase.com'
database = b'sql6582223'
user = b'sql6582223'
password = b'pAqH3aPJut'
key = b'VH5wkUrclI6AUkzm4-FuPPdRwsJC2vl1Obyz02BrFbQ='
fernet = Fernet(key)


_host = fernet.encrypt(host)
_database = fernet.encrypt(database)
_user = fernet.encrypt(user)
_password = fernet.encrypt(password)

print('h : ', _host)
print('d : ', _database)    
print('u : ',_user)
print('p : ',_password)

#update_json(config)

