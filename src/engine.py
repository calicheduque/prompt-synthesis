# engine.py
# =============================================================================
# EVOLUTIONARY ENGINE
# Implements the Darwin-Kropotkin synthesis:
# - Darwin mode: Competition, survival of the fittest
# - Kropotkin mode: Cooperation, knowledge sharing via Commons
# Reference: Conceptual framework for self-improving agents
# =============================================================================

import random
from typing import List, Tuple
from genome import PromptGenome


class EvolutionaryEngine:
    """
    Manages the evolutionary process for a population of PromptGenomes.
    
    Supports two evolutionary modes:
    - 'darwin': Competitive selection, high pressure for individual fitness
    - 'kropotkin': Cooperative selection, shared knowledge pool (Commons)
    """
    
    def __init__(self, population_size: int = 5, commons_size: int = 10):
        """
        Initialize the evolutionary engine.
        
        Args:
            population_size: Number of individuals in each generation.
            commons_size: Maximum size of the shared knowledge pool.
        """
        self.population_size = population_size
        self.commons: List[int] = []  # Shared fragment pool (Kropotkin)
        self.commons_max_size = commons_size
        self.generation_count = 0
    
    def create_initial_population(self) -> List[PromptGenome]:
        """Generate the initial random population."""
        return [PromptGenome() for _ in range(self.population_size)]
    
    def _evaluate_population(
        self, 
        population: List[PromptGenome], 
        evaluator, 
        task: str
    ) -> List[float]:
        """Evaluate fitness for all individuals in the population."""
        return [evaluator.evaluate(ind, task) for ind in population]
    
    def select_darwin(
        self, 
        population: List[PromptGenome], 
        scores: List[float],
        survival_rate: float = 0.5
    ) -> List[PromptGenome]:
        """
        Darwinian selection: survival of the fittest.
        
        Args:
            population: Current generation.
            scores: Fitness scores for each individual.
            survival_rate: Fraction of population to keep (default: 50%).
            
        Returns:
            List of surviving individuals.
        """
        # Rank by fitness (highest first)
        ranked = sorted(
            zip(population, scores), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        # Keep top performers
        num_survivors = max(1, int(len(population) * survival_rate))
        survivors = [ind for ind, _ in ranked[:num_survivors]]
        
        return survivors
    
    def select_kropotkin(
        self, 
        population: List[PromptGenome], 
        scores: List[float],
        sharing_probability: float = 0.5
    ) -> List[PromptGenome]:
        """
        Kropotkinian selection: cooperation via shared knowledge.
        
        Args:
            population: Current generation.
            scores: Fitness scores for each individual.
            sharing_probability: Chance an individual adopts from Commons.
            
        Returns:
            List of individuals (all survive, but may adopt shared genes).
        """
        # Step 1: Best individuals contribute to the Commons
        ranked = sorted(
            zip(population, scores), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        if ranked:
            best_genome = ranked[0][0]
            # Add best fragments to shared pool
            self.commons.extend(best_genome.genes['fragments'])
            # Limit commons size to prevent bloat
            if len(self.commons) > self.commons_max_size:
                self.commons = self.commons[-self.commons_max_size:]
        
        # Step 2: All individuals survive, but may adopt from Commons
        survivors = []
        for ind in population:
            if self.commons and random.random() < sharing_probability:
                # Adopt a random fragment from the Commons
                ind.genes['fragments'][0] = random.choice(self.commons)
            survivors.append(ind)
        
        return survivors
    
    def _reproduce(
        self, 
        survivors: List[PromptGenome], 
        mode: str
    ) -> List[PromptGenome]:
        """
        Generate new individuals through crossover and mutation.
        
        Args:
            survivors: Individuals selected for reproduction.
            mode: Evolutionary mode ('darwin' or 'kropotkin').
            
        Returns:
            New population at target size.
        """
        next_generation = survivors.copy()
        
        while len(next_generation) < self.population_size:
            # Select two random parents from survivors
            parent1, parent2 = random.sample(survivors, 2)
            
            # Create child via crossover
            child = parent1.crossover(parent2)
            
            # Apply mutation
            child.mutate()
            
            # Set mode for child
            child.genes['mode'] = mode
            
            next_generation.append(child)
        
        return next_generation
    
    def evolve_generation(
        self, 
        population: List[PromptGenome], 
        scores: List[float], 
        mode: str = 'darwin'
    ) -> List[PromptGenome]:
        """
        Execute one full generation of evolution.
        
        Args:
            population: Current generation.
            scores: Fitness scores.
            mode: 'darwin' or 'kropotkin'.
            
        Returns:
            New generation after selection and reproduction.
        """
        self.generation_count += 1
        
        # Step 1: Selection based on mode
        if mode == 'darwin':
            survivors = self.select_darwin(population, scores)
        else:  # kropotkin
            survivors = self.select_kropotkin(population, scores)
        
        # Step 2: Reproduction to restore population size
        next_generation = self._reproduce(survivors, mode)
        
        return next_generation
    
    def get_commons_stats(self) -> dict:
        """Return statistics about the shared knowledge pool."""
        return {
            'commons_size': len(self.commons),
            'unique_fragments': len(set(self.commons)) if self.commons else 0
        }
