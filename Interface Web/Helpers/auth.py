import csv
from env import DELIM
delim = DELIM

db_path = 'auth.csv'
headers = ['user', 'password', 'operation']
#delim = '/'
#if file doesnt exist DO NOT USE 'a+', file CANT BE READ
def authenticate_user(user:dict):
    user_found = dict()
    try:
        with open(db_path,newline='') as file:
            database = csv.DictReader(file, delimiter=delim, fieldnames=headers)
            user_found = next((u for u in database if u['user'] == user['user']), False)
    #revisar si usuario w podria leer, si es asi, lo debajo de esta linea debe ser repensado y modificado
    #w puede leer
    except:
        user_found = False
    
    if not user_found:
        return False
    if user_found["password"] != user["password"]:
        return False
    if user_found["operation"] == 'r' and (user_found["operation"] != user["operation"]):
        return False
    return True


