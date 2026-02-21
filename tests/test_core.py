# test_core.py
# =============================================================================
# CORE FUNCTIONALITY TEST
# Validates the evolutionary engine before UI integration.
# Run with: python test_core.py
# =============================================================================

from engine import EvolutionaryEngine
from evaluator import Evaluator
from genome import PromptGenome


def run_demo(generations: int = 3, use_mock: bool = True):
    """
    Run a short evolutionary demo to validate core functionality.
    
    Args:
        generations: Number of generations to simulate.
        use_mock: Use mock evaluator for speed.
    """
    print("🧬 Starting Functional Core Demo...")
    print("=" * 60)
    
    # Initialize components
    engine = EvolutionaryEngine(population_size=5)
    evaluator = Evaluator(use_mock=use_mock)
    task = "Explain the concept of recursion in Python"
    
    # Create initial population
    population = engine.create_initial_population()
    
    # Run evolutionary loop
    for gen in range(generations):
        print(f"\n--- Generation {gen} ---")
        
        # Evaluate current population
        scores = []
        for ind in population:
            score = evaluator.evaluate(ind, task)
            scores.append(score)
            print(f"  Agent: {ind} | Fitness: {score:.2f}")
        
        # Alternate modes to test both strategies
        mode = 'darwin' if gen % 2 == 0 else 'kropotkin'
        print(f"  🔄 Mode: {mode.upper()}")
        
        # Evolve to next generation
        population = engine.evolve_generation(population, scores, mode=mode)
        
        # Print Commons status (Kropotkin mode)
        if mode == 'kropotkin':
            stats = engine.get_commons_stats()
            print(f"  📦 Commons: {stats['unique_fragments']} unique fragments")
    
    # Final summary
    print("\n" + "=" * 60)
    print("✅ Functional Core Operational.")
    print(f"📊 Total evaluations: {evaluator.get_stats()['total_evaluations']}")
    print(f"🧬 Final population diversity: {len(set(str(ind) for ind in population))}/{len(population)}")
    
    # Show best individual
    final_scores = [evaluator.evaluate(ind, task) for ind in population]
    best_idx = final_scores.index(max(final_scores))
    print(f"🏆 Best Agent: {population[best_idx]} | Score: {final_scores[best_idx]:.2f}")


def run_quick_test():
    """Minimal test to verify imports and basic functionality."""
    print("🔍 Running Quick Validation...")
    
    # Test genome creation
    genome = PromptGenome()
    prompt = genome.render_prompt("Test task")
    assert "Test task" in prompt, "Prompt rendering failed"
    
    # Test mutation
    original_frags = genome.genes['fragments'].copy()
    genome.mutate(rate=1.0)  # Force mutation
    # (Mutation may or may not change fragments, so we just check it doesn't crash)
    
    # Test evaluator
    evaluator = Evaluator(use_mock=True)
    score = evaluator.evaluate(genome)
    assert 0 <= score <= 10, f"Invalid score: {score}"
    
    print("✅ Quick validation passed.")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        run_quick_test()
    else:
        run_demo()
