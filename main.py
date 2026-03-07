import pygame
from PIL import Image
import random
import time
import os
import math

from helper import get_season, get_weather, update_discord_avt


os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

WIDTH, HEIGHT = 900, 600
OUTPUT_SIZE = (512, 512)
FRAMES = 180
DURATION = 33
CITY = os.getenv("CITY_NAME", "new york")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

original_bg = pygame.image.load("static/bg.jpg")
original_bg = pygame.transform.scale(original_bg, (WIDTH, HEIGHT))

season_tints = {
    "spring": (255, 182, 220, 60),  # Light Pink
    "summer": (180, 220, 255, 45),  # Light Yellow
    "autumn": (255, 190, 120, 80),  # Light Orange
    "winter": (240, 245, 255, 70),  # Light Blue
}

tinted_bgs = {}
for s, c in season_tints.items():
    tinted = original_bg.copy()
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill(c)
    tinted.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    tinted_bgs[s] = tinted

character = {
    ("spring", "clear"): pygame.image.load("static/char_spring_clear.png"),
    ("spring", "rain"): pygame.image.load("static/char_spring_rain.png"),
    ("summer", "clear"): pygame.image.load("static/char_summer_clear.png"),
    ("summer", "rain"): pygame.image.load("static/char_summer_rain.png"),
    ("autumn", "clear"): pygame.image.load("static/char_autumn_clear.png"),
    ("autumn", "rain"): pygame.image.load("static/char_autumn_rain.png"),
    ("winter", "clear"): pygame.image.load("static/char_winter_clear.png"),
    ("winter", "rain"): pygame.image.load("static/char_winter_rain.png"),
}
for key in character:
    character[key] = pygame.transform.scale(character[key], (280, 380))

