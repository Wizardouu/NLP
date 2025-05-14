import tkinter as tk
from tkinter import scrolledtext, filedialog
import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np
import time
import os
from pydub import AudioSegment
from pydub.playback import play
import threading

class AudioChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Chat App")
        
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(root, width=60, height=20)
        self.chat_display.pack(pady=10)
        
        # Message entry
        self.message_entry = tk.Entry(root, width=50)
        self.message_entry.pack(pady=5)
        
        # Send text button
        self.send_button = tk.Button(root, text="Send Text", command=self.send_text)
        self.send_button.pack(pady=5)
        
        # Audio controls
        self.audio_frame = tk.Frame(root)
        self.audio_frame.pack(pady=10)
        
        self.record_button = tk.Button(self.audio_frame, text="Record Audio", command=self.start_recording)
        self.record_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = tk.Button(self.audio_frame, text="Stop Recording", command=self.stop_recording, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        self.play_button = tk.Button(self.audio_frame, text="Play Last Recording", command=self.play_recording)
        self.play_button.pack(side=tk.LEFT, padx=5)
        
        # Audio state variables
        self.is_recording = False
        self.audio_frames = []
        self.sample_rate = 44100
        self.last_recording = None
        
    def send_text(self):
        message = self.message_entry.get()
        if message:
            self.display_message("You: " + message)
            self.message_entry.delete(0, tk.END)
            
    def display_message(self, message):
        self.chat_display.insert(tk.END, message + "\n")
        self.chat_display.see(tk.END)
        
    def start_recording(self):
        self.is_recording = True
        self.audio_frames = []
        self.record_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.play_button.config(state=tk.DISABLED)
        
        self.display_message("System: Recording started...")
        
        # Start recording in a separate thread
        self.recording_thread = threading.Thread(target=self.record_audio)
        self.recording_thread.start()
        
    def record_audio(self):
        with sd.InputStream(samplerate=self.sample_rate, channels=1, callback=self.audio_callback):
            while self.is_recording:
                time.sleep(0.1)
                
    def audio_callback(self, indata, frames, time, status):
        if self.is_recording:
            self.audio_frames.append(indata.copy())
            
    def stop_recording(self):
        self.is_recording = False
        self.recording_thread.join()
        
        self.record_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.play_button.config(state=tk.NORMAL)
        
        # Save recording
        if self.audio_frames:
            audio_data = np.concatenate(self.audio_frames)
            self.last_recording = "recording_" + str(int(time.time())) + ".wav"
            write(self.last_recording, self.sample_rate, audio_data)
            self.display_message(f"System: Recording saved as {self.last_recording}")
            
    def play_recording(self):
        if self.last_recording and os.path.exists(self.last_recording):
            self.display_message("System: Playing last recording...")
            
            # Play in a separate thread to avoid freezing the GUI
            threading.Thread(target=self._play_audio).start()
        else:
            self.display_message("System: No recording available to play")
            
    def _play_audio(self):
        audio = AudioSegment.from_wav(self.last_recording)
        play(audio)
        self.display_message("System: Finished playing recording")

# For running in Colab
try:
    from google.colab import output
    output.enable_custom_widget_manager()
except:
    pass

# Create and run the app
root = tk.Tk()
app = AudioChatApp(root)