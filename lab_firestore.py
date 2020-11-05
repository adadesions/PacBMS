import firebase_admin
from time import sleep
from datetime import datetime
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate(".adake.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

def send_to_firestore(data_pack):
    now = datetime.now()
    date = now.strftime('%d-%m-%Y')
    time = now.strftime('%H:%M:%S')
    data_pack['timestamp'] = now

    doc_ref = db.collection('pacpower').document('001')
    doc_sub_ref = doc_ref.collection(date).document(time)
    doc_sub_ref.set(data_pack)
    print("===== Data Sent =====")
