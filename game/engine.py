import threading
import time
import math


class AnimationThread(threading.Thread):
    def __init__(self, animation_func, *args, **kwargs):
        super().__init__(daemon=True)
        self.animation_func = animation_func
        self.args = args
        self.kwargs = kwargs
        self._stop_event = threading.Event()
    
    def run(self):
        while not self._stop_event.is_set():
            result = self.animation_func(*self.args, **self.kwargs)
            if not result:
                break
    
    def stop(self):
        self._stop_event.set()


class FlipAnimation:
    def __init__(self, duration=0.5):
        self.duration = duration
        self.start_time = None
        self.is_running = False
        self.progress = 0.0
    
    def start(self):
        self.start_time = time.time()
        self.is_running = True
        self.progress = 0.0
    
    def update(self):
        if not self.is_running:
            return False
        
        elapsed = time.time() - self.start_time
        self.progress = min(elapsed / self.duration, 1.0)
        
        if self.progress >= 1.0:
            self.is_running = False
            return False
        
        return True
    
    def get_scale(self):
        if self.progress < 0.5:
            return 1.0 - 2.0 * self.progress
        else:
            return 2.0 * (self.progress - 0.5)
    
    def is_halfway(self):
        return self.progress >= 0.5


class Particle:
    def __init__(self, x, y, vx, vy, color, size, lifetime=1.0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.size = size
        self.lifetime = lifetime
        self.start_time = time.time()
        self.alpha = 255
    
    def update(self, gravity=980.0, dt=0.016):
        self.vy += gravity * dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        elapsed = time.time() - self.start_time
        remaining = self.lifetime - elapsed
        if remaining > 0:
            self.alpha = int(255 * (remaining / self.lifetime))
        else:
            self.alpha = 0
        
        return self.alpha > 0
    
    def is_alive(self):
        return self.alpha > 0


class ParticleSystem:
    def __init__(self):
        self.particles = []
        self.lock = threading.Lock()
    
    def add_particle(self, particle):
        with self.lock:
            self.particles.append(particle)
    
    def create_explosion(self, x, y, colors, count=20):
        import random
        with self.lock:
            for _ in range(count):
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(100, 300)
                vx = math.cos(angle) * speed
                vy = math.sin(angle) * speed - 100
                color = random.choice(colors)
                size = random.uniform(3, 8)
                lifetime = random.uniform(0.5, 1.5)
                
                particle = Particle(x, y, vx, vy, color, size, lifetime)
                self.particles.append(particle)
    
    def update(self, gravity=980.0, dt=0.016):
        with self.lock:
            self.particles = [
                p for p in self.particles if p.update(gravity, dt)
            ]
    
    def get_particles(self):
        with self.lock:
            return list(self.particles)
    
    def clear(self):
        with self.lock:
            self.particles.clear()


class GameEngine:
    def __init__(self):
        self.particle_system = ParticleSystem()
        self.animations = []
        self.animation_lock = threading.Lock()
        self.running = False
    
    def start(self):
        self.running = True
    
    def stop(self):
        self.running = False
    
    def update(self, dt=0.016):
        self.particle_system.update(dt=dt)
        
        with self.animation_lock:
            self.animations = [
                anim for anim in self.animations if anim.update()
            ]
    
    def add_animation(self, animation):
        with self.animation_lock:
            self.animations.append(animation)
            animation.start()
    
    def create_match_effect(self, x, y):
        colors = [(255, 215, 0), (255, 193, 7), (255, 250, 240), (210, 180, 140)]
        self.particle_system.create_explosion(x, y, colors, count=15)
    
    def draw_particles(self, surface):
        import pygame
        particles = self.particle_system.get_particles()
        for particle in particles:
            if particle.alpha > 0:
                temp_surface = pygame.Surface(
                    (int(particle.size * 2), int(particle.size * 2)),
                    pygame.SRCALPHA
                )
                color_with_alpha = (*particle.color[:3], particle.alpha)
                pygame.draw.circle(
                    temp_surface, color_with_alpha,
                    (int(particle.size), int(particle.size)),
                    int(particle.size)
                )
                surface.blit(
                    temp_surface,
                    (int(particle.x - particle.size), int(particle.y - particle.size))
                )
