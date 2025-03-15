import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
import cv2
import numpy as np
from deepface import DeepFace
import time
import pygame  # For playing the audio
import random

class EmotionSyncApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("EmotionSync - Face Emotion Recognition")
        self.geometry("1000x600")
        self.resizable(False, False)

        # Initialize pygame for music
        pygame.mixer.init()

        # Video capture setup
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Error: Could not open webcam.")
            exit()

        # Give the camera time to adjust
        time.sleep(3)

        # UI Setup
        self.create_starry_background()
        self.create_widgets()

        # Avatar images (using your specified GIF files)
        self.avatars = {
            'happy': self.load_gif("/Users/pillalashyamvenkatarun/Desktop/FER-SHARE 2 new - Copy 3/FER-SHARE/gif/happy.gif", (200, 200)),
            'sad': self.load_gif("/Users/pillalashyamvenkatarun/Desktop/FER-SHARE 2 new - Copy 3/FER-SHARE/gif/sad.gif", (200, 200)),
            'angry': self.load_gif("/Users/pillalashyamvenkatarun/Desktop/FER-SHARE 2 new - Copy 3/FER-SHARE/gif/angry.gif", (200, 200)),
            'neutral': self.load_gif("/Users/pillalashyamvenkatarun/Desktop/FER-SHARE 2 new - Copy 3/FER-SHARE/gif/neutral.gif", (200, 200)),
            'surprise': self.load_gif("/Users/pillalashyamvenkatarun/Desktop/FER-SHARE 2 new - Copy 3/FER-SHARE/gif/surprise-gif-3.gif", (200, 200)),
            'fear': self.load_gif("/Users/pillalashyamvenkatarun/Desktop/FER-SHARE 2 new - Copy 3/FER-SHARE/gif/fear.gif", (200, 200)),
        }
        self.current_avatar_frame = {emotion: 0 for emotion in self.avatars}

        # Song paths for each emotion with multiple songs (update with correct paths)
        self.song_paths = {
            'happy': [
                r"/Users/pillalashyamvenkatarun/Desktop/FER-SHARE 2 new - Copy 3/FER-SHARE/music/happy/apt.mp3",
                "/Users/pillalashyamvenkatarun/Desktop/FER-SHARE 2 new - Copy 3/FER-SHARE/music/happy/levitating.mp3",
                "/Users/pillalashyamvenkatarun/Desktop/FER-SHARE 2 new - Copy 3/FER-SHARE/music/happy/paper rings.mp3",
            ],
            'sad': [
                "/Users/pillalashyamvenkatarun/Desktop/FER-SHARE 2 new - Copy 3/FER-SHARE/music/sad/die with a smile.mp3",
                "/Users/pillalashyamvenkatarun/Desktop/FER-SHARE 2 new - Copy 3/FER-SHARE/music/sad/my you .mp3",
                r"/Users/pillalashyamvenkatarun/Desktop/FER-SHARE 2 new - Copy 3/FER-SHARE/music/sad/unstoppable.mp3",
            ],
            'angry': [
                r"/Users/pillalashyamvenkatarun/Desktop/FER-SHARE 2 new - Copy 3/FER-SHARE/music/angry/animals.mp3",
                r"/Users/pillalashyamvenkatarun/Desktop/FER-SHARE 2 new - Copy 3/FER-SHARE/music/angry/night changes.mp3",
                r"/Users/pillalashyamvenkatarun/Desktop/FER-SHARE 2 new - Copy 3/FER-SHARE/music/angry/sorry.mp3",
            ],
            'neutral': [
                r"/Users/pillalashyamvenkatarun/Desktop/FER-SHARE 2 new - Copy 3/FER-SHARE/music/neutral/cheap thrills.mp3",
                r"/Users/pillalashyamvenkatarun/Desktop/FER-SHARE 2 new - Copy 3/FER-SHARE/music/neutral/heatwaves.mp3",
                r"/Users/pillalashyamvenkatarun/Desktop/FER-SHARE 2 new - Copy 3/FER-SHARE/music/neutral/wnna be yours.mp3",
            ],
            'surprise': [
                "/Users/pillalashyamvenkatarun/Desktop/FER-SHARE 2 new - Copy 3/FER-SHARE/music/surprise/7 rings.mp3",
                "/Users/pillalashyamvenkatarun/Desktop/FER-SHARE 2 new - Copy 3/FER-SHARE/music/surprise/counting stars.mp3",
                r"/Users/pillalashyamvenkatarun/Desktop/FER-SHARE 2 new - Copy 3/FER-SHARE/music/surprise/shake it off.mp3",
            ],
            'fear': [
                r"/Users/pillalashyamvenkatarun/Desktop/FER-SHARE 2 new - Copy 3/FER-SHARE/music/fear/believer.mp3",
                r"/Users/pillalashyamvenkatarun/Desktop/FER-SHARE 2 new - Copy 3/FER-SHARE/music/fear/on my way.mp3",
                r"/Users/pillalashyamvenkatarun/Desktop/FER-SHARE 2 new - Copy 3/FER-SHARE/music/fear/the nights.mp3",
            ],
        }

        # Dictionary to track the last played song for each emotion
        self.last_played_song = {emotion: None for emotion in self.song_paths.keys()}

        # Flag to control detection
        self.detecting = False
        self.current_emotion = None  # To store the detected emotion

        # Start the video update loop
        self.update_video()

    def load_gif(self, path, size):
        """Loads a GIF and returns a list of PhotoImage frames."""
        try:
            img = Image.open(path)
            frames = []
            for frame in ImageSequence.Iterator(img):
                frame = frame.convert('RGBA').resize(size)
                photo = ImageTk.PhotoImage(frame)
                frames.append(photo)
            return frames
        except Exception as e:
            print(f"Error loading GIF {path}: {e}")
            return []

    def create_starry_background(self):
        self.canvas = tk.Canvas(self, width=1000, height=600)
        self.canvas.pack(fill="both", expand=True)

        # Background: Deep plum
        self.canvas.create_rectangle(0, 0, 1000, 600, fill="#3B0033", outline="#3B0033")

        # Subtle overlay for depth
        for i in range(0, 600, 50):
            alpha = int(20 * (i / 600))  # Fade to darker shade
            color = f'#2A00{alpha:02x}'
            self.canvas.create_rectangle(0, i, 1000, i + 50, fill=color, outline="")

        # Equalizer bars
        self.bars = []
        colors = [("#6600CC", "#CC00CC"), ("#990099", "#FF66CC")]  # Two gradient pairs
        for i in range(20):
            x = 50 + i * 45  # Spacing bars evenly
            base_height = random.randint(50, 250)
            start_color, end_color = colors[i % 2]
            bar = self.canvas.create_rectangle(x, 600 - base_height, x + 20, 600,
                                               fill=start_color, outline=end_color, width=2)
            self.bars.append((bar, base_height))

        # Musical notes
        self.notes = []
        for _ in range(25):
            x = random.randint(0, 990)  # Leave room for size
            y = random.randint(0, 585)  # Leave room for stem
            size = random.randint(5, 10)
            outline_color = random.choice(["#6600CC", "#FF66CC"])
            note = self.canvas.create_oval(x, y, x + size, y + size, fill="#FFFFFF", outline=outline_color, width=2)
            self.canvas.create_line(x + size, y, x + size + 8, y - 15, fill=outline_color, width=2)  # Stem
            self.notes.append(note)

        # Start animation
        self.animate_equalizer()

    def animate_equalizer(self):
        for bar, base_height in self.bars:
            new_height = base_height + random.randint(-30, 30)  # Pulse effect
            new_height = max(50, min(400, new_height))  # Clamp between 50 and 400
            coords = self.canvas.coords(bar)
            self.canvas.coords(bar, coords[0], 600 - new_height, coords[2], 600)

        for note in self.notes:
            if random.random() < 0.2:  # 20% chance to pulse
                size = random.randint(5, 10)
                coords = self.canvas.coords(note)
                x1, y1 = coords[0], coords[1]
                x2, y2 = min(1000, x1 + size), min(600, y1 + size)  # Ensure within bounds
                self.canvas.coords(note, x1, y1, x2, y2)

        self.after(200, self.animate_equalizer)  # Update every 200ms

    def create_widgets(self):
        # Video Container
        self.video_frame = tk.Frame(self, bg="#ffffff", bd=5, relief="ridge")
        self.video_frame.place(x=20, y=20, width=500, height=400)
        self.video_label = tk.Label(self.video_frame)
        self.video_label.pack(expand=True)

        # Emoji Container
        self.emoji_frame = tk.Frame(self, bg="#ffffff", bd=5, relief="ridge")
        self.emoji_frame.place(x=550, y=20, width=430, height=260)
        self.emoji_label = tk.Label(self.emoji_frame, text="Waiting for detection...",
                                  font=("Arial", 16), bg="#ffffff", fg="#333333")
        self.emoji_label.pack(pady=5)
        self.avatar_label = tk.Label(self.emoji_frame, bg="#ffffff")
        self.avatar_label.pack()

        # Buttons (changed to magenta)
        button_frame = tk.Frame(self)  # Deep magenta from Emo Violet scheme
        button_frame.place(x=550, y=250, width=430, height=60)

        self.detect_btn = AnimatedButton(button_frame, "Detect Emotion", self.detect_emotion,
                                       "#FF6F61", "#FF8A80")
        self.detect_btn.grid(row=0, column=0, padx=5)

        self.play_btn = AnimatedButton(button_frame, "Play Song", self.play_song,
                                     "#4CAF50", "#66BB6A", state=tk.DISABLED)
        self.play_btn.grid(row=0, column=1, padx=5)

        self.exit_btn = AnimatedButton(button_frame, "Exit", self.exit_app,
                                     "#F06292", "#F48FB1")
        self.exit_btn.grid(row=0, column=2, padx=5)

    def update_video(self):
        ret, frame = self.cap.read()
        if ret:
            try:
                # Detect emotion only when triggered by detect_emotion
                if self.detecting and self.current_emotion is None:
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                    # Use specific face detection backend
                    result = DeepFace.analyze(rgb_frame,
                                            actions=['emotion'],
                                            enforce_detection=True,
                                            detector_backend='opencv',
                                            silent=True)

                    if result and 'dominant_emotion' in result[0]:
                        # Add confidence threshold (0-100)
                        if result[0]['emotion'][result[0]['dominant_emotion']] > 30:
                            self.current_emotion = result[0]['dominant_emotion'].lower()
                            print(f"Detected Emotion: {self.current_emotion} (Confidence: {result[0]['emotion'][self.current_emotion]:.1f}%)")
                            self.detecting = False
                            self.emoji_label.config(text=f"Detected: {self.current_emotion.capitalize()}")
                            self.update_avatar()
                            self.play_btn.config(state=tk.NORMAL)

                            face_location = result[0]['region']
                            x, y, w, h = face_location['x'], face_location['y'], face_location['w'], face_location['h']
                            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            except Exception as e:
                print("Detection error:", str(e))

            # Convert frame for Tkinter display
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.config(image=imgtk)

        self.after(10, self.update_video)  # Update the video every 10ms

    def update_avatar(self):
        """Updates the avatar label with the next frame of the GIF."""
        if self.current_emotion and self.current_emotion in self.avatars:
            frames = self.avatars[self.current_emotion]
            if frames:
                frame_index = self.current_avatar_frame[self.current_emotion]
                self.avatar_label.config(image=frames[frame_index])
                self.avatar_label.image = frames[frame_index]  # Keep a reference!

                # Increment frame index and loop
                self.current_avatar_frame[self.current_emotion] = (frame_index + 1) % len(frames)
                self.after(100, self.update_avatar)  # Adjust speed as needed

    def detect_emotion(self):
        if not self.detecting:
            self.detecting = True
            self.current_emotion = None  # Reset current emotion for new detection
            print("Starting emotion detection...")

    def play_song(self):
        # Get the emotion detected
        emotion = self.current_emotion
        if emotion and emotion in self.song_paths:
            # Get the list of songs for this emotion
            songs = self.song_paths[emotion]
            # Exclude the last played song from the options
            available_songs = [song for song in songs if song != self.last_played_song[emotion]]
            if not available_songs:  # If all songs have been played, reset to full list
                available_songs = songs

            # Randomly select a song from the available ones
            song_path = random.choice(available_songs)
            self.last_played_song[emotion] = song_path  # Update the last played song
            print(f"Playing song: {song_path} for emotion: {emotion}")

            pygame.mixer.music.load(song_path)
            pygame.mixer.music.play()
            self.after(15000, self.stop_music_and_reset)  # Stop after 15 seconds

    def stop_music_and_reset(self):
        pygame.mixer.music.stop()
        self.detecting = False  # Ensure detecting is off
        self.current_emotion = None  # Clear emotion for next detection
        self.emoji_label.config(text="Waiting for detection...")
        self.avatar_label.config(image='')
        self.play_btn.config(state=tk.DISABLED)

    def stop_music(self):
        pygame.mixer.music.stop()

    def animate_emoji(self):
        # Placeholder for emoji animation functionality
        pass

    def exit_app(self):
        self.cap.release()
        pygame.mixer.music.stop()  # Stop any playing music
        self.quit()

class AnimatedButton(tk.Button):
    def __init__(self, master, text, command, bg_color, hover_color, **kwargs):
        super().__init__(master, text=text, command=command, font=("Arial", 14, "bold"),
                         bg=bg_color, fg="white", bd=0, relief="flat", padx=20, pady=10, **kwargs)
        self.default_bg = bg_color
        self.hover_bg = hover_color
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, event):
        self.config(bg=self.hover_bg)

    def on_leave(self, event):
        self.config(bg=self.default_bg)

if __name__ == "__main__":
    app = EmotionSyncApp()
    app.mainloop()
