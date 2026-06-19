import pygame
import random

PIPE_SPEED = 5
PIPE_GAP = 150
PIPE_WIDTH = 60
SCREEN_HEIGHT = 800
SCREEN_WIDTH = 600

PIPE_COLOR = (34, 139, 34)
PIPE_BORDER_COLOR = (0, 100, 0)
CAP_HEIGHT = 20


class Pipe:
    def __init__(self, x):
        self.x = x
        self.gap_y = random.randint(200, SCREEN_HEIGHT - 200)
        self.passed = False

    @property
    def top_rect(self):
        return pygame.Rect(self.x, 0, PIPE_WIDTH, self.gap_y - PIPE_GAP // 2)

    @property
    def bottom_rect(self):
        top = self.gap_y + PIPE_GAP // 2
        return pygame.Rect(self.x, top, PIPE_WIDTH, SCREEN_HEIGHT - top)

    def update(self):
        self.x -= PIPE_SPEED

    def is_off_screen(self):
        return self.x + PIPE_WIDTH < 0

    def collides_with(self, bird_rect):
        return self.top_rect.colliderect(bird_rect) or self.bottom_rect.colliderect(bird_rect)

    def draw(self, screen):
        top = self.top_rect
        bot = self.bottom_rect

        pygame.draw.rect(screen, PIPE_COLOR, top)
        pygame.draw.rect(screen, PIPE_BORDER_COLOR, top, 2)
        cap_top = pygame.Rect(top.x - 5, top.bottom - CAP_HEIGHT, PIPE_WIDTH + 10, CAP_HEIGHT)
        pygame.draw.rect(screen, PIPE_COLOR, cap_top)
        pygame.draw.rect(screen, PIPE_BORDER_COLOR, cap_top, 2)

        pygame.draw.rect(screen, PIPE_COLOR, bot)
        pygame.draw.rect(screen, PIPE_BORDER_COLOR, bot, 2)
        cap_bot = pygame.Rect(bot.x - 5, bot.top, PIPE_WIDTH + 10, CAP_HEIGHT)
        pygame.draw.rect(screen, PIPE_COLOR, cap_bot)
        pygame.draw.rect(screen, PIPE_BORDER_COLOR, cap_bot, 2)
