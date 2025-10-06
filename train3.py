import os
import neat
import multiprocessing
from scripts.player import Player
from scripts.agents import NEAT_Agent
from scripts.game import Game


gen = 0

def eval_genomes(genomes, config):
    """
    Evaluate populations of genomes in the game environment.
    """
    global gen
    gen += 1

    nets = []
    agents = []
    ge = []

    for genome_id, genome in genomes:
        genome.fitness = 0  # start with fitness level of 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        
        nets.append(net)
        agent = NEAT_Agent(net)
        agents.append(Player(human=False, agent=agent))

        ge.append(genome)
        

    # Evaluate all agents
    
    for i, agent in enumerate(agents):
        result = 0
        for x in range(5):  # Play 5 games each
            game = Game(player=agent)
            result += game.run()

        average_fitness = result / 5.0

        ge[i].fitness = average_fitness
    

def run(config_file):
    """
    runs the NEAT algorithm to train a neural network to play flappy bird.
    :param config_file: location of config file
    :return: None
    """
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(20))

    # Run for up to 50 generations.
    winner = p.run(eval_genomes, 2000)

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))

    # save the winner
    with open("best.pickle", "wb") as f:
        import pickle
        pickle.dump(winner, f)


if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'unified.txt')
    run(config_path)