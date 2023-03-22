import csv
from Helpers.parser import json_to_protocol

from env import DELIM
delim = DELIM

headers = ['cedula','name','info']
db_path = '../db.csv'
db_path_temp = '../db.temp.csv'

#delim = '/'
#find patient and return protocol-ready
#DO NOT USE 'a+', file CANT BE READ
def find_patient(identifier, value):
    person = dict()
    try:
        with open(db_path, newline='') as f:
            database = csv.DictReader(f, delimiter=delim, fieldnames=headers)
            person = next((p for p in database if p[identifier] == value), False)
    except:
        person = False

    return json_to_protocol(person)

def read_database():
    try:
        with open(db_path,newline='') as f:
            return list(csv.DictReader(f, delimiter=delim, fieldnames=headers))
    except:
        return False

def appendToUser(identifier:str, patient_to_be_updated:dict):
    
    patients_data = read_database()
    if not patients_data:
        return False

    status = True
    #create file if it doesn't exist
    try:
        with open(db_path, 'w', newline='') as p:
            writer = csv.DictWriter(p, delimiter=delim, fieldnames=headers)
            for patient in patients_data:
                if patient[identifier] == patient_to_be_updated[identifier]:
                    #patient['name'] = patient_to_be_updated['name'] #replace name
                    patient['info'] += ' ' + patient_to_be_updated['info'] #append more info
                    writer.writerow(patient)
                else:
                    writer.writerow(patient)
    except:
        status = False
    return status



def create_patient(patient):
    status = True
    try:
        with open(db_path,'a+', newline='') as file:
            writer = csv.DictWriter(file, delimiter=delim, fieldnames=headers)
            writer.writerow(patient)
    except:
        status = False
    return status

#save patient to db
#seems to be working even if the file doesnt exist
def save_patient(patient):
    status = True
    patient_founded = find_patient('cedula',patient['cedula'])
    if(patient_founded):
        #append
        status = appendToUser('cedula', patient)
    else:
        #create user
        status = create_patient(patient)
    return status
            


    
        

