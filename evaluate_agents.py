import optuna
import random
import numpy as np
import matplotlib.pyplot as plt
from scripts.game import Game
from scripts.agent import RandomAgent, IntelAgent, IntelAgent2


# --- Simulation function ---
def simulate_battle(agent, num_games=50, seed=42, return_all=False):
    """
    Runs several new Game() instances and returns performance metrics.
    """
    total_score = 0
    total_health = 0
    total_victories = 0
    scores = []

    random.seed(seed)

    for _ in range(num_games):
        game = Game(simulation=True, log_path="sim_log.txt")
        game.set_agent(agent)
        result = game.run()

        if isinstance(result, tuple):
            score, victory = result
        else:
            score = result
            victory = 1 if game.player.alive else 0

        total_score += score
        total_health += max(game.player.health, 0)
        total_victories += victory
        scores.append(score)

    avg_score = total_score / num_games
    avg_health = total_health / num_games
    avg_victories = total_victories / num_games

    if return_all:
        return avg_score, avg_health, avg_victories, scores
    return avg_score, avg_health, avg_victories


# --- Optuna objective for IntelAgent ---
def objective_intel1(trial):
    health_weight = trial.suggest_float("health_weight", 0.0, 1.0)
    threshold = trial.suggest_float("stay_and_fight_threshold", 0.1, 10.0, log=True)

    agent = IntelAgent(health_weight=health_weight, STAY_AND_FIGHT_THRESHOLD=threshold)
    score, health, victories = simulate_battle(agent, num_games=50)
    return score


# --- Optuna objective for IntelAgent2 ---
def objective_intel2(trial):
    health_weight = trial.suggest_float("health_weight", 0.0, 0.8)
    score_weight = trial.suggest_float("score_weight", 0.0, 0.8)
    if health_weight + score_weight >= 1.0:
        raise optuna.TrialPruned()

    threshold = trial.suggest_float("stay_and_fight_threshold", 0.1, 10.0, log=True)

    agent = IntelAgent2(
        health_weight=health_weight,
        score_weight=score_weight,
        STAY_AND_FIGHT_THRESHOLD=threshold
    )
    score, health, victories = simulate_battle(agent, num_games=50)
    return score


# --- Run both Optuna optimizations ---
def run_optimizations():
    print("Optimizing IntelAgent 1...")
    sampler1 = optuna.samplers.TPESampler(seed=42)
    study1 = optuna.create_study(direction="maximize", sampler=sampler1)
    study1.optimize(objective_intel1, n_trials=100, n_jobs=1)

    print("\nOptimizing IntelAgent 2...")
    sampler2 = optuna.samplers.TPESampler(seed=43)
    study2 = optuna.create_study(direction="maximize", sampler=sampler2)
    study2.optimize(objective_intel2, n_trials=100, n_jobs=1)

    print("\nBest Results:")
    print("IntelAgent 1:", study1.best_params, f"score={study1.best_value:.2f}")
    print("IntelAgent 2:", study2.best_params, f"score={study2.best_value:.2f}")

    return study1, study2


# --- Compare all agents ---
def compare_agents(study1, study2, num_games=50):
    agents = []

    # Random
    random_agent = RandomAgent()
    agents.append(("Random", random_agent))

    # Intel 1
    p1 = study1.best_params
    intel1 = IntelAgent(
        health_weight=p1["health_weight"],
        STAY_AND_FIGHT_THRESHOLD=p1["stay_and_fight_threshold"]
    )
    agents.append(("2-parameter", intel1))

    # Intel 2
    p2 = study2.best_params
    intel2 = IntelAgent2(
        health_weight=p2["health_weight"],
        score_weight=p2["score_weight"],
        STAY_AND_FIGHT_THRESHOLD=p2["stay_and_fight_threshold"]
    )
    agents.append(("3-parameter", intel2))

    results = []
    all_scores = []
    for name, agent in agents:
        score, health, victories, scores = simulate_battle(agent, num_games=num_games, seed=24, return_all=True)
        results.append((name, score, health, victories))
        all_scores.append(scores)

    labels = [r[0] for r in results]
    scores = [r[1] for r in results]
    victories = [r[3] * 100 for r in results]

    # --- Chart 1: Average Score ---
    plt.figure(figsize=(7, 5))
    plt.bar(labels, scores, color=["tomato", "royalblue", "seagreen"])
    plt.title("Average Score Comparison")
    plt.ylabel("Average Score")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.show()

    # --- Chart 2: Victory Rate ---
    plt.figure(figsize=(7, 5))
    plt.bar(labels, victories, color=["tomato", "royalblue", "seagreen"])
    plt.title("Average Victory Rate")
    plt.ylabel("Victory %")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.show()

    # --- Chart 3: Score Distributions ---
    plt.figure(figsize=(8, 6))
    plt.boxplot(all_scores, labels=labels, patch_artist=True,
                boxprops=dict(facecolor="lightgray", color="black"),
                medianprops=dict(color="red", linewidth=2))
    plt.title("Score Distributions Across Games")
    plt.ylabel("Game Score")
    plt.grid(True, linestyle="--", alpha=0.4)
    plt.tight_layout()
    plt.show()

    print("\nAgent Performance Summary")
    for name, score, health, victories in results:
        print(f"{name:10} | Score={score:.2f}, Health={health:.2f}, Victories={victories*100:.1f}%")


# --- Main ---
if __name__ == "__main__":
    study1, study2 = run_optimizations()
    compare_agents(study1, study2)
