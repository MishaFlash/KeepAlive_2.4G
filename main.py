import pygame
import numpy as np
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageDraw
import pystray
import threading

# settings
SAMPLE_RATE = 44100
VOLUME = 0.05
PULSE_INTERVAL = 299000  # 299 seconds to milliseconds

class KeepAliveApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("KeepAlive 2.4G")
        self.root.geometry("450x450")
        self.root.minsize(450, 450)
        self.root.configure(bg='#1E1E1E')
    
        # icon for title and task bar
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
    
        self.root.protocol("WM_DELETE_WINDOW", self.hide_to_tray)
    
        self.is_running = False
        self.tray_icon = None
    
        self.setup_ui()
        self.create_tray_icon()
    
    def setup_ui(self):
        # title
        title_label = tk.Label(
            self.root,
            text="KeepAlive 2.4G",
            fg="white",
            bg="#1E1E1E",
            font=("Segoe UI", 16, "bold")
        )
        title_label.pack(pady=(30, 10))
        
        subtitle_label = tk.Label(
            self.root,
            text="Impulses keep headset turned on",
            fg="#AAAAAA",
            bg="#1E1E1E",
            font=("Segoe UI", 10)
        )
        subtitle_label.pack()
        
        # status
        self.status_frame = tk.Frame(self.root, bg='#2A2A2A', padx=15, pady=10)
        self.status_frame.pack(pady=20, fill='x', padx=30)
        
        self.status_indicator = tk.Canvas(
            self.status_frame,
            width=12,
            height=12,
            bg='#2A2A2A',
            highlightthickness=0
        )
        self.status_indicator.pack(side='left', padx=(0, 10))
        self.indicator_circle = self.status_indicator.create_oval(
            1, 1, 11, 11,
            fill='#FF4444',
            outline=''
        )
        
        self.status_label = tk.Label(
            self.status_frame,
            text="Stopped",
            fg="#AAAAAA",
            bg='#2A2A2A',
            font=("Segoe UI", 11)
        )
        self.status_label.pack(side='left')
        
        # mode info
        info_frame = tk.Frame(self.root, bg='#1E1E1E')
        info_frame.pack(pady=10)
        
        tk.Label(
            info_frame,
            text=f"Impulse every {PULSE_INTERVAL // 1000} seoonds",
            fg="#888888",
            bg='#1E1E1E',
            font=("Segoe UI", 9)
        ).pack()
        
        tk.Label(
            info_frame,
            text="20 Hz + 19000 Hz • 0.05 sec",
            fg="#888888",
            bg='#1E1E1E',
            font=("Segoe UI", 9)
        ).pack()
        
        # buttons
        button_frame = tk.Frame(self.root, bg='#1E1E1E')
        button_frame.pack(pady=20)
        
        self.start_button = tk.Button(
            button_frame,
            text="Run",
            command=self.start,
            bg="#2ECC71",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            bd=0,
            padx=20,
            pady=8,
            activebackground="#27AE60",
            cursor="hand2"
        )
        self.start_button.pack(side='left', padx=5)
        
        self.stop_button = tk.Button(
            button_frame,
            text="Stop",
            command=self.stop,
            bg="#E74C3C",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            bd=0,
            padx=20,
            pady=8,
            activebackground="#C0392B",
            state='disabled',
            cursor="hand2"
        )
        self.stop_button.pack(side='left', padx=5)
        
        # hide button
        tray_button = tk.Button(
            self.root,
            text="▼ Hide",
            command=self.hide_to_tray,
            bg="#555555",
            fg="white",
            font=("Segoe UI", 9),
            bd=0,
            padx=15,
            pady=5,
            activebackground="#777777",
            cursor="hand2"
        )
        tray_button.pack(pady=(5, 0))
        
        # hint
        hint_label = tk.Label(
            self.root,
            text="Select your headset as Windows output device\nbefore launching",
            fg="#555555",
            bg='#1E1E1E',
            font=("Segoe UI", 8)
        )
        hint_label.pack(side='bottom', pady=15)
    
    def create_tray_icon(self):
        """tray icon"""
        # indicator
        icon_image = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(icon_image)
        draw.ellipse([8, 8, 56, 56], fill='#2ECC71', outline='#27AE60', width=2)
        draw.text((20, 20), "K", fill='white')
        
        # tray menu
        menu = pystray.Menu(
            pystray.MenuItem("Show window", self.show_window),
            pystray.MenuItem("Run", self.start),
            pystray.MenuItem("Stop", self.stop),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", self.quit_app)
        )
        
        self.tray_icon = pystray.Icon(
            "keepalive",
            icon_image,
            "KeepAlive 2.4G",
            menu
        )
        
        tray_thread = threading.Thread(target=self.tray_icon.run, daemon=True)
        tray_thread.start()
    
    def start(self):
        """keepalive impulse start"""
        try:
            pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=2)
            self.is_running = True
            self.update_status("Running", '#F39C12')
            self.start_button.config(state='disabled')
            self.stop_button.config(state='normal')
            
            self.update_tray_icon('#F39C12')
            
            self.pulse()
            
            print("KeepAlive started")
        except Exception as e:
            messagebox.showerror("Err", f"Failed to run:\n{e}")
    
    def pulse(self):
        """next impulse"""
        if not self.is_running:
            return
        
        duration = 0.05
        samples = int(SAMPLE_RATE * duration)
        t = np.linspace(0, duration, samples, False)
        
        tone_low = np.sin(2 * np.pi * 20 * t) * 0.5
        tone_high = np.sin(2 * np.pi * 19000 * t) * 0.5
        tone = (tone_low + tone_high) / 2
        tone = tone * VOLUME
        tone = (tone * 32767).astype(np.int16)
        
        # stereo
        stereo_tone = np.column_stack((tone, tone))
        
        # running
        sound = pygame.sndarray.make_sound(stereo_tone)
        sound.play()
        
        # next impulse
        self.root.after(PULSE_INTERVAL, self.pulse)
    
    def stop(self):
        """stops keepalive"""
        self.is_running = False
        
        try:
            pygame.mixer.quit()
        except:
            pass
        
        self.update_status("stopped", '#FF4444')
        self.update_tray_icon('#FF4444')
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        
        print("KeepAlive stopped")
    
    def update_status(self, text, color):
        """Обновляет индикатор статуса в окне"""
        self.status_label.config(text=text)
        self.status_indicator.itemconfig(self.indicator_circle, fill=color)
    
    def update_tray_icon(self, color):
        """Обновляет цвет иконки в трее"""
        if self.tray_icon:
            icon_image = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
            draw = ImageDraw.Draw(icon_image)
            draw.ellipse([8, 8, 56, 56], fill=color, outline='#333333', width=2)
            draw.text((20, 20), "K", fill='white')
            self.tray_icon.icon = icon_image
    
    def hide_to_tray(self):
        """hide to tray"""
        self.root.withdraw()
    
    def show_window(self):
        """show from tray"""
        self.root.deiconify()
        self.root.lift()
    
    def quit_app(self):
        """program quit"""
        self.stop()
        if self.tray_icon:
            self.tray_icon.stop()
        self.root.destroy()
    
    def on_closing(self):
        """x"""
        self.hide_to_tray()
    
    def run(self):
        """mainloop"""
        self.root.mainloop()


# run
if __name__ == "__main__":
    app = KeepAliveApp()
    app.run()
