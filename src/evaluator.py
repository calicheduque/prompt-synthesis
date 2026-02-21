# evaluator.py
# =============================================================================
# FITNESS EVALUATOR
# Measures how well a genome solves the given task.
# Supports both mock evaluation (for development) and real LLM evaluation.
# Reference: Sheppard (2019), Ch. 2 - Fitness Function Design
# =============================================================================

import random
import time
from typing import Optional
from genome import PromptGenome

# Optional: Import Gemini for real evaluation
# import google.generativeai as genai


class Evaluator:
    """
    Evaluates the fitness of PromptGenome individuals.
    
    Fitness Score: Float between 0.0 (worst) and 10.0 (best).
    """
    
    def __init__(self, use_mock: bool = True, api_key: Optional[str] = None):
        """
        Initialize the evaluator.
        
        Args:
            use_mock: If True, use simulated scores (faster for development).
            api_key: Gemini API key for real evaluation (if use_mock=False).
        """
        self.use_mock = use_mock
        self.api_key = api_key
        self.eval_count = 0  # Track number of evaluations for debugging
        
        # Optional: Configure Gemini if using real evaluation
        # if not use_mock and api_key:
        #     genai.configure(api_key=api_key)
    
    def evaluate(self, genome: PromptGenome, task: str = "Explain Python") -> float:
        """
        Evaluate a genome's fitness for a given task.
        
        Args:
            genome: The PromptGenome to evaluate.
            task: The task/question to assess.
            
        Returns:
            float: Fitness score (0.0 to 10.0).
        """
        self.eval_count += 1
        
        if self.use_mock:
            return self._mock_evaluate(genome, task)
        else:
            return self._real_evaluate(genome, task)
    
    def _mock_evaluate(self, genome: PromptGenome, task: str) -> float:
        """
        Simulated evaluation for development/testing.
        Produces plausible scores without API calls.
        """
        # Base score with some randomness
        base_score = random.uniform(5.0, 8.0)
        
        # Bonus for "reasonable" temperature (exploration vs exploitation balance)
        temp = genome.genes['temperature']
        if 0.5 < temp < 0.8:
            base_score += 1.0
        
        # Bonus for having diverse fragments (exploration)
        if len(set(genome.genes['fragments'])) >= 2:
            base_score += 0.5
        
        # Clamp to valid range
        return min(10.0, max(0.0, base_score))
    
    def _real_evaluate(self, genome: PromptGenome, task: str) -> float:
        """
        Real evaluation using Gemini API.
        Note: Implement this when ready for production testing.
        """
        # TODO: Implement real LLM-based evaluation
        # 1. Render the prompt from genome
        # 2. Send to Gemini with the task
        # 3. Ask Gemini to score the response 1-10
        # 4. Return the score
        
        # Placeholder for now
        time.sleep(0.1)  # Simulate API latency
        return 5.0
    
    def get_stats(self) -> dict:
        """Return evaluation statistics for debugging."""
        return {
            'total_evaluations': self.eval_count,
            'mode': 'mock' if self.use_mock else 'real'
        }
