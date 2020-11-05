import firebase_admin
from datetime import datetime
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate(".adake.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

now = datetime.now()
date = now.strftime('%d-%m-%Y')
time = now.strftime('%H:%M:%S')
# read data
pac_ref = db.collection('pacpower').document('001')
plant_ref = pac_ref.collection(date)
docs = plant_ref.order_by('timestamp', direction=firestore.Query.DESCENDING).limit(1).stream()

for doc in docs:
    print(f'{doc.id} => {doc.to_dict()}')