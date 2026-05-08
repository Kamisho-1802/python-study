import pygame

GRAVITY = 0.5
JUMP_VELOCITY = -10


class Bird:
    WIDTH = 34
    HEIGHT = 24
    COLOR = (255, 220, 0)
    EYE_COLOR = (0, 0, 0)
    WING_COLOR = (255, 180, 0)

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocity = 0
        self.alive = True
        self.score = 0
        self.fitness = 0

    def jump(self):
        self.velocity = JUMP_VELOCITY

    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity
        self.fitness += 0.1

    def get_rect(self):
        return pygame.Rect(
            self.x - self.WIDTH // 2,
            self.y - self.HEIGHT // 2,
            self.WIDTH,
            self.HEIGHT,
        )

    def draw(self, screen):
        cx = int(self.x)
        cy = int(self.y)

        angle = max(-30, min(30, -self.velocity * 3))
        surf = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)

        pygame.draw.ellipse(surf, self.COLOR, (0, 0, self.WIDTH, self.HEIGHT))

        wing_y = self.HEIGHT // 2 + 2
        pygame.draw.ellipse(surf, self.WING_COLOR, (4, wing_y, 14, 8))

        pygame.draw.circle(surf, (255, 255, 255), (self.WIDTH - 8, self.HEIGHT // 2 - 2), 5)
        pygame.draw.circle(surf, self.EYE_COLOR, (self.WIDTH - 6, self.HEIGHT // 2 - 2), 3)

        pygame.draw.polygon(surf, (255, 140, 0), [
            (self.WIDTH, self.HEIGHT // 2 - 2),
            (self.WIDTH + 6, self.HEIGHT // 2),
            (self.WIDTH, self.HEIGHT // 2 + 2),
        ])

        rotated = pygame.transform.rotate(surf, angle)
        rect = rotated.get_rect(center=(cx, cy))
        screen.blit(rotated, rect.topleft)
