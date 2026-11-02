import math

import pygame

from gui.constants import ASSETS, BUTTON_SIZE, ICON_SIZE
from gui.playback import Playback


class HudRenderer():
    def __init__(self, total_turns: int) -> None:
        self._total_turns = total_turns
        self._font = pygame.font.Font(None, 32)
        self._icons: dict[str, pygame.Surface] = {}
        for name in ("left_skip", "pause", "play", "right_skip", "stop"):
            img = pygame.image.load(ASSETS / f"{name}.png").convert_alpha()
            self._icons[name] = self._fit(img, ICON_SIZE)

    def draw(self, surface: pygame.Surface, playback: Playback) -> None:
        self._draw_turn_counter(surface, playback.sim_time)
        self._draw_buttons(surface, playback)

    def _draw_turn_counter(self, surface: pygame.Surface,
                           sim_time: float) -> None:
        turn = min(math.floor(sim_time), self._total_turns)
        small = self._font.render(f"Turn: {turn}", False, (255, 255, 255))
        big = pygame.transform.scale(small, (small.get_width() * 2,
                                             small.get_height() * 2))
        width = surface.get_width()
        row_y = next(iter(self._button_rects(surface).values())).centery
        surface.blit(big, big.get_rect(midright=(width - 20, row_y)))

    @staticmethod
    def _fit(img: pygame.Surface, size: int) -> pygame.Surface:
        scale = size / max(img.get_size())
        new = (round(img.get_width() * scale),
               round(img.get_height() * scale))
        return pygame.transform.smoothscale(img, new)

    def _button_rects(self, surface: pygame.Surface
                      ) -> dict[str, pygame.Rect]:
        width, height = surface.get_size()
        names = ["left_skip", "play", "stop", "right_skip"]
        gap = 12
        total = len(names) * BUTTON_SIZE + (len(names) - 1) * gap
        x = (width - total) // 2
        y = height - BUTTON_SIZE - 20
        rects: dict[str, pygame.Rect] = {}
        for name in names:
            rects[name] = pygame.Rect(x, y, BUTTON_SIZE, BUTTON_SIZE)
            x += BUTTON_SIZE + gap
        return rects

    def _draw_buttons(self, surface: pygame.Surface,
                      playback: Playback) -> None:
        for name, rect in self._button_rects(surface).items():
            pygame.draw.rect(surface, (40, 40, 60), rect, border_radius=8)
            pygame.draw.rect(surface, (200, 200, 200), rect, width=2,
                             border_radius=8)
            icon_name = name
            if name == "play" and not playback.paused:
                icon_name = "pause"
            icon = self._icons[icon_name]
            surface.blit(icon, icon.get_rect(center=rect.center))

    def button_at(self, surface: pygame.Surface,
                  pos: tuple[int, int]) -> str | None:
        for name, rect in self._button_rects(surface).items():
            if rect.collidepoint(pos):
                return name
        return None
