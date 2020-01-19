import pygame
from parameters import screen


def print_text(mes, x, y, font_color=(0, 0, 0), font_size=30, font_type='data/18897.otf'):
    font_type = pygame.font.Font(font_type, font_size)
    text = font_type.render(mes, True, font_color)
    screen.blit(text, (x, y))