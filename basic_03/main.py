import sys
import os
import pickle
import argparse
import pygame
import neat

from game import FlappyBirdGame
from bird import Bird
from pipe import SCREEN_WIDTH, SCREEN_HEIGHT

FPS = 120
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config-feedforward.txt")


def eval_genomes(genomes, config):
    screen = pygame.display.get_surface()
    clock = pygame.time.Clock()

    game = FlappyBirdGame(screen)
    nets = []
    birds = []

    for genome_id, genome in genomes:
        genome.fitness = 0.0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        bird = Bird(100, SCREEN_HEIGHT // 2)
        birds.append(bird)

    game.birds = birds
    game.alive_count = len(birds)
    game.generation += 1

    while not game.is_over():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

        game.update(nets=nets)
        game.draw()
        pygame.display.flip()
        clock.tick(FPS)

    for i, (genome_id, genome) in enumerate(genomes):
        genome.fitness = birds[i].fitness


def run_neat(replay_path=None):
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Flappy Bird AI — NEAT")

    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        CONFIG_PATH,
    )

    if replay_path:
        _replay(screen, config, replay_path)
        return

    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    population.add_reporter(neat.StatisticsReporter())

    best = population.run(eval_genomes, n=100)

    save_path = os.path.join(os.path.dirname(__file__), "best_genome.pkl")
    with open(save_path, "wb") as f:
        pickle.dump(best, f)
    print(f"\n最優秀ゲノムを保存しました: {save_path}")

    pygame.quit()


def _replay(screen, config, path):
    with open(path, "rb") as f:
        genome = pickle.load(f)

    net = neat.nn.FeedForwardNetwork.create(genome, config)
    clock = pygame.time.Clock()
    game = FlappyBirdGame(screen)
    bird = Bird(100, SCREEN_HEIGHT // 2)
    game.birds = [bird]
    game.alive_count = 1

    print("リプレイ中… ESCキーで終了")
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

        game.update(nets=[net])
        game.draw()
        pygame.display.flip()
        clock.tick(FPS)

        if game.is_over():
            game.birds = [Bird(100, SCREEN_HEIGHT // 2)]
            game.alive_count = 1
            game.pipes = []
            game.frame_count = 0
            game.score = 0


def run_manual():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Flappy Bird — 手動プレイ")
    game = FlappyBirdGame(screen, manual=True)
    game.run_manual()
    pygame.quit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Flappy Bird AI (NEAT)")
    parser.add_argument("--manual", action="store_true", help="手動プレイモード")
    parser.add_argument("--replay", metavar="FILE", help="保存済みゲノムを再生")
    args = parser.parse_args()

    if args.manual:
        run_manual()
    else:
        run_neat(replay_path=args.replay)
