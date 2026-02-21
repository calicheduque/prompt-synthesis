# genome.py
# =============================================================================
# PROMPT GENOME CLASS
# Represents an individual in the evolutionary population.
# Separates Genotype (data structure) from Phenotype (executable prompt).
# Reference: Gridin (2021), Ch. 8; Kar & Ralte (2025), Ch. 12
# =============================================================================

import random
from typing import List, Dict, Any
from pool import INSTRUCTION_POOL, ROLES, FORMATS, TONES


class PromptGenome:
    """
    Represents a configurable agent as an evolvable genome.
    
    Genotype (internal representation):
    - fragments: List[int] - indices into INSTRUCTION_POOL
    - temperature: float - LLM temperature parameter (0.0 to 1.0)
    - mode: str - 'darwin' or 'kropotkin' (evolutionary strategy)
    
    Phenotype (external representation):
    - render_prompt() -> str: The actual prompt sent to the LLM
    """
    
    def __init__(self, genes: Dict[str, Any] = None):
        """
        Initialize a genome with given genes or generate random ones.
        
        Args:
            genes: Optional dict with pre-defined gene values.
        """
        if genes:
            self.genes = genes
        else:
            # Random initialization for initial population
            self.genes = self._generate_random_genes()
    
    def _generate_random_genes(self) -> Dict[str, Any]:
        """Generate a valid random genome for population initialization."""
        return {
            'fragments': random.sample(
                range(len(INSTRUCTION_POOL)), 
                k=min(3, len(INSTRUCTION_POOL))
            ),
            'temperature': random.uniform(0.3, 0.9),
            'mode': random.choice(['darwin', 'kropotkin'])
        }
    
    def render_prompt(self, task: str) -> str:
        """
        Convert genotype to phenotype: render executable prompt.
        
        Args:
            task: The specific task/question for the agent.
            
        Returns:
            str: The complete prompt to send to the LLM.
        """
        # Translate fragment indices to actual instructions
        instructions = " ".join([
            INSTRUCTION_POOL[i] for i in self.genes['fragments']
        ])
        
        # Construct final prompt
        return (
            f"{instructions}. "
            f"Task: {task}. "
            f"Temperature: {self.genes['temperature']:.2f}"
        )
    
    def mutate(self, rate: float = 0.2) -> None:
        """
        Apply mutation operators based on gene type.
        Reference: Gridin (2021), Ch. 5 - Mutation Methods
        
        Args:
            rate: Probability of mutation occurring (default: 20%).
        """
        if random.random() > rate:
            return  # No mutation this generation
        
        # Mutation Type 1: Discrete (fragment indices)
        if random.random() < 0.5 and self.genes['fragments']:
            idx = random.randint(0, len(self.genes['fragments']) - 1)
            self.genes['fragments'][idx] = random.randint(
                0, len(INSTRUCTION_POOL) - 1
            )
        
        # Mutation Type 2: Real-valued (temperature)
        else:
            noise = random.gauss(0, 0.1)  # Gaussian deviation
            new_temp = self.genes['temperature'] + noise
            # Clamp to valid range [0.0, 1.0]
            self.genes['temperature'] = max(0.0, min(1.0, new_temp))
    
    def crossover(self, partner: 'PromptGenome') -> 'PromptGenome':
        """
        Perform single-point crossover with another genome.
        Reference: Gridin (2021), Ch. 4 - Crossover Methods
        
        Args:
            partner: The other parent genome.
            
        Returns:
            PromptGenome: A new child genome with mixed genes.
        """
        # Crossover for fragment list (take first half from self, rest from partner)
        mid_point = len(self.genes['fragments']) // 2
        child_fragments = (
            self.genes['fragments'][:mid_point] + 
            partner.genes['fragments'][mid_point:]
        )
        
        # Blend crossover for temperature (average of parents)
        child_temp = (
            self.genes['temperature'] + partner.genes['temperature']
        ) / 2
        
        # Create child genome
        return PromptGenome({
            'fragments': child_fragments,
            'temperature': child_temp,
            'mode': self.genes['mode']  # Inherit mode from first parent
        })
    
    def get_fitness_key(self) -> str:
        """Generate a hashable key for caching fitness evaluations."""
        return f"{sorted(self.genes['fragments'])}_{self.genes['temperature']:.2f}"
    
    def __str__(self) -> str:
        """Human-readable representation for debugging/logging."""
        return (
            f"Mode:{self.genes['mode']} | "
            f"Temp:{self.genes['temperature']:.2f} | "
            f"Frags:{self.genes['fragments']}"
        )
    
    def __repr__(self) -> str:
        return f"PromptGenome(mode={self.genes['mode']}, temp={self.genes['temperature']:.2f})"
