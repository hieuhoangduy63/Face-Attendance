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
        },
    "224987": {
        "name": "Donal Trump",
        "major": "BUS-15",
        "starting_year": 2019,
        "total_attendance": 15,
        "standing": "A",
        "year": 6,
        "last_attendance_time": "2025-6-12 14:30:00"
    },
    "234845": {
        "name": "Trấn Thành",
        "major": "ART-08",
        "starting_year": 2020,
        "total_attendance": 23,
        "standing": "A",
        "year": 5,
        "last_attendance_time": "2025-6-11 09:15:00"
    },
    "224999": {
        "name": "Trường Giang",
        "major": "ART-09",
        "starting_year": 2021,
        "total_attendance": 18,
        "standing": "B",
        "year": 4,
        "last_attendance_time": "2025-6-10 16:45:00"
    },
    "224834": {
        "name": "Hiếu Thứ 2",
        "major": "MED-12",
        "starting_year": 2022,
        "total_attendance": 12,
        "standing": "B",
        "year": 3,
        "last_attendance_time": "2025-6-8 11:20:00"
    },
    "236000": {
        "name": "Phương Mỹ Chi",
        "major": "MUS-05",
        "starting_year": 2020,
        "total_attendance": 20,
        "standing": "A",
        "year": 5,
        "last_attendance_time": "2025-6-13 13:10:00"
    },
    "236001": {
        "name": "Pháo",
        "major": "MUS-06",
        "starting_year": 2021,
        "total_attendance": 16,
        "standing": "A",
        "year": 4,
        "last_attendance_time": "2025-6-12 19:30:00"
    },
    "236002": {
        "name": "Phương Ly",
        "major": "MUS-07",
        "starting_year": 2019,
        "total_attendance": 25,
        "standing": "A",
        "year": 6,
        "last_attendance_time": "2025-6-11 15:45:00"
    },
    "236003": {
        "name": "Hoàng Thuy Linh",
        "major": "MUS-08",
        "starting_year": 2018,
        "total_attendance": 28,
        "standing": "A",
        "year": 7,
        "last_attendance_time": "2025-6-13 17:20:00"
    },
    "236004": {
        "name": "Đen Vâu",
        "major": "MUS-09",
        "starting_year": 2020,
        "total_attendance": 22,
        "standing": "A",
        "year": 5,
        "last_attendance_time": "2025-6-10 20:15:00"
    },
    "236005": {
        "name": "Jack",
        "major": "MUS-10",
        "starting_year": 2021,
        "total_attendance": 14,
        "standing": "B",
        "year": 4,
        "last_attendance_time": "2025-6-9 12:30:00"
    },
    "236006": {
        "name": "Người Sắt",
        "major": "ENG-20",
        "starting_year": 2017,
        "total_attendance": 35,
        "standing": "A",
        "year": 8,
        "last_attendance_time": "2025-6-13 08:45:00"
    },
    "226007": {
        "name": "Tom Holland",
        "major": "ART-15",
        "starting_year": 2020,
        "total_attendance": 19,
        "standing": "A",
        "year": 5,
        "last_attendance_time": "2025-6-12 14:20:00"
    },
    "226008": {
        "name": "Người khổng lồ xanh",
        "major": "SCI-25",
        "starting_year": 2016,
        "total_attendance": 40,
        "standing": "A",
        "year": 9,
        "last_attendance_time": "2025-6-11 10:30:00"
    },
    "226009": {
        "name": "Issac",
        "major": "MUS-11",
        "starting_year": 2021,
        "total_attendance": 17,
        "standing": "B",
        "year": 4,
        "last_attendance_time": "2025-6-8 18:45:00"
    },
    "226010": {
        "name": "Quân AP",
        "major": "MUS-12",
        "starting_year": 2022,
        "total_attendance": 11,
        "standing": "B",
        "year": 3,
        "last_attendance_time": "2025-6-7 16:20:00"
    },
    "226011": {
        "name": "Dương Domic",
        "major": "MUS-13",
        "starting_year": 2021,
        "total_attendance": 15,
        "standing": "B",
        "year": 4,
        "last_attendance_time": "2025-6-10 21:10:00"
    },
    "226012": {
        "name": "Quang Hùng",
        "major": "MUS-14",
        "starting_year": 2020,
        "total_attendance": 21,
        "standing": "A",
        "year": 5,
        "last_attendance_time": "2025-6-13 19:25:00"
    },
    "226013": {
        "name": "Anh Tú",
        "major": "MUS-15",
        "starting_year": 2019,
        "total_attendance": 24,
        "standing": "A",
        "year": 6,
        "last_attendance_time": "2025-6-12 13:40:00"
    },
    "226014": {
        "name": "Tlinh",
        "major": "MUS-16",
        "starting_year": 2021,
        "total_attendance": 13,
        "standing": "B",
        "year": 4,
        "last_attendance_time": "2025-6-9 15:50:00"
    },
    "226015": {
        "name": "Orange",
        "major": "MUS-17",
        "starting_year": 2022,
        "total_attendance": 9,
        "standing": "C",
        "year": 3,
        "last_attendance_time": "2025-6-6 11:15:00"
    },
    "226016": {
        "name": "Bảo Anh",
        "major": "MUS-18",
        "starting_year": 2020,
        "total_attendance": 18,
        "standing": "B",
        "year": 5,
        "last_attendance_time": "2025-6-11 17:30:00"
    },
    "226017": {
        "name": "Bích Phương",
        "major": "MUS-19",
        "starting_year": 2019,
        "total_attendance": 26,
        "standing": "A",
        "year": 6,
        "last_attendance_time": "2025-6-13 14:45:00"
    },
    "226018": {
        "name": "Ngô Lan Hương",
        "major": "MUS-20",
        "starting_year": 2018,
        "total_attendance": 30,
        "standing": "A",
        "year": 7,
        "last_attendance_time": "2025-6-12 16:20:00"
    },
    "226019": {
        "name": "Captain America",
        "major": "MIL-30",
        "starting_year": 2015,
        "total_attendance": 45,
        "standing": "A",
        "year": 10,
        "last_attendance_time": "2025-6-13 07:30:00"
    },
    "226020": {
        "name": "Thần Sấm",
        "major": "PHY-35",
        "starting_year": 2014,
        "total_attendance": 50,
        "standing": "A",
        "year": 11,
        "last_attendance_time": "2025-6-12 22:15:00"
    },
    "226021": {
        "name": "Doctor Strange",
        "major": "MED-40",
        "starting_year": 2013,
        "total_attendance": 55,
        "standing": "A",
        "year": 12,
        "last_attendance_time": "2025-6-13 06:45:00"
    },
    "226022": {
        "name": "Loki",
        "major": "PSY-45",
        "starting_year": 2016,
        "total_attendance": 32,
        "standing": "B",
        "year": 9,
        "last_attendance_time": "2025-6-10 23:30:00"
    }
}
for key, value in data.items():
    ref.child(key).set(value)
