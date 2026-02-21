# src/ui.py
# =============================================================================
# PROMPT SYNTHESIS - EVOLUTIONARY UI
# Visual interface for Darwin-Kropotkin prompt evolution system.
# Reference: Sheppard (2019), Ch. 1 - "Make it visible and understandable"
# =============================================================================

import streamlit as st
import json
import time
import random
from pathlib import Path

# Import core modules
from src.genome import PromptGenome
from src.engine import EvolutionaryEngine
from src.evaluator import Evaluator
from src.pool import INSTRUCTION_POOL

# Page configuration
st.set_page_config(
    page_title="Prompt Synthesis | Darwin-Kropotkin Evolution",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better visuals
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }
    .darwin-mode {
        background-color: #ffe6e6;
        border-left: 5px solid #ff4444;
    }
    .kropotkin-mode {
        background-color: #e6ffe6;
        border-left: 5px solid #44ff44;
    }
    .evolution-dial {
        font-size: 24px;
        font-weight: bold;
        text-align: center;
        padding: 20px;
        background: linear-gradient(90deg, #ff4444 0%, #ffff44 50%, #44ff44 100%);
        border-radius: 10px;
        color: #000;
    }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# SESSION STATE INITIALIZATION
# =============================================================================

def init_session_state():
    """Initialize Streamlit session state for persistence across reruns."""
    if 'engine' not in st.session_state:
        st.session_state.engine = EvolutionaryEngine(population_size=5)
    if 'population' not in st.session_state:
        st.session_state.population = st.session_state.engine.create_initial_population()
    if 'evaluator' not in st.session_state:
        st.session_state.evaluator = Evaluator(use_mock=True)
    if 'generation' not in st.session_state:
        st.session_state.generation = 0
    if 'fitness_history' not in st.session_state:
        st.session_state.fitness_history = []
    if 'diversity_history' not in st.session_state:
        st.session_state.diversity_history = []
    if 'mode_history' not in st.session_state:
        st.session_state.mode_history = []
    if 'is_running' not in st.session_state:
        st.session_state.is_running = False
    if 'use_fallback' not in st.session_state:
        st.session_state.use_fallback = False


# =============================================================================
# FALLBACK DATA LOADER
# =============================================================================

def load_fallback_data():
    """Load pre-computed demo data for safe presentation."""
    fallback_path = Path("data/fallback.json")
    if fallback_path.exists():
        with open(fallback_path, 'r') as f:
            return json.load(f)
    return None


def save_fallback_data():
    """Save current state for future demo fallback."""
    fallback_path = Path("data/fallback.json")
    fallback_path.parent.mkdir(exist_ok=True)
    
    data = {
        'generation': st.session_state.generation,
        'fitness_history': st.session_state.fitness_history,
        'diversity_history': st.session_state.diversity_history,
        'mode_history': st.session_state.mode_history,
        'population': [ind.genes for ind in st.session_state.population],
        'commons': st.session_state.engine.commons
    }
    
    with open(fallback_path, 'w') as f:
        json.dump(data, f, indent=2)


# =============================================================================
# VISUAL COMPONENTS
# =============================================================================

def render_evolution_dial(current_mode: str, balance: int):
    """
    Render the Darwin-Kropotkin balance dial.
    Reference: Visual feedback for evolutionary strategy (Gridin, 2021, Ch. 7)
    """
    st.markdown("### 🧭 Evolutionary Strategy Dial")
    
    # Dial visualization
    dial_col1, dial_col2, dial_col3 = st.columns([1, 2, 1])
    
    with dial_col1:
        st.markdown("#### 🧬 Darwin")
        st.markdown("*Competition*")
        if current_mode == 'darwin':
            st.success("● ACTIVE")
    
    with dial_col2:
        # Progress bar as dial
        st.progress(balance / 100)
        st.markdown(f"**Balance: {balance}% Cooperation**")
    
    with dial_col3:
        st.markdown("#### 🤝 Kropotkin")
        st.markdown("*Cooperation*")
        if current_mode == 'kropotkin':
            st.success("● ACTIVE")
    
    # Explanation
    st.caption(
        "🔍 **Why this matters:** Darwin mode explores diversity. "
        "Kropotkin mode consolidates knowledge. The system alternates based on need."
    )


def render_metrics():
    """Display real-time evolutionary metrics."""
    st.markdown("### 📊 Evolutionary Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Calculate current metrics
    if st.session_state.fitness_history:
        avg_fitness = sum(st.session_state.fitness_history[-5:]) / len(st.session_state.fitness_history[-5:])
        max_fitness = max(st.session_state.fitness_history)
    else:
        avg_fitness = 0
        max_fitness = 0
    
    # Calculate diversity
    all_frags = []
    for ind in st.session_state.population:
        all_frags.extend(ind.genes['fragments'])
    diversity = len(set(all_frags))
    
    # Commons size
    commons_size = len(set(st.session_state.engine.commons))
    
    with col1:
        st.metric(
            label="📈 Avg Fitness (last 5 gen)",
            value=f"{avg_fitness:.2f}",
            delta=f"{max_fitness - avg_fitness:.2f}" if st.session_state.fitness_history else None
        )
    
    with col2:
        st.metric(
            label="🏆 Best Fitness",
            value=f"{max_fitness:.2f}",
            delta=None
        )
    
    with col3:
        st.metric(
            label="🧬 Genetic Diversity",
            value=f"{diversity} unique fragments",
            delta=None
        )
    
    with col4:
        st.metric(
            label="📦 Commons Size",
            value=f"{commons_size} shared",
            delta=None
        )


def render_fitness_chart():
    """Display fitness evolution over generations."""
    st.markdown("### 📈 Fitness Evolution Over Time")
    
    if st.session_state.fitness_history:
        # Create chart data
        chart_data = {
            'Generation': list(range(len(st.session_state.fitness_history))),
            'Avg Fitness': st.session_state.fitness_history
        }
        
        st.line_chart(
            chart_data,
            x='Generation',
            y='Avg Fitness'
        )
        
        # Add mode markers
        st.caption("🔴 Red phases = Darwin mode | 🟢 Green phases = Kropotkin mode")
    else:
        st.info("Run evolution to see fitness chart")


def render_population_table():
    """Display current population with details."""
    st.markdown("### 👥 Current Population")
    
    if not st.session_state.population:
        st.warning("No population yet. Start evolution!")
        return
    
    # Create table data
    population_data = []
    for i, ind in enumerate(st.session_state.population):
        # Get instruction texts from indices
        instructions = [INSTRUCTION_POOL[idx] for idx in ind.genes['fragments']]
        
        population_data.append({
            'Agent': f"#{i+1}",
            'Mode': '🧬 Darwin' if ind.genes['mode'] == 'darwin' else '🤝 Kropotkin',
            'Temperature': f"{ind.genes['temperature']:.2f}",
            'Fragments': f"{ind.genes['fragments']}",
            'Instructions': ", ".join(instructions[:2]) + "..."  # Truncate for display
        })
    
    st.dataframe(population_data, use_container_width=True)


def render_mode_explanation():
    """Explain the current evolutionary mode."""
    st.markdown("### 📖 How It Works")
    
    # Get current mode from last generation
    current_mode = st.session_state.mode_history[-1] if st.session_state.mode_history else 'darwin'
    
    if current_mode == 'darwin':
        st.markdown("""
        **🧬 Darwin Mode (Competition)**
        
        - ✅ **Purpose:** Explore diversity, discover new strategies
        - ✅ **Mechanism:** Survival of the fittest, eliminate weak agents
        - ✅ **When:** Early generations or when stuck in local optimum
        - ⚠️ **Risk:** Can lose diversity too quickly
        
        *Reference: Sheppard (2019), Ch. 2 - Selection Pressure*
        """)
    else:
        st.markdown("""
        **🤝 Kropotkin Mode (Cooperation)**
        
        - ✅ **Purpose:** Consolidate knowledge, share successful traits
        - ✅ **Mechanism:** Commons pool, all agents benefit from best fragments
        - ✅ **When:** When fitness plateaus or diversity is low
        - ⚠️ **Risk:** Can converge too quickly to suboptimal solution
        
        *Reference: Kar & Ralte (2025), Ch. 12 - Cooperative Evolution*
        """)


# =============================================================================
# MAIN UI LAYOUT
# =============================================================================

def main():
    """Main UI entry point."""
    
    # Initialize session state
    init_session_state()
    
    # Header
    st.title("🧬🤝 Prompt Synthesis")
    st.markdown("**Self-Improving AI Agents using Darwin-Kropotkin Evolutionary Synthesis**")
    st.markdown("*Hackathon NYC 2025 | Self-Improving Agents Track*")
    
    # Sidebar controls
    st.sidebar.header("⚙️ Controls")
    
    # Fallback mode toggle
    use_fallback = st.sidebar.checkbox(
        "📦 Use Fallback Data (Demo Mode)",
        value=st.session_state.use_fallback
    )
    st.session_state.use_fallback = use_fallback
    
    if use_fallback:
        fallback_data = load_fallback_data()
        if fallback_data:
            st.sidebar.success("✅ Fallback data loaded")
            # Load fallback into session state
            st.session_state.fitness_history = fallback_data.get('fitness_history', [])
            st.session_state.diversity_history = fallback_data.get('diversity_history', [])
            st.session_state.mode_history = fallback_data.get('mode_history', [])
            st.session_state.generation = fallback_data.get('generation', 0)
        else:
            st.sidebar.warning("⚠️ No fallback data found")
    
    # Task selection
    task = st.sidebar.selectbox(
        "📝 Evaluation Task",
        [
            "Explain Python recursion",
            "Write a sorting function",
            "Debug this code snippet",
            "Optimize this algorithm"
        ]
    )
    
    # Evolution controls
    st.sidebar.header("🚀 Evolution Controls")
    
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button("▶️ Run 1 Generation", use_container_width=True):
            # Evaluate current population
            scores = [
                st.session_state.evaluator.evaluate(ind, task)
                for ind in st.session_state.population
            ]
            
            # Determine mode based on diversity (simple heuristic)
            all_frags = []
            for ind in st.session_state.population:
                all_frags.extend(ind.genes['fragments'])
            diversity = len(set(all_frags))
            
            # Switch mode based on diversity
            if diversity < 5:
                mode = 'kropotkin'  # Low diversity → cooperate
            else:
                mode = 'darwin'  # High diversity → compete
            
            # Evolve
            st.session_state.population = st.session_state.engine.evolve_generation(
                st.session_state.population,
                scores,
                mode=mode
            )
            
            # Update histories
            st.session_state.generation += 1
            st.session_state.fitness_history.append(sum(scores) / len(scores))
            st.session_state.diversity_history.append(diversity)
            st.session_state.mode_history.append(mode)
            
            st.rerun()
    
    with col2:
        if st.button("🔄 Reset Population", use_container_width=True):
            st.session_state.engine = EvolutionaryEngine(population_size=5)
            st.session_state.population = st.session_state.engine.create_initial_population()
            st.session_state.generation = 0
            st.session_state.fitness_history = []
            st.session_state.diversity_history = []
            st.session_state.mode_history = []
            st.rerun()
    
    # Auto-run toggle
    auto_run = st.sidebar.checkbox("⏱️ Auto-Run (5 sec/generation)")
    
    if auto_run and not st.session_state.is_running:
        st.session_state.is_running = True
        # Note: Auto-run requires additional Streamlit configuration
    
    # Save fallback button
    if st.sidebar.button("💾 Save Current State as Fallback"):
        save_fallback_data()
        st.sidebar.success("✅ State saved!")
    
    # Main content area
    st.divider()
    
    # Row 1: Evolution Dial + Metrics
    col1, col2 = st.columns([1, 2])
    
    with col1:
        current_mode = st.session_state.mode_history[-1] if st.session_state.mode_history else 'darwin'
        balance = 80 if current_mode == 'kropotkin' else 20
        render_evolution_dial(current_mode, balance)
    
    with col2:
        render_metrics()
    
    st.divider()
    
    # Row 2: Charts + Population
    col1, col2 = st.columns([2, 1])
    
    with col1:
        render_fitness_chart()
    
    with col2:
        render_mode_explanation()
    
    st.divider()
    
    # Row 3: Population Details
    render_population_table()
    
    # Footer
    st.divider()
    st.markdown("""
    
    **🔗 GitHub:** [github.com/your-username/prompt-synthesis](https://github.com)
    """)


if __name__ == "__main__":
    main()
