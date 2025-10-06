import os
import neat
import random
from scripts.player import Player
from scripts.agents import NEAT_Agent
from scripts.game import Game

gen = 0
best_fitness_ever = float('-inf')

def eval_genomes(genomes, config):
    """
    Evaluate populations of genomes in the game environment.
    """
    global gen, best_fitness_ever
    gen += 1

    # Use different random seeds for each generation to increase diversity
    random.seed(42 + gen)

    nets = []
    agents = []
    ge = []

    for genome_id, genome in genomes:
        genome.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        
        nets.append(net)
        agent = NEAT_Agent(net)
        agents.append(Player(human=False, agent=agent))
        ge.append(genome)
    
    # Run multiple games per agent
    num_games = 3
    
    for i, agent in enumerate(agents):
        total_fitness = 0
        wins = 0
        
        for game_num in range(num_games):
            # Vary random seed per game for diversity
            random.seed(42 + gen * 1000 + i * 10 + game_num)
            
            game = Game(player=agent)
            initial_deck_size = len(game.deck.cards)
            
            result = game.run()
            
            # Enhanced fitness calculation
            base_score = result
            survival_bonus = agent.health * 2 if agent.alive else 0
            cards_cleared = initial_deck_size - len(game.deck.cards)
            progress_bonus = cards_cleared * 0.5
            
            if agent.alive and game.all_rooms_cleared():
                win_bonus = 100
                wins += 1
            else:
                win_bonus = 0
            
            death_penalty = -20 if not agent.alive else 0
            
            fitness = base_score + survival_bonus + progress_bonus + win_bonus + death_penalty
            fitness = max(fitness, -50)  # Floor to prevent too negative
            
            total_fitness += fitness
        
        # Average fitness across games
        ge[i].fitness = total_fitness / num_games
        
        # Track best performer
        if ge[i].fitness > best_fitness_ever:
            best_fitness_ever = ge[i].fitness
            print(f"\n NEW BEST FITNESS: {best_fitness_ever:.2f} (Gen {gen}, Wins: {wins}/{num_games})")
    
    # Print generation statistics
    avg_fitness = sum(g.fitness for g in ge) / len(ge)
    max_fitness = max(g.fitness for g in ge)
    min_fitness = min(g.fitness for g in ge)
    
    print(f"Gen {gen:3d} | Avg: {avg_fitness:7.2f} | Max: {max_fitness:7.2f} | Min: {min_fitness:7.2f} | Best Ever: {best_fitness_ever:7.2f}")


def run(config_file):
    """
    Run the NEAT algorithm to train a neural network.
    """
    config = neat.config.Config(
        neat.DefaultGenome, 
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet, 
        neat.DefaultStagnation,
        config_file
    )

    # Create the population
    p = neat.Population(config)

    # Add reporters
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(10, filename_prefix='checkpoints/neat-checkpoint-'))

    # Run for up to 100 generations (increased from 50)
    winner = p.run(eval_genomes, 100)

    # Show final stats
    print('\n' + '='*50)
    print('TRAINING COMPLETE')
    print('='*50)
    print(f'Best genome fitness: {winner.fitness}')
    print(f'Best fitness achieved: {best_fitness_ever}')

    # Save the winner
    os.makedirs('models', exist_ok=True)
    with open("models/best.pickle", "wb") as f:
        import pickle
        pickle.dump(winner, f)
    
    print("\nBest model saved to models/best.pickle")

    return winner, stats


if __name__ == '__main__':
    # Ensure checkpoint directory exists
    os.makedirs('checkpoints', exist_ok=True)
    
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'unified.txt')
    
    winner, stats = run(config_path)