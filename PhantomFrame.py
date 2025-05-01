import tkinter as tk
from tkinter import ttk, messagebox
from textblob import TextBlob
import cv2
import numpy as np
import time
import threading
import speech_recognition as sr
import os


# Global cloak color
cloak_color = "Red"

# === Voice Sentiment Analysis ===
def sentiment_analysis_voice():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        output_label.config(text="Listening...")
        try:
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio)
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            sentiment = "Neutral"
            if polarity > 0:
                sentiment = "Positive"
            elif polarity < 0:
                sentiment = "Negative"
            result = f"You said: {text}\nPolarity: {polarity:.2f}\nSentiment: {sentiment}"
            output_label.config(text=result)
        except sr.UnknownValueError:
            output_label.config(text="Could not understand your speech.")
        except sr.RequestError:
            output_label.config(text="Speech recognition service unavailable.")
            

# === Invisibility Cloak (no voice control) ===
def invisibility_cloak_gui():
    color_ranges = {
        "Red": ([0, 120, 70], [10, 255, 255], [170, 120, 70], [180, 255, 255]),
        "Blue": ([94, 80, 2], [126, 255, 255]),
        "Green": ([40, 40, 40], [70, 255, 255])
    }

    cap = cv2.VideoCapture(0)
    output_label.config(text="Capturing background. Please stay still...")
    time.sleep(3)

    for i in range(30):
        ret, background = cap.read()
    background = np.flip(background, axis=1)

    output_label.config(text="Cloak activated! Press 'Q' to stop.")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame = np.flip(frame, axis=1)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        if cloak_color == "Red":
            lower1 = np.array(color_ranges["Red"][0])
            upper1 = np.array(color_ranges["Red"][1])
            lower2 = np.array(color_ranges["Red"][2])
            upper2 = np.array(color_ranges["Red"][3])
            mask1 = cv2.inRange(hsv, lower1, upper1)
            mask2 = cv2.inRange(hsv, lower2, upper2)
            cloak_mask = mask1 + mask2
        else:
            lower = np.array(color_ranges[cloak_color][0])
            upper = np.array(color_ranges[cloak_color][1])
            cloak_mask = cv2.inRange(hsv, lower, upper)

        cloak_mask = cv2.morphologyEx(cloak_mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8), iterations=2)
        cloak_mask = cv2.dilate(cloak_mask, np.ones((3, 3), np.uint8), iterations=1)

        inverse_mask = cv2.bitwise_not(cloak_mask)
        cloak_area = cv2.bitwise_and(background, background, mask=cloak_mask)
        non_cloak_area = cv2.bitwise_and(frame, frame, mask=inverse_mask)
        final_output = cv2.addWeighted(cloak_area, 1, non_cloak_area, 1, 0)

        cv2.imshow("Invisibility Cloak - Press Q to stop", final_output)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    output_label.config(text="Cloak deactivated.")

# === Update Cloak Color ===
def update_cloak_color(event):
    global cloak_color
    cloak_color = cloak_color_var.get()

def record_and_reverse_video():
    output_label.config(text="Recording video for 5 seconds...")
    cap = cv2.VideoCapture(0)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640, 480))

    start_time = time.time()
    while int(time.time() - start_time) < 5:
        ret, frame = cap.read()
        if not ret:
            break
        out.write(frame)
        cv2.imshow("Recording...", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()
    output_label.config(text="Recording done. Reversing video...")

# time turner
def time_turner():
    output_label.config(text="Recording 10 seconds of video for Time-Turner effect...")
    cap = cv2.VideoCapture(0)
    width = int(cap.get(3))
    height = int(cap.get(4))
    fps = 20
    frames = []

    start_time = time.time()
    while time.time() - start_time < 10:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        frames.append(frame)
        cv2.imshow("Recording... (10 seconds)", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    output_label.config(text="Rewinding time...")

    for frame in reversed(frames):
        cv2.imshow("Time Reversed", frame)
        if cv2.waitKey(int(1000 / fps)) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()
    output_label.config(text="Time-Turner completed!")

# === Beautiful Modern GUI ===
def launch_sentiment_popup():
    def start_sentiment():
        popup.destroy()
        sentiment_analysis_voice()

    popup = tk.Toplevel(root)
    popup.title("Sentiment Analysis")
    popup.geometry("320x150")
    popup.configure(bg="#fff1ff")

    tk.Label(popup, text="🎤 Speak something, I am listening...", bg="#fff1ff",
             font=("Segoe UI", 12)).pack(pady=15)
    ttk.Button(popup, text="🎧 Start Listening", command=start_sentiment).pack(pady=10)


def launch_cloak_popup():
    def start_cloak():
        global cloak_color
        cloak_color = color_choice.get()
        popup.destroy()
        threading.Thread(target=invisibility_cloak_gui).start()

    popup = tk.Toplevel(root)
    popup.title("Select Cloak Color")
    popup.geometry("320x170")
    popup.configure(bg="#fff1ff")

    tk.Label(popup, text="🧥 Choose your cloak color:", bg="#fff1ff",
             font=("Segoe UI", 12)).pack(pady=10)
    color_choice = tk.StringVar(value="Red")
    cloak_dropdown = ttk.Combobox(popup, textvariable=color_choice,
                                   values=["Red", "Blue", "Green"], state="readonly", width=15)
    cloak_dropdown.pack(pady=5)
    ttk.Button(popup, text="✨ Activate Cloak", command=start_cloak).pack(pady=15)


root = tk.Tk()
root.title("4Ces Toolkit")
root.geometry("560x520")
root.configure(bg="#f7f0ff")

style = ttk.Style()
style.theme_use("clam")

# Style buttons nicely
style.configure("TButton",
                font=("Segoe UI", 11, "bold"),
                padding=10,
                background="#b891f7",
                foreground="black",
                relief="flat")
style.map("TButton",
          background=[("active", "#a67ef7")],
          foreground=[("pressed", "white")])

style.configure("TLabel", background="#f7f0ff", font=("Segoe UI", 12))

# Title
tk.Label(root, text="✨Ghumo Ghoomo Cloak Lagao✨", font=("Segoe UI", 22, "bold"), bg="#f7f0ff", fg="#5a189a").pack(pady=(25, 10))

# Menu Label
tk.Label(root, text="Menu", font=("Segoe UI", 14, "bold underline"), bg="#f7f0ff").pack(pady=(5, 15))

# Menu Frame
btn_frame = ttk.Frame(root)
btn_frame.pack(pady=5)

# Menu Buttons
ttk.Button(btn_frame, text=" Sentiment Analysis", width=35, command=launch_sentiment_popup).grid(row=0, column=0, pady=10)
ttk.Button(btn_frame, text=" Time Turner Mode", width=35, command=lambda: threading.Thread(target=time_turner).start()).grid(row=1, column=0, pady=10)
ttk.Button(btn_frame, text=" Harry Potter Invisibility Cloak", width=35, command=launch_cloak_popup).grid(row=2, column=0, pady=10)

# Output Display Box
output_frame = tk.Frame(root, bg="#e8dcff", bd=2, relief="groove")
output_frame.pack(pady=30, padx=30, fill="x")

output_label = tk.Label(output_frame, text="Your output will appear here.", font=("Segoe UI", 11), bg="#e8dcff",
                        fg="black", wraplength=480, justify="center", padx=20, pady=12)
output_label.pack(fill="both")


root.mainloop()