class practice:
    _surf_cache = {}

    def __init__(self, season, weather):
        self.season = season
        self.weather = weather
        self.image = None
        self.reset()

    def reset(self, initial=False):
        self.x = random.randint(-50, WIDTH + 50)
        if initial:
            self.y = random.randint(-HEIGHT, HEIGHT)
        else:
            self.y = random.randint(-200, -0)

        self.vx = random.uniform(-1.2, 1.2)
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-2, 2)

        self.layer = random.choices([1, 2, 3], weights=[50, 30, 20])[0]
        self.speed_multiplier = 0.7 + (self.layer * 0.4) 
        self.size_multiplier = 0.5 + (self.layer * 0.5)

        if self.weather == "rain":
            self.vy = random.uniform(12, 22) * self.speed_multiplier
            self.color = random.choice([(140, 180, 255), (160, 200, 255), (120, 160, 240)])
            self.size = random.randint(1, 3) * self.size_multiplier
            self.length = random.randint(12, 30)
            self.fade_length = self.length // 2
            self.type = "rain"
        else:
            if self.season == "spring":
                self.vy = random.uniform(1.0, 2.8) * self.speed_multiplier
                self.vx = random.uniform(-0.8, 0.8) + math.sin(self.y * 0.02) * 0.4
                self.color = random.choice([(255,182,193), (255,200,220), (240,150,180)])
                self.size = random.randint(3, 5) * self.size_multiplier
                self.rotation = random.uniform(0, 360)
                self.rotation_speed = random.uniform(-3, 3)
                self.type = "petal"
                self._get_cached_petal()
            elif self.season == "summer":
                self.vy = random.uniform(-0.5, 1.5) * self.speed_multiplier
                self.vx = random.uniform(-1.0, 1.0) + math.cos(self.y * 0.03) * 0.6
                self.color = (255,240,100)
                self.brightness = random.randint(160, 255)
                self.size = random.randint(4, 7) * self.size_multiplier
                self.type = "firefly"
                self._get_cached_firefly()
            elif self.season == "autumn":
                self.vy = random.uniform(1.8, 4.2) * self.speed_multiplier
                self.vx = random.uniform(-1.5, 1.5) + math.sin(self.y * 0.015) * 1.2
                self.color = random.choice([(255,140,0), (220,120,0), (255,215,0), (180,90,30)])
                self.size = random.randint(6, 12) * self.size_multiplier
                self.rotation = random.uniform(0, 360)
                self.rotation_speed = random.uniform(-5, 5)
                self.type = "leaf"
                self.base_points = [
                    (0, 0),
                    (self.size, self.size//2),
                    (self.size//2, self.size*1.5),
                    (-self.size//2, self.size*1.2),
                    (-self.size, self.size//3),
                ]
            else:
                self.vy = random.uniform(1.5, 3.0)
                self.vx = random.uniform(-1.0, 1.0) + math.sin(self.y * 0.01) * 0.5
                self.color = random.choice([(240, 255, 255), (220, 240, 255), (200, 230, 255)])
                self.size = random.randint(2, 4)
                self.alpha = random.randint(180, 255)
                self.type = "snow"
                self._get_cached_snow()

    def _get_cached_petal(self):
        key = (self.size, self.color)
        if key not in self._surf_cache:
            width = self.size * 2
            height = self.size * 4
            surf = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.ellipse(surf, self.color, (0, 0, surf.get_width(), surf.get_height()))
            self._surf_cache[key] = surf
        self.image = self._surf_cache[key]

    def _get_cached_firefly(self):
        key = (self.size, self.color)
        if key not in self._surf_cache:
            width = self.size * 2
            height = self.size * 2
            surf = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.circle(surf, self.color, (surf.get_width()//2, surf.get_height()//2), self.size)
            self._surf_cache[key] = surf
        self.image = self._surf_cache[key]

    def _get_cached_snow(self):
        key = ("snow", self.size, self.color, self.alpha)
        if key not in self._surf_cache:
            s_size = self.size * 2 + 6
            surf = pygame.Surface((s_size, s_size), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*self.color, self.alpha), (surf.get_width()//2, surf.get_height()//2), self.size)
            pygame.draw.circle(surf, (255, 255, 255, 180), (self.size + 2, self.size + 2), self.size + 2, 1)
            self._surf_cache[key] = surf
        self.image = self._surf_cache[key]
    
    def update(self):
        if self.type == "petal":
            self.vx = math.sin(self.y * 0.02) * 0.8
        elif self.type == "firefly":
            self.vx = math.cos(self.y * 0.03) * 1.0
        elif self.type == "leaf":
            self.vx = math.sin(self.y * 0.015) * 1.5
        elif self.type == "snow":
            self.vx = math.sin(self.y * 0.01) * 0.8

        self.x += self.vx
        self.y += self.vy

        if self.y > HEIGHT + 200 or self.x < -50 or self.x > WIDTH:
            self.reset()
    
    def draw(self, surface):
        if self.type == "rain":
            end_y = self.y + self.length
            pygame.draw.line(surface, self.color, (self.x, self.y), (self.x, end_y), self.size)
            if self.length > 20:
                fade_color = (*self.color, 80)
                pygame.draw.line(surface, fade_color, (self.x, end_y - self.fade_length), (self.x, end_y), self.size)
        elif self.type == "petal":
            rotated = pygame.transform.rotate(self.image, self.rotation)
            rot_rect = rotated.get_rect(center=(self.x, self.y))
            surface.blit(rotated, rot_rect.topleft)
            self.rotation += self.rotation_speed
        elif self.type == "firefly" or self.type == "snow":
            rect = self.image.get_rect(center=(self.x, self.y))
            surface.blit(self.image, rect.topleft)
        elif self.type == "leaf":
            rotated_points = [pygame.math.Vector2(p).rotate(self.rotation) + (self.x, self.y) for p in self.base_points]
            pygame.draw.polygon(surface, self.color, rotated_points)
            self.rotation += self.rotation_speed


class DynamicBackground:
    def __init__(self, original_bg, season):
        self.original = original_bg
        self.season = season
        self.glow_time = 0
        self.update_tint()

    def update_tint(self):
        c = season_tints[self.season]
        self.tinted = self.original.copy()
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill(c)
        self.tinted.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)


    def draw(self, surface, frame_idx=None):
        surface.blit(self.tinted, (0, 0))

        self.glow_time += 0.05
        pulse = (math.sin(self.glow_time) + 1) / 2 * 60 + 20
        glow_color = (255, 240, 200, int(pulse)) if self.season in ["autumn", "summer"] else (200, 220, 255, int(pulse))
        glow_position = [(200, 300), (400, 350), (600, 280)]
        for pos in glow_position:
            glow_radius = 50 + int(pulse / 4)
            glow_surf = pygame.Surface((glow_radius*2, glow_radius*2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, glow_color, (glow_radius, glow_radius), glow_radius)
            surface.blit(glow_surf, (pos[0] - glow_radius, pos[1] - glow_radius))


def generate_live_gif(season, weather):
    screen = pygame.Surface((WIDTH, HEIGHT))
    bg_particles = []
    fg_particles = []
    for _ in range(700):
        p = practice(season, weather)
        p.reset(initial=True)
        if p.layer == 1:
            bg_particles.append(p)
        else:
            fg_particles.append(p)

    dyn_bg = DynamicBackground(original_bg, season)
    
    frames = []
    for frame_idx in range(FRAMES):
        dyn_bg.draw(screen, frame_idx)

        for p in bg_particles:
            p.update()
            p.draw(screen)

        base_x = WIDTH // 2 - 140
        base_y = HEIGHT - 380 - 50

        scale_factor = 1.0 + math.sin(frame_idx * 0.12) * 0.005
        scaled_char = pygame.transform.smoothscale(
            character.get((season, weather), character[("autumn", "clear")]),
            (int(280 * scale_factor), int(380 * scale_factor))
        )

        char_rect = scaled_char.get_rect(midbottom=(base_x + 140, base_y + 380))

        screen.blit(scaled_char, char_rect.topleft)

        for p in fg_particles:
            p.update()
            p.draw(screen)

        pil_image = Image.frombytes("RGBA", screen.get_size(), pygame.image.tostring(screen, "RGBA"))
        cropped = pil_image.crop((170, 50, 730, 570))
        resized = cropped.convert("RGB").resize(OUTPUT_SIZE, Image.LANCZOS)
        frames.append(resized)

    filename = "live_aether_avatar.gif"
    frames[0].save(filename, save_all=True, append_images=frames[1:], 
                   optimize=True, duration=DURATION, loop=0)
    
    
current_season = get_season()
current_weather = get_weather(CITY, WEATHER_API_KEY)
generate_live_gif(current_season, current_weather)

last_season = current_season
last_weather = current_weather

def update_gif():
    global last_season, last_weather
    current_season = get_season()
    current_weather = get_weather(CITY, WEATHER_API_KEY)
    if current_season != last_season or current_weather != last_weather:
        generate_live_gif(current_season, current_weather)
        last_season = current_season
        last_weather = current_weather
        update_discord_avt("live_aether_avatar.gif", DISCORD_TOKEN)


if __name__ == "__main__":
    update_gif()