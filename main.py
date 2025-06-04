import cv2
import os
import pickle
import numpy as np
import cvzone
import face_recognition
from EncodeGenerator import encodeListKnownWithIds, studentIds
from face_recognition import compare_faces
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime


if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': "https://faceattendancerealtime-b2410-default-rtdb.firebaseio.com/",
        'storageBucket': "faceattendancerealtime-b2410.firebasestorage.app"
    })

bucket = storage.bucket()

cap = cv2.VideoCapture(0)
cap.set(3,640)  #because of using graphic
cap.set(4, 480)


imgBackground = cv2.imread('Resources/background.png')

#importing the mode images into a list
folderModePath = 'Resources/Modes'
modePathList = os.listdir(folderModePath)
imgModeList = []
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))

#print(len(imgModeList))

# Load the encoding file
print("Loading Encode File ...")
file = open('EncodeFile.p', 'rb')
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, studentIds = encodeListKnownWithIds
#print(studentIds)
print("Encode File Loaded")

modeType = 0
counter = 0
id = -1
unknownCounter = 0
imgStudent = []

while True:
    success, img = cap.read()

    imgS = cv2.resize(img, (0,0) , None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    imgBackground[162:162+480,55:55+640] = img
    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

    if faceCurFrame:
        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)

            matchIndex = np.argmin(faceDis)

            # Vẽ khung cho khuôn mặt được phát hiện
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
            imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)

            if matches[matchIndex]:
                # Khuôn mặt được nhận diện
                print("Known Face Detected")
                print(studentIds[matchIndex])
                id = studentIds[matchIndex]
                unknownCounter = 0  # Reset unknown counter

                if counter == 0:
                    cvzone.putTextRect(imgBackground, "Loading", (275, 400))
                    cv2.imshow("Face Attendance", imgBackground)
                    cv2.waitKey(1)
                    counter = 1
                    modeType = 1
            else:
                # Khuôn mặt không được nhận diện
                print("Unknown Face Detected")
                if unknownCounter == 0:
                    unknownCounter = 1
                id = -1
                counter = 0
                modeType = 0

        # Xử lý hiển thị "Not Recognize"
        if unknownCounter != 0:
            cvzone.putTextRect(imgBackground, "Not Recognize", (250, 400))
            unknownCounter += 1
            if unknownCounter >= 30:  # Hiển thị trong 30 frames (~1 giây)
                unknownCounter = 0

        # Xử lý cho recognized faces (code cũ)
        if counter != 0:
            if counter == 1:
                # Get the data with error handling
                studentInfo = db.reference(f'Students/{id}').get()
                print(f"Student ID: {id}")
                print(f"Student Info: {studentInfo}")

                # Kiểm tra xem studentInfo có tồn tại không
                if studentInfo is None:
                    print(f"Không tìm thấy thông tin sinh viên với ID: {id}")
                    modeType = 3  # Chuyển sang mode lỗi
                    counter = 0
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
                else:
                    try:
                        # Get the image from the storage
                        blob = bucket.get_blob(f'Images/{id}.png')
                        if blob.exists():
                            array = np.frombuffer(blob.download_as_string(), np.uint8)
                            imgStudent = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)
                        else:
                            print(f"Không tìm thấy ảnh sinh viên với ID: {id}")
                            imgStudent = np.zeros((216, 216, 3), dtype=np.uint8)

                        # Update data of attendance
                        if 'last_attendance_time' in studentInfo and studentInfo['last_attendance_time']:
                            datetimeObject = datetime.strptime(studentInfo['last_attendance_time'],
                                                               "%Y-%m-%d %H:%M:%S")
                            secondsElapsed = (datetime.now() - datetimeObject).total_seconds()
                            print(f"Seconds elapsed: {secondsElapsed}")
                        else:
                            secondsElapsed = 31
                            print("Chưa có lịch sử điểm danh")

                        if secondsElapsed > 30:
                            ref = db.reference(f'Students/{id}')
                            if 'total_attendance' not in studentInfo or studentInfo['total_attendance'] is None:
                                studentInfo['total_attendance'] = 0

                            studentInfo['total_attendance'] += 1
                            ref.child('total_attendance').set(studentInfo['total_attendance'])
                            ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                            print(f"Đã cập nhật điểm danh cho sinh viên {id}")
                        else:
                            modeType = 3
                            counter = 0
                            imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
                            print("Điểm danh quá gần, cần chờ ít nhất 30 giây")

                    except Exception as e:
                        print(f"Lỗi khi xử lý dữ liệu sinh viên: {e}")
                        modeType = 3
                        counter = 0
                        imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

            if modeType != 3 and studentInfo is not None:
                if 10 < counter < 20:
                    modeType = 2

                imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

                if counter <= 10:
                    # Hiển thị thông tin sinh viên
                    total_attendance = studentInfo.get('total_attendance', 0)
                    major = studentInfo.get('major', 'N/A')
                    standing = studentInfo.get('standing', 'N/A')
                    year = studentInfo.get('year', 'N/A')
                    starting_year = studentInfo.get('starting_year', 'N/A')
                    name = studentInfo.get('name', 'Unknown')

                    cv2.putText(imgBackground, str(total_attendance), (861, 125),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(major), (1006, 550),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(id), (1006, 493),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(standing), (910, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                    cv2.putText(imgBackground, str(year), (1025, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                    cv2.putText(imgBackground, str(starting_year), (1125, 125),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

                    (w, h), _ = cv2.getTextSize(name, cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                    offset = (414 - w) // 2
                    cv2.putText(imgBackground, str(name), (808 + offset, 445),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)

                    if imgStudent is not None and imgStudent.size > 0:
                        imgBackground[175:175 + 216, 909:909 + 216] = imgStudent

                counter += 1

                if counter >= 20:
                    counter = 0
                    modeType = 0
                    studentInfo = []
                    imgStudent = []
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
    else:
        # Không phát hiện khuôn mặt nào
        modeType = 0
        counter = 0
        unknownCounter = 0  # Reset unknown counter
        id = -1


    cv2.imshow("Face Attendance", imgBackground)
    cv2.waitKey(1)

