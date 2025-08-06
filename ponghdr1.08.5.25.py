import tkinter as tk
import random
import time
import math
import pygame
from pygame import mixer

class PS5Pong:
    def __init__(self, root):
        self.root = root
        self.root.title("PS5 PONG")
        self.root.geometry("900x600")
        self.root.configure(bg="#000814")
        self.root.resizable(False, False)
        
        # Initialize pygame mixer
        pygame.init()
        mixer.init()
        
        # Create sound effects
        self.sounds = {
            "paddle": mixer.Sound(self.generate_sine_wave(440, 0.1)),
            "wall": mixer.Sound(self.generate_sine_wave(330, 0.1)),
            "score": mixer.Sound(self.generate_sine_wave(880, 0.3)),
            "start": mixer.Sound(self.generate_sine_wave(523.25, 0.5))
        }
        
        # Create main menu
        self.create_main_menu()
        
        # Performance tracking
        self.last_frame_time = time.time()
        
    def generate_sine_wave(self, freq, duration, sample_rate=44100, volume=0.5):
        """Generate a sine wave sound effect"""
        samples = bytearray()
        for i in range(int(duration * sample_rate)):
            sample = int(volume * 32767.0 * math.sin(2 * math.pi * freq * i / sample_rate))
            samples.extend([sample & 0xFF, (sample >> 8) & 0xFF])
        return bytes(samples)
    
    def create_main_menu(self):
        """Create PS5-style main menu"""
        self.menu_canvas = tk.Canvas(self.root, bg="#000814", highlightthickness=0)
        self.menu_canvas.pack(fill=tk.BOTH, expand=True)
        
        # PS5 logo
        self.menu_canvas.create_rectangle(350, 100, 550, 300, fill="#0072CE", outline="")
        self.menu_canvas.create_text(450, 200, text="PS5", fill="white", 
                                    font=("Arial", 48, "bold"))
        
        # Game title
        self.menu_canvas.create_text(450, 350, text="PONG", fill="#FF9B1A", 
                                    font=("Arial", 64, "bold"))
        
        # Start button
        self.start_btn = tk.Button(self.root, text="START GAME", font=("Arial", 24), 
                                 bg="#0072CE", fg="white", activebackground="#FF9B1A",
                                 command=self.start_game)
        self.start_btn.place(x=350, y=400, width=200, height=50)
        
        # Quit button
        self.quit_btn = tk.Button(self.root, text="QUIT", font=("Arial", 24), 
                                bg="#5D5D5D", fg="white", activebackground="#FF9B1A",
                                command=self.root.quit)
        self.quit_btn.place(x=350, y=470, width=200, height=50)
        
        # Play start sound
        self.sounds["start"].play()
    
    def start_game(self):
        """Initialize game elements"""
        # Remove menu elements
        self.menu_canvas.destroy()
        self.start_btn.destroy()
        self.quit_btn.destroy()
        
        # Create game canvas
        self.canvas = tk.Canvas(self.root, bg="#111", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Game elements
        self.width = 900
        self.height = 600
        self.paddle_width = 15
        self.paddle_height = 120
        self.ball_size = 20
        self.ball_speed = 5
        self.paddle_speed = 8
        self.ai_difficulty = 0.7  # AI skill level (0-1)
        
        # Create center line
        for i in range(0, self.height, 30):
            self.canvas.create_rectangle(
                self.width//2 - 5, i,
                self.width//2 + 5, i + 15,
                fill="#333", outline=""
            )
        
        # Create player paddle (left)
        self.player_paddle = self.canvas.create_rectangle(
            50, self.height//2 - self.paddle_height//2,
            50 + self.paddle_width, self.height//2 + self.paddle_height//2,
            fill="#0072CE", outline=""  # PS5 blue
        )
        
        # Create AI paddle (right)
        self.ai_paddle = self.canvas.create_rectangle(
            self.width - 50 - self.paddle_width, self.height//2 - self.paddle_height//2,
            self.width - 50, self.height//2 + self.paddle_height//2,
            fill="#5D5D5D", outline=""  # PS5 gray
        )
        
        # Create ball
        self.ball = self.canvas.create_oval(
            self.width//2 - self.ball_size//2, self.height//2 - self.ball_size//2,
            self.width//2 + self.ball_size//2, self.height//2 + self.ball_size//2,
            fill="#FF9B1A", outline=""  # PS5 orange
        )
        
        # Score display
        self.player_score = 0
        self.ai_score = 0
        self.score_display = self.canvas.create_text(
            self.width//2, 40,
            text="0 : 0",
            fill="#aaa",
            font=("Arial", 24, "bold")
        )
        
        # FPS display
        self.fps_display = self.canvas.create_text(
            80, 30,
            text="FPS: 60",
            fill="#666",
            font=("Arial", 12)
        )
        
        # Initialize movement parameters
        self.ball_dx = self.ball_speed * random.choice([-1, 1])
        self.ball_dy = self.ball_speed * random.choice([-1, 1])
        self.player_paddle_dy = 0
        
        # Key bindings
        self.root.bind("<KeyPress-w>", lambda e: self.set_paddle_speed("player", -self.paddle_speed))
        self.root.bind("<KeyPress-s>", lambda e: self.set_paddle_speed("player", self.paddle_speed))
        self.root.bind("<KeyRelease-w>", lambda e: self.stop_paddle("player"))
        self.root.bind("<KeyRelease-s>", lambda e: self.stop_paddle("player"))
        
        # Start game loop
        self.last_frame_time = time.time()
        self.game_loop()
    
    def set_paddle_speed(self, paddle, speed):
        if paddle == "player":
            self.player_paddle_dy = speed
    
    def stop_paddle(self, paddle):
        if paddle == "player":
            self.player_paddle_dy = 0
    
    def move_paddles(self):
        # Move player paddle
        player_pos = self.canvas.coords(self.player_paddle)
        if (player_pos[1] + self.player_paddle_dy > 0 and 
            player_pos[3] + self.player_paddle_dy < self.height):
            self.canvas.move(self.player_paddle, 0, self.player_paddle_dy)
        
        # AI paddle movement
        ball_pos = self.canvas.coords(self.ball)
        ai_pos = self.canvas.coords(self.ai_paddle)
        ai_center = (ai_pos[1] + ai_pos[3]) / 2
        ball_center = (ball_pos[1] + ball_pos[3]) / 2
        
        # AI follows ball with some imperfection
        if ball_center < ai_center - 10:
            ai_dy = -self.paddle_speed * self.ai_difficulty
        elif ball_center > ai_center + 10:
            ai_dy = self.paddle_speed * self.ai_difficulty
        else:
            ai_dy = 0
            
        # Add random imperfection to AI
        if random.random() < 0.2:  # 20% chance of error
            ai_dy *= random.uniform(0.5, 1.5)
        
        if (ai_pos[1] + ai_dy > 0 and 
            ai_pos[3] + ai_dy < self.height):
            self.canvas.move(self.ai_paddle, 0, ai_dy)
    
    def move_ball(self):
        self.canvas.move(self.ball, self.ball_dx, self.ball_dy)
        ball_pos = self.canvas.coords(self.ball)
        
        # Wall collisions (top/bottom)
        if ball_pos[1] <= 0 or ball_pos[3] >= self.height:
            self.ball_dy *= -1
            self.sounds["wall"].play()
            self.create_impact_effect(ball_pos)
        
        # Paddle collisions
        player_pos = self.canvas.coords(self.player_paddle)
        ai_pos = self.canvas.coords(self.ai_paddle)
        
        # Player paddle collision
        if (ball_pos[0] <= player_pos[2] and 
            ball_pos[2] >= player_pos[0] and 
            ball_pos[3] >= player_pos[1] and 
            ball_pos[1] <= player_pos[3]):
            self.ball_dx = abs(self.ball_dx) * 1.05
            # Add spin based on paddle movement
            self.ball_dy += self.player_paddle_dy * 0.2
            self.sounds["paddle"].play()
            self.create_impact_effect(ball_pos)
        
        # AI paddle collision
        elif (ball_pos[2] >= ai_pos[0] and 
              ball_pos[0] <= ai_pos[2] and 
              ball_pos[3] >= ai_pos[1] and 
              ball_pos[1] <= ai_pos[3]):
            self.ball_dx = -abs(self.ball_dx) * 1.05
            self.sounds["paddle"].play()
            self.create_impact_effect(ball_pos)
        
        # Scoring
        if ball_pos[0] <= 0:
            self.ai_score += 1
            self.sounds["score"].play()
            self.reset_ball()
        elif ball_pos[2] >= self.width:
            self.player_score += 1
            self.sounds["score"].play()
            self.reset_ball()
    
    def create_impact_effect(self, pos):
        """Create a PS5-style impact effect"""
        x, y = (pos[0] + pos[2])/2, (pos[1] + pos[3])/2
        # PS5 blue effect
        effect = self.canvas.create_oval(
            x-15, y-15, x+15, y+15,
            fill="", outline="#0072CE",
            width=3, dash=(5, 3)
        )
        self.canvas.after(100, lambda: self.canvas.delete(effect))
    
    def reset_ball(self):
        self.canvas.coords(self.ball, 
                          self.width//2 - self.ball_size//2,
                          self.height//2 - self.ball_size//2,
                          self.width//2 + self.ball_size//2,
                          self.height//2 + self.ball_size//2)
        self.ball_dx = self.ball_speed * random.choice([-1, 1])
        self.ball_dy = self.ball_speed * random.choice([-1, 1])
        self.canvas.itemconfig(self.score_display, text=f"{self.player_score} : {self.ai_score}")
        
        # Increase difficulty as score increases
        self.ai_difficulty = min(0.95, 0.7 + (self.ai_score + self.player_score) * 0.02)
    
    def update_fps(self):
        current_time = time.time()
        elapsed = current_time - self.last_frame_time
        self.last_frame_time = current_time
        fps = 1.0 / elapsed if elapsed > 0 else 60
        self.canvas.itemconfig(self.fps_display, text=f"FPS: {int(fps)}")
    
    def game_loop(self):
        self.update_fps()
        self.move_paddles()
        self.move_ball()
        
        # Performance optimization: Self-adjusting delay
        elapsed = time.time() - self.last_frame_time
        delay = max(1, int(16.67 - elapsed*1000))  # Target 60 FPS (16.67ms/frame)
        
        self.root.after(delay, self.game_loop)

if __name__ == "__main__":
    root = tk.Tk()
    game = PS5Pong(root)
    root.mainloop()
