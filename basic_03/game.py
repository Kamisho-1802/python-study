import pygame
from bird import Bird
from pipe import Pipe, PIPE_WIDTH, SCREEN_WIDTH, SCREEN_HEIGHT

FPS = 60
PIPE_SPAWN_INTERVAL = 90
BG_COLOR = (135, 206, 235)
GROUND_COLOR = (222, 184, 135)
GROUND_HEIGHT = 80
FONT_COLOR = (255, 255, 255)
SHADOW_COLOR = (0, 0, 0)


class FlappyBirdGame:
    def __init__(self, screen, manual=False):
        self.screen = screen
        self.manual = manual
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.SysFont("monospace", 32, bold=True)
        self.font_small = pygame.font.SysFont("monospace", 20)
        self.reset()

    def reset(self):
        self.birds = []
        self.pipes = []
        self.frame_count = 0
        self.score = 0
        self.generation = 0
        self.alive_count = 0

        if self.manual:
            self.birds = [Bird(100, SCREEN_HEIGHT // 2)]
            self.alive_count = 1

    def spawn_pipe(self):
        self.pipes.append(Pipe(SCREEN_WIDTH))

    def get_next_pipe(self):
        for pipe in self.pipes:
            if pipe.x + PIPE_WIDTH > 100:
                return pipe
        return None

    def update(self, nets=None):
        self.frame_count += 1

    # ← ここを変更：最初のフレームでもパイプをスポーン
        if self.frame_count == 1 or self.frame_count % PIPE_SPAWN_INTERVAL == 0:
            self.spawn_pipe()

        next_pipe = self.get_next_pipe()

        for i, bird in enumerate(self.birds):
            if not bird.alive:
                continue

        # ← ここを変更：パイプがなくても入力を与える
            if nets is not None:
                if next_pipe is not None:
                    inputs = (
                        bird.y / SCREEN_HEIGHT,
                        bird.velocity / 20.0,
                        (next_pipe.x - bird.x) / SCREEN_WIDTH,
                        next_pipe.gap_y / SCREEN_HEIGHT,
                        (next_pipe.gap_y + 75) / SCREEN_HEIGHT,
                    )
                else:
                    inputs = (
                        bird.y / SCREEN_HEIGHT,
                        bird.velocity / 20.0,
                        1.0,
                        0.5,
                        0.5,
                    )
                output = nets[i].activate(inputs)
                if output[0] > 0.0:
                    bird.jump()


            bird.update()

            if next_pipe is not None:
                dist = abs(bird.y - next_pipe.gap_y)
                bird.fitness += max(0, (SCREEN_HEIGHT - dist) / SCREEN_HEIGHT) * 0.05

            bird_rect = bird.get_rect()
            if bird.y - bird.HEIGHT // 2 < 0 or bird.y + bird.HEIGHT // 2 > SCREEN_HEIGHT - GROUND_HEIGHT:
                bird.alive = False
                bird.fitness -= 1.0
                continue

            for pipe in self.pipes:
                if pipe.collides_with(bird_rect):
                    bird.alive = False
                    bird.fitness -= 1.0
                    break

        for pipe in self.pipes:
            pipe.update()
            for bird in self.birds:
                if not bird.alive:
                    continue
                if not pipe.passed and pipe.x + PIPE_WIDTH < bird.x:
                    pipe.passed = True
                    self.score += 1
                    for b in self.birds:
                        if b.alive:
                            b.fitness += 5.0
                            b.score += 1

        self.pipes = [p for p in self.pipes if not p.is_off_screen()]
        self.alive_count = sum(1 for b in self.birds if b.alive)

    def handle_manual_input(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            for bird in self.birds:
                if bird.alive:
                    bird.jump()
        if event.type == pygame.MOUSEBUTTONDOWN:
            for bird in self.birds:
                if bird.alive:
                    bird.jump()

    def draw(self):
        self.screen.fill(BG_COLOR)

        pygame.draw.rect(
            self.screen, GROUND_COLOR,
            (0, SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_WIDTH, GROUND_HEIGHT)
        )
        pygame.draw.line(
            self.screen, (180, 140, 80),
            (0, SCREEN_HEIGHT - GROUND_HEIGHT),
            (SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_HEIGHT),
            3
        )

        for pipe in self.pipes:
            pipe.draw(self.screen)

        for bird in self.birds:
            if bird.alive:
                bird.draw(self.screen)

        self._draw_hud()

    def _draw_text(self, text, font, x, y, color=FONT_COLOR):
        shadow = font.render(text, True, SHADOW_COLOR)
        self.screen.blit(shadow, (x + 1, y + 1))
        surf = font.render(text, True, color)
        self.screen.blit(surf, (x, y))

    def _draw_hud(self):
        self._draw_text(f"SCORE: {self.score}", self.font_large, 10, 10)
        if not self.manual:
            self._draw_text(f"GEN: {self.generation}", self.font_large, 10, 50)
            self._draw_text(f"ALIVE: {self.alive_count}", self.font_small, 10, 90)

    def is_over(self):
        return self.alive_count == 0

    def run_manual(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False
                self.handle_manual_input(event)

            self.update()
            self.draw()

            if self.is_over():
                self._show_game_over()
                pygame.time.wait(2000)
                self.reset()

            pygame.display.flip()
            self.clock.tick(FPS)

    def _show_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        self.screen.blit(overlay, (0, 0))
        msg = self.font_large.render("GAME OVER", True, (255, 80, 80))
        self.screen.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, SCREEN_HEIGHT // 2 - 30))
        sc = self.font_small.render(f"Score: {self.score}", True, FONT_COLOR)
        self.screen.blit(sc, (SCREEN_WIDTH // 2 - sc.get_width() // 2, SCREEN_HEIGHT // 2 + 20))
        pygame.display.flip()
