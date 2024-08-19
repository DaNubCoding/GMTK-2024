from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.core.game import Game

from src.sprites.blob import Blob, ParticleBlob
from src.core.glpg import Texture, Shader
from src.core.scene import Scene
from src.utils import Timer
import src.assets as assets

from random import randint, uniform
from math import cos, sin, exp2, pi
import pygame

class MainScene(Scene):
    def __init__(self, game: Game) -> None:
        super().__init__(game)

        self.blob_shader = Shader(game.window, "assets/shaders/metaball.frag")
        surf = pygame.Surface(game.window.size, pygame.SRCALPHA)
        self.blob_texture = Texture(game.window, surf, self.blob_shader)

        self.blobs = []
        self.blob_count = 0
        self.expand_speed = 0.03
        self.linear_radius = 4
        self.radius = exp2(self.linear_radius)
        self.main_blob = Blob(self, (400, 400), self.radius)
        self.blob_timer = Timer(lambda r: 4 / r if r < 80 else 1 / r, self.main_blob.radius)

        self.fractal_shader = Shader(game.window, "assets/shaders/fractal.frag")
        self.fractal_texture = Texture(game.window, assets.noise_image, self.fractal_shader)
        self.fractal_post_shader = Shader(game.window, "assets/shaders/fractal_post.frag")
        surf = pygame.Surface(game.window.size, pygame.SRCALPHA)
        self.fractal_post_texture = Texture(game.window, surf, self.fractal_post_shader)
        self.zoom = 0
        self.zoom_speed = 0

    def update(self, dt: float) -> None:
        r = self.main_blob.radius
        for _ in range(self.blob_timer.ended_and_reset(r)):
            angle = uniform(0, 2 * pi)
            x, y = 400 + max(0, r - 50) * cos(angle), 400 + max(0, r - 50) * sin(angle)
            ParticleBlob(self, (x, y), (cos(angle + randint(-10, 10)), sin(angle + randint(-10, 10))), randint(2, 12))

        self.linear_radius += self.expand_speed * dt
        self.radius = exp2(self.linear_radius)
        self.main_blob.radius = self.radius / exp2(self.zoom)
        if self.linear_radius > 50:
            self.zoom_speed *= 0.9995
        elif self.linear_radius > 7.5:
            self.zoom_speed += (self.expand_speed - self.zoom_speed) * 0.02
        self.zoom += self.zoom_speed * dt

        self.blob_shader.send("u_metaballCount", self.blob_count)
        self.blob_shader.send("u_metaballs", [self.blobs[i].data if i < len(self.blobs) else (0, 0, 0) for i in range(500)])

        self.fractal_shader.send("u_zoom", self.zoom)

        self.sprite_manager.update(dt)

    def draw(self, screen: pygame.Surface) -> None:
        self.fractal_post_texture.blit(self.fractal_texture, (0, 0))
        self.game.window.blit(self.fractal_post_texture, (0, 0))
        self.game.window.blit(self.blob_texture, (0, 0))
        self.sprite_manager.draw(screen)

    def add_blob(self, blob: Blob) -> None:
        self.blobs.append(blob)
        self.add(blob)
        self.blob_count += 1

    def remove_blob(self, blob: Blob) -> None:
        self.blobs.remove(blob)
        self.remove(blob)
        self.blob_count -= 1
