import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendancerealtime-b2410-default-rtdb.firebaseio.com/"
})

ref = db.reference('Students')

data = {
    "321654":
        {
            "name": "Hoang Duy Hieu deptrai",
            "major": "IT1",
            "starting_year":2022,
            "total_attendance": 6,
            "standing" : "G",
            "year": 3,
            "last_attendance_time": "2025-6-1 18:19:00"
        },
    "852741":
        {
            "name": "Emily Blunt",
            "major": "IT2",
            "starting_year":2021,
            "total_attendance": 10,
            "standing" : "B",
            "year": 4,
            "last_attendance_time": "2025-6-1 18:19:00"
        },
    "963852":
        {
            "name": "Elon Musk",
            "major": "ITE-10",
            "starting_year":2018,
            "total_attendance": 7,
            "standing" : "A",
            "year": 7,
            "last_attendance_time": "2025-6-1 18:19:00"
        }
}

for key, value in data.items():
    ref.child(key).set(value)
