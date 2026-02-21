# pool.py
# =============================================================================
# GENE POOL DEFINITIONS
# These are the "alleles" - predefined, valid values that genes can take.
# Using discrete encoding ensures mutations always produce valid prompts.
# Reference: Gridin (2021), Ch. 8 - "Enumeration Encoding"
# =============================================================================

# Predefined instruction fragments for prompt construction
# Each index represents a valid "instruction gene"
INSTRUCTION_POOL = [
    "Be concise and direct",
    "Use practical examples",
    "Think step-by-step (Chain of Thought)",
    "Be empathetic and kind",
    "Prioritize technical precision",
    "Use Markdown formatting",
    "Use JSON formatting",
    "Act as a senior expert",
    "Act as a patient tutor",
    "Provide constructive criticism"
]

# Available agent roles (categorical gene)
ROLES = ["expert", "tutor", "critic", "assistant"]

# Available output formats (categorical gene)
FORMATS = ["markdown", "json", "plain_text", "bullet_points"]

# Available tones (categorical gene)
TONES = ["clinical", "friendly", "formal", "casual"]


def get_instruction_by_index(index: int) -> str:
    """Safely retrieve instruction from pool by index."""
    if 0 <= index < len(INSTRUCTION_POOL):
        return INSTRUCTION_POOL[index]
    return INSTRUCTION_POOL[0]  # Fallback to default
