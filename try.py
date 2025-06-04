import sys
print("Python executable:", sys.executable)
print("Python path:", sys.path)

try:
    import tkinter
    print("Tkinter import successful!")
except Exception as e:
    print("Tkinter error:", e)