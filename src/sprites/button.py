from src.sprites.blob import Blob, ParticleBlob
from src.core.glpg import Texture, Shader
from src.core.render_layer import Layer
from src.core.sprite import Sprite
from src.core.scene import Scene
from src.utils import Vec, Timer
import src.assets as assets

from random import uniform, randint
from math import cos, sin, pi
from typing import Callable
import pygame

class Button(Sprite):
    def __init__(self, scene: Scene, pos: tuple[int, int], text: str, font_size: int, callback: Callable[[], None], scale: float = 1.0) -> None:
        super().__init__(scene, Layer.UI)
        self.pos = Vec(pos)
        self.text_surf = assets.fonts[font_size].render(text, True, (222, 222, 222))
        self.text_texture = Texture(self.game.window, self.text_surf)
        self.scale = scale
        self.radius = max(self.text_surf.get_size()) // 2 * 2.0 * self.scale
        self.shader = Shader(self.game.window, "assets/shaders/metaball.frag")
        surf = pygame.Surface((self.radius * 2 * 2, self.radius * 2 * 2), pygame.SRCALPHA)
        self.texture = Texture(self.game.window, surf, self.shader)
        self.callback = callback
        self.text_offset = Vec(0, 8)
        self.metaballs = []
        self.metaball_count = 0
        self.main_ball = Blob(self, self.texture.size // 2, self.radius)
        self.particle_timer = Timer(lambda: 0.15)
        self.particle_timer.start()
        self.hover = False

    def update(self, dt: float) -> None:
        if (hover := self.pos.distance_to(pygame.mouse.get_pos()) < self.radius + 5) and not self.hover:
            assets.button_hover.set_volume(uniform(0.4, 0.6))
            assets.button_hover.play()
            self.particle_timer = Timer(lambda: 0.03)
            self.particle_timer.start()
        elif not hover and self.hover:
            self.particle_timer = Timer(lambda: 0.15)
            self.particle_timer.start()

        self.hover = hover
        if self.hover:
            self.main_ball.radius += (self.radius * 1.3 - self.main_ball.radius) * 0.2 * dt
            if self.game.events.get(pygame.MOUSEBUTTONUP) and self.game.events[pygame.MOUSEBUTTONUP].button == 1:
                assets.button_click.set_volume(uniform(0.7, 0.9))
                assets.button_click.play()
                self.callback()
        else:
            self.main_ball.radius += (self.radius - self.main_ball.radius) * 0.2 * dt

        if self.particle_timer.ended_and_reset():
            angle = uniform(0, 2 * pi)
            ParticleBlob(self, self.texture.size // 2, (cos(angle) * 1.5, sin(angle) * 1.5), randint(5, 15))

        self.shader.send("u_metaballs", [self.metaballs[i].data if i < len(self.metaballs) else (0, 0, 0) for i in range(400)])
        self.shader.send("u_metaballCount", self.metaball_count)

    def draw(self, screen: pygame.Surface) -> None:
        self.game.texture.blit(self.texture, self.pos - Vec(self.radius * 2, self.radius * 2))
        self.game.texture.blit(self.text_texture, self.pos - Vec(self.text_texture.size) // 2 + self.text_offset)

    def add_blob(self, blob: Blob) -> None:
        self.metaballs.append(blob)
        self.scene.add(blob)
        self.metaball_count += 1

    def remove_blob(self, blob: Blob) -> None:
        self.metaballs.remove(blob)
        self.scene.remove(blob)
        self.metaball_count -= 1
