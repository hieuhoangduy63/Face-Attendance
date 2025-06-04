import cv2
import os
import pickle
import numpy as np
import face_recognition
from EncodeGenerator import encodeListKnownWithIds, studentIds
from face_recognition import compare_faces
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import threading
import time


class ModernAttendanceSystem:
    def __init__(self):
        # Initialize Firebase
        if not firebase_admin._apps:
            cred = credentials.Certificate("serviceAccountKey.json")
            firebase_admin.initialize_app(cred, {
                'databaseURL': "https://faceattendancerealtime-b2410-default-rtdb.firebaseio.com/",
                'storageBucket': "faceattendancerealtime-b2410.firebasestorage.app"
            })

        self.bucket = storage.bucket()

        # Load encodings
        print("Loading Encode File ...")
        with open('EncodeFile.p', 'rb') as file:
            encodeListKnownWithIds = pickle.load(file)
        self.encodeListKnown, self.studentIds = encodeListKnownWithIds
        print("Encode File Loaded")

        # Camera setup
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 640)
        self.cap.set(4, 480)

        # State variables
        self.modeType = 0
        self.counter = 0
        self.id = -1
        self.unknownCounter = 0
        self.studentInfo = None
        self.imgStudent = None
        self.face_locations = []
        self.status_text = "System Ready"
        self.status_color = "#48bb78"

        # Create GUI
        self.setup_gui()

        # Start camera thread
        self.camera_thread = threading.Thread(target=self.process_camera, daemon=True)
        self.camera_thread.start()

        # Start GUI update thread
        self.gui_thread = threading.Thread(target=self.update_gui, daemon=True)
        self.gui_thread.start()

    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("🎓 Modern Face Attendance System")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f8f9fa')

        # Configure styles
        style = ttk.Style()
        style.theme_use('clam')

        # Configure custom styles
        style.configure('Title.TLabel', font=('Segoe UI', 24, 'bold'), foreground='#2d3748', background='#f8f9fa')
        style.configure('Subtitle.TLabel', font=('Segoe UI', 12), foreground='#718096', background='#f8f9fa')
        style.configure('Status.TLabel', font=('Segoe UI', 14, 'bold'), background='#f8f9fa')
        style.configure('StudentName.TLabel', font=('Segoe UI', 20, 'bold'), foreground='white', background='#667eea')
        style.configure('StudentInfo.TLabel', font=('Segoe UI', 12), foreground='white', background='#667eea')
        style.configure('Card.TFrame', background='white', relief='solid', borderwidth=1)

        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=2)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))

        ttk.Label(header_frame, text="🎓 ATTENDANCE SYSTEM", style='Title.TLabel').pack()
        ttk.Label(header_frame, text="Advanced Face Recognition Technology", style='Subtitle.TLabel').pack()

        # Left side - Camera section
        camera_frame = ttk.LabelFrame(main_frame, text="📹 Live Camera Feed", padding="15")
        camera_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        camera_frame.columnconfigure(0, weight=1)
        camera_frame.rowconfigure(0, weight=1)

        # Camera display
        self.camera_label = ttk.Label(camera_frame, text="Initializing camera...",
                                      background='#1a202c', foreground='white',
                                      font=('Segoe UI', 16), anchor='center')
        self.camera_label.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))

        # Status section
        status_frame = ttk.Frame(camera_frame)
        status_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        status_frame.columnconfigure(1, weight=1)

        ttk.Label(status_frame, text="Status:", font=('Segoe UI', 12, 'bold')).grid(row=0, column=0, sticky=tk.W)
        self.status_label = ttk.Label(status_frame, text=self.status_text, style='Status.TLabel')
        self.status_label.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))

        # Statistics
        stats_frame = ttk.LabelFrame(camera_frame, text="📊 Statistics", padding="10")
        stats_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))

        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill=tk.X)
        stats_grid.columnconfigure(0, weight=1)
        stats_grid.columnconfigure(1, weight=1)

        # Today's attendance
        today_frame = ttk.Frame(stats_grid, style='Card.TFrame', padding="15")
        today_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Label(today_frame, text="24", font=('Segoe UI', 24, 'bold'), foreground='#667eea').pack()
        ttk.Label(today_frame, text="Today's Attendance", font=('Segoe UI', 10)).pack()

        # Total students
        total_frame = ttk.Frame(stats_grid, style='Card.TFrame', padding="15")
        total_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0))
        ttk.Label(total_frame, text="156", font=('Segoe UI', 24, 'bold'), foreground='#764ba2').pack()
        ttk.Label(total_frame, text="Total Students", font=('Segoe UI', 10)).pack()

        # Right side - Student info section
        self.info_frame = ttk.LabelFrame(main_frame, text="👤 Student Information", padding="15")
        self.info_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.info_frame.columnconfigure(0, weight=1)

        # Default message
        self.setup_default_info()

    def setup_default_info(self):
        # Clear existing widgets
        for widget in self.info_frame.winfo_children():
            widget.destroy()

        default_frame = ttk.Frame(self.info_frame)
        default_frame.pack(expand=True, fill=tk.BOTH)
        default_frame.columnconfigure(0, weight=1)

        ttk.Label(default_frame, text="👤", font=('Segoe UI', 48)).pack(pady=20)
        ttk.Label(default_frame, text="No Face Detected",
                  font=('Segoe UI', 16, 'bold'), foreground='#718096').pack()
        ttk.Label(default_frame, text="Please position yourself\nin front of the camera",
                  font=('Segoe UI', 12), foreground='#a0aec0', justify=tk.CENTER).pack(pady=10)

    def setup_unknown_info(self):
        # Clear existing widgets
        for widget in self.info_frame.winfo_children():
            widget.destroy()

        unknown_frame = ttk.Frame(self.info_frame)
        unknown_frame.pack(expand=True, fill=tk.BOTH)
        unknown_frame.columnconfigure(0, weight=1)

        ttk.Label(unknown_frame, text="❌", font=('Segoe UI', 48)).pack(pady=20)
        ttk.Label(unknown_frame, text="Face Not Recognized",
                  font=('Segoe UI', 16, 'bold'), foreground='#f56565').pack()
        ttk.Label(unknown_frame, text="Please register or\ncontact administrator",
                  font=('Segoe UI', 12), foreground='#feb2b2', justify=tk.CENTER).pack(pady=10)

    def setup_loading_info(self):
        # Clear existing widgets
        for widget in self.info_frame.winfo_children():
            widget.destroy()

        loading_frame = ttk.Frame(self.info_frame)
        loading_frame.pack(expand=True, fill=tk.BOTH)
        loading_frame.columnconfigure(0, weight=1)

        ttk.Label(loading_frame, text="🔄", font=('Segoe UI', 48)).pack(pady=20)
        ttk.Label(loading_frame, text="Processing...",
                  font=('Segoe UI', 16, 'bold'), foreground='#ed8936').pack()
        ttk.Label(loading_frame, text="Verifying identity",
                  font=('Segoe UI', 12), foreground='#fbb040').pack(pady=10)

    def setup_student_info(self):
        # Clear existing widgets
        for widget in self.info_frame.winfo_children():
            widget.destroy()

        if not self.studentInfo:
            self.setup_default_info()
            return

        # Student card with gradient-like effect
        card_frame = tk.Frame(self.info_frame, bg='#667eea', relief='raised', bd=2)
        card_frame.pack(fill=tk.X, pady=(0, 20))

        # Student photo
        photo_frame = tk.Frame(card_frame, bg='#667eea')
        photo_frame.pack(pady=15)

        if self.imgStudent is not None and self.imgStudent.size > 0:
            # Resize and convert student image
            img_pil = Image.fromarray(cv2.cvtColor(self.imgStudent, cv2.COLOR_BGR2RGB))
            img_pil = img_pil.resize((100, 100), Image.Resampling.LANCZOS)

            # Create circular mask
            mask = Image.new('L', (100, 100), 0)
            from PIL import ImageDraw
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, 100, 100), fill=255)

            # Apply mask
            img_pil.putalpha(mask)
            photo = ImageTk.PhotoImage(img_pil)

            photo_label = tk.Label(photo_frame, image=photo, bg='#667eea')
            photo_label.image = photo  # Keep a reference
            photo_label.pack()
        else:
            # Default avatar
            ttk.Label(photo_frame, text="👤", font=('Segoe UI', 60),
                      foreground='white', background='#667eea').pack()

        # Student name
        name = self.studentInfo.get('name', 'Unknown')
        ttk.Label(card_frame, text=name, style='StudentName.TLabel').pack(pady=(0, 5))

        # Student ID
        ttk.Label(card_frame, text=f"ID: {self.id}",
                  style='StudentInfo.TLabel').pack(pady=(0, 15))

        # Details section
        details_frame = tk.Frame(self.info_frame, bg='white', relief='raised', bd=1)
        details_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Details content
        content_frame = ttk.Frame(details_frame, padding="20")
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Detail rows
        details = [
            ("Major", self.studentInfo.get('major', 'N/A')),
            ("Year", str(self.studentInfo.get('year', 'N/A'))),
            ("Standing", self.studentInfo.get('standing', 'N/A')),
            ("Total Attendance", str(self.studentInfo.get('total_attendance', 0))),
            ("Starting Year", str(self.studentInfo.get('starting_year', 'N/A')))
        ]

        for i, (label, value) in enumerate(details):
            row_frame = ttk.Frame(content_frame)
            row_frame.pack(fill=tk.X, pady=5)
            row_frame.columnconfigure(1, weight=1)

            ttk.Label(row_frame, text=f"{label}:", font=('Segoe UI', 11, 'bold')).grid(row=0, column=0, sticky=tk.W)
            ttk.Label(row_frame, text=value, font=('Segoe UI', 11)).grid(row=0, column=1, sticky=tk.E)

        # Status badge
        status_frame = ttk.Frame(content_frame)
        status_frame.pack(fill=tk.X, pady=(15, 0))

        if self.modeType == 3:
            status_text = "⏰ Already Marked"
            status_color = "#ed8936"
        else:
            status_text = "✅ Marked Today"
            status_color = "#48bb78"

        status_label = tk.Label(status_frame, text=status_text,
                                bg=status_color, fg='white',
                                font=('Segoe UI', 12, 'bold'),
                                relief='raised', bd=1, padx=15, pady=8)
        status_label.pack()

    def process_camera(self):
        while True:
            success, img = self.cap.read()
            if not success:
                continue

            imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
            imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

            faceCurFrame = face_recognition.face_locations(imgS)
            encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

            self.face_locations = []

            if faceCurFrame:
                for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
                    matches = face_recognition.compare_faces(self.encodeListKnown, encodeFace)
                    faceDis = face_recognition.face_distance(self.encodeListKnown, encodeFace)

                    matchIndex = np.argmin(faceDis)

                    # Scale face location back to original size
                    y1, x2, y2, x1 = faceLoc
                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4

                    if matches[matchIndex]:
                        # Known face detected
                        print("Known Face Detected")
                        print(self.studentIds[matchIndex])
                        self.id = self.studentIds[matchIndex]
                        self.unknownCounter = 0

                        # Draw green rectangle for known face
                        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 3)
                        cv2.putText(img, "RECOGNIZED", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                        if self.counter == 0:
                            self.counter = 1
                            self.modeType = 1
                            self.status_text = "🔄 Processing..."
                            self.status_color = "#ed8936"
                    else:
                        # Unknown face detected
                        print("Unknown Face Detected")
                        if self.unknownCounter == 0:
                            self.unknownCounter = 1
                        self.id = -1
                        self.counter = 0
                        self.modeType = 0

                        # Draw red rectangle for unknown face
                        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 3)
                        cv2.putText(img, "UNKNOWN", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

                        self.status_text = "❌ Unknown Face"
                        self.status_color = "#f56565"

                # Handle unknown face display
                if self.unknownCounter != 0:
                    self.unknownCounter += 1
                    if self.unknownCounter >= 30:
                        self.unknownCounter = 0
                        self.status_text = "🟢 System Ready"
                        self.status_color = "#48bb78"

                # Handle recognized faces
                if self.counter != 0:
                    if self.counter == 1:
                        # Get student data
                        self.studentInfo = db.reference(f'Students/{self.id}').get()
                        print(f"Student ID: {self.id}")
                        print(f"Student Info: {self.studentInfo}")

                        if self.studentInfo is None:
                            print(f"Không tìm thấy thông tin sinh viên với ID: {self.id}")
                            self.modeType = 3
                            self.counter = 0
                            self.status_text = "❌ Student Not Found"
                            self.status_color = "#f56565"
                        else:
                            try:
                                # Get student image
                                blob = self.bucket.get_blob(f'Images/{self.id}.png')
                                if blob and blob.exists():
                                    array = np.frombuffer(blob.download_as_string(), np.uint8)
                                    self.imgStudent = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)
                                else:
                                    print(f"Không tìm thấy ảnh sinh viên với ID: {self.id}")
                                    self.imgStudent = None

                                # Check attendance timing
                                if 'last_attendance_time' in self.studentInfo and self.studentInfo[
                                    'last_attendance_time']:
                                    datetimeObject = datetime.strptime(self.studentInfo['last_attendance_time'],
                                                                       "%Y-%m-%d %H:%M:%S")
                                    secondsElapsed = (datetime.now() - datetimeObject).total_seconds()
                                    print(f"Seconds elapsed: {secondsElapsed}")
                                else:
                                    secondsElapsed = 31
                                    print("Chưa có lịch sử điểm danh")

                                if secondsElapsed > 30:
                                    # Update attendance
                                    ref = db.reference(f'Students/{self.id}')
                                    if 'total_attendance' not in self.studentInfo or self.studentInfo[
                                        'total_attendance'] is None:
                                        self.studentInfo['total_attendance'] = 0

                                    self.studentInfo['total_attendance'] += 1
                                    ref.child('total_attendance').set(self.studentInfo['total_attendance'])
                                    ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                                    print(f"Đã cập nhật điểm danh cho sinh viên {self.id}")

                                    self.status_text = "✅ Attendance Marked"
                                    self.status_color = "#48bb78"
                                else:
                                    self.modeType = 3
                                    self.counter = 0
                                    self.status_text = "⏰ Already Marked Today"
                                    self.status_color = "#ed8936"
                                    print("Điểm danh quá gần, cần chờ ít nhất 30 giây")

                            except Exception as e:
                                print(f"Lỗi khi xử lý dữ liệu sinh viên: {e}")
                                self.modeType = 3
                                self.counter = 0
                                self.status_text = "❌ Processing Error"
                                self.status_color = "#f56565"

                    if self.modeType != 3 and self.studentInfo is not None:
                        if 10 < self.counter < 20:
                            self.modeType = 2

                    self.counter += 1

                    if self.counter >= 20:
                        self.counter = 0
                        self.modeType = 0
                        self.studentInfo = None
                        self.imgStudent = None
                        self.status_text = "🟢 System Ready"
                        self.status_color = "#48bb78"
            else:
                # No face detected
                self.modeType = 0
                self.counter = 0
                self.unknownCounter = 0
                self.id = -1
                self.status_text = "🟢 System Ready"
                self.status_color = "#48bb78"

            # Store current frame for GUI update
            self.current_frame = img.copy()

            time.sleep(0.1)  # Limit processing rate

    def update_gui(self):
        while True:
            try:
                # Update camera feed
                if hasattr(self, 'current_frame'):
                    # Convert frame to display format
                    frame_rgb = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB)
                    frame_pil = Image.fromarray(frame_rgb)
                    frame_pil = frame_pil.resize((560, 420), Image.Resampling.LANCZOS)
                    frame_tk = ImageTk.PhotoImage(frame_pil)

                    self.camera_label.configure(image=frame_tk, text="")
                    self.camera_label.image = frame_tk  # Keep a reference

                # Update status
                self.status_label.configure(text=self.status_text, foreground=self.status_color)

                # Update student info based on mode
                if self.modeType == 0 and self.unknownCounter == 0:
                    # No face or system ready
                    self.setup_default_info()
                elif self.unknownCounter > 0:
                    # Unknown face
                    self.setup_unknown_info()
                elif self.counter == 1:
                    # Loading
                    self.setup_loading_info()
                elif self.studentInfo is not None:
                    # Show student info
                    self.setup_student_info()

            except Exception as e:
                print(f"GUI update error: {e}")

            time.sleep(0.1)  # Update rate limit

    def run(self):
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("Shutting down...")
        finally:
            self.cap.release()
            cv2.destroyAllWindows()


if __name__ == "__main__":
    app = ModernAttendanceSystem()
    app.run()