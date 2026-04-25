import streamlit as st
import datetime
import numpy as np

from pipeline import DataPipeline
from run_aus import set_game_params
from aus_data import load_from_csv, fetch_all_aus_draws, scrape_latest_results
from numerology_lunar import get_chaldean_number, calculate_moon_phase
from aus_pool import build_restricted_pool
from aus_generate_ticket import generate_aus_ticket

import steps.deep_learning as dl
import config.quantum_features as qf

from main import safe_run
from steps.historical import process_historical_data
from steps.frequency import analyze_number_frequency
from steps.decay import calculate_decay_factors
from steps.clustering import kmeans_clustering_and_correlation
from steps.monte_carlo import monte_carlo_simulation
from steps.redundancy import sequential_features
from steps.markov import markov_features
from steps.entropy import shannon_entropy_features

def run_ml_pipeline(game_type):
    pipeline = DataPipeline(game_type=game_type)
    config = pipeline.config
    set_game_params(config['NUM_MAIN'], config['NUM_POWERBALL'], config['NUM_TOTAL'])
    all_draws = fetch_all_aus_draws(game_type)

    pipeline.clear_pipeline()
    pipeline.add_data("historical_data", all_draws)

    if len(all_draws) > 10:
        st.info("Running deep learning and quantum analytical pipeline... This may take a few seconds.")
        safe_run(lambda p: process_historical_data({"past_results": all_draws}, p), pipeline, "Historical Processing")
        safe_run(analyze_number_frequency, pipeline, "Frequency Analysis")
        safe_run(calculate_decay_factors, pipeline, "Decay Calculation")
        try:
            from steps.bayesian_fusion import bayesian_fusion_with_mechanics
            safe_run(bayesian_fusion_with_mechanics, pipeline, "Bayesian Fusion")
        except:
            pipeline.add_data("bayesian_fusion", np.ones(config['NUM_TOTAL']) / config['NUM_TOTAL'])

        safe_run(kmeans_clustering_and_correlation, pipeline, "Clustering")
        safe_run(monte_carlo_simulation, pipeline, "Monte Carlo Simulation")
        safe_run(sequential_features, pipeline, "Sequential/Redundancy")
        safe_run(markov_features, pipeline, "Markov Features")
        safe_run(shannon_entropy_features, pipeline, "Entropy Features")
        safe_run(dl.deep_learning_prediction, pipeline, "Deep Learning Prediction")
    else:
        st.warning("Not enough historical data to run full ML pipeline. Generating probabilities uniformly.")
        pipeline.add_data("deep_learning_predictions", np.ones(config['NUM_TOTAL']) / config['NUM_TOTAL'])

    return pipeline

st.set_page_config(page_title="Aussie Lotto Analytical Dashboard", layout="wide")

# Apple UI/UX Dark Mode Polish
st.markdown('''
<style>
    /* Global Apple Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
    }

    /* Main Container Padding and rounded feel */
    .block-container {
        padding: 3rem 5rem !important;
    }

    /* Streamlit Buttons: Apple Style */
    .stButton > button {
        background-color: #0A84FF !important;
        color: white !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 0.6rem 1.2rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        box-shadow: 0 4px 14px 0 rgba(10, 132, 255, 0.39) !important;
        transition: all 0.2s ease-in-out !important;
    }
    .stButton > button:hover {
        background-color: #007aff !important;
        box-shadow: 0 6px 20px rgba(10, 132, 255, 0.23) !important;
        transform: scale(1.02);
    }

    /* Tickets Output Styling (Cards) */
    .ticket-card {
        background-color: #2c2c2e;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border: 1px solid #3a3a3c;
    }

    .ticket-numbers {
        font-size: 1.4rem;
        font-weight: 700;
        letter-spacing: 2px;
        color: #ffffff;
    }

    .ticket-pb {
        font-size: 1.4rem;
        font-weight: 700;
        color: #ff9f0a; /* Apple Orange */
        margin-left: 10px;
    }

    /* Alerts and Info Boxes */
    div[data-testid="stAlert"] {
        border-radius: 12px;
        border: none;
    }

    /* Tabs styling */
    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
        border-radius: 8px 8px 0 0;
    }
</style>
''', unsafe_allow_html=True)

st.title("Local Australian Lotto Analytical Web App")

st.sidebar.header("Lunar Phasing Module")
today = datetime.datetime.now()
moon_status = calculate_moon_phase(today)

if moon_status == 'FULL_MOON_WINDOW':
    st.sidebar.success("🌕 FULL MOON WINDOW: Geomagnetic Calm. Optimal time to play!")
elif moon_status == 'SKIP_NEW_MOON':
    st.sidebar.error("🌑 NEW MOON: Skip playing today.")
else:
    st.sidebar.info("🌗 NORMAL MOON PHASE")

st.sidebar.markdown(f"**Current Date:** {today.strftime('%Y-%m-%d')}")

st.sidebar.header("Chaldean Numerology")
personal_input = st.sidebar.text_input("Enter Name or Intention:")
chaldean_vibration = 1
if personal_input:
    chaldean_vibration = get_chaldean_number(personal_input)
    st.sidebar.write(f"Your Chaldean Vibration Number: **{chaldean_vibration}**")

tab1, tab2, tab3 = st.tabs(["Saturday Lotto (6/45)", "Oz Lotto (7/47)", "Powerball (7/35 + 1/20)"])

if 'pipeline' not in st.session_state:
    st.session_state.pipeline = None

def render_game_tab(game_name, game_type):
    st.header(game_name)
    count_scraped = scrape_latest_results(game_type)
    if count_scraped > 0:
        st.success(f"Successfully auto-fetched {count_scraped} recent {game_name} draws from the web!")

    uploaded_file = st.file_uploader(f"Upload Historical CSV for {game_name}", type=['csv'], key=f"file_{game_type}")
    if uploaded_file is not None:
        count = load_from_csv(uploaded_file, game_type)
        st.success(f"Loaded {count} draws.")

    st.subheader("Strategy Configuration")
    strategy = st.radio(
        "Select Generation Strategy:",
        ["Standard (Max 12 Games)", "System 8 (Wheel 8 Numbers)"] + (["PowerHit (1 Game, All PBs)"] if game_type == 'powerball' else []),
        key=f"strat_{game_type}"
    )

    if st.button(f"Generate Tickets for {game_name}", key=f"btn_{game_type}"):
        if moon_status == 'SKIP_NEW_MOON':
            st.warning("Warning: Generating tickets on a New Moon is not recommended by the framework.")

        pipeline = run_ml_pipeline(game_type)
        st.session_state.pipeline = pipeline

        pool = build_restricted_pool(pipeline, chaldean_vibration, game_type)
        st.write(f"**Restricted Number Pool (12-18 numbers):** {pool}")

        is_system_8 = "System 8" in strategy
        powerhit = "PowerHit" in strategy
        num_lines = 1 if powerhit else (1 if is_system_8 else 12)

        tickets = generate_aus_ticket(pipeline, game_type, pool, num_lines=num_lines, is_system_8=is_system_8, powerhit=powerhit)

        st.subheader("Your Generated Tickets")
        for i, t in enumerate(tickets):
            line_str = "  ".join([f"{n:02d}" for n in t['line']])
            pb_str = f"<span class='ticket-pb'>| PB: {t['powerball']}</span>" if t['powerball'] is not None else ""
            st.markdown(f"<div class='ticket-card'><span class='ticket-numbers'>Game {i+1}: &nbsp;&nbsp; {line_str}</span> {pb_str}</div>", unsafe_allow_html=True)

with tab1:
    render_game_tab("Saturday Lotto", "saturday")

with tab2:
    render_game_tab("Oz Lotto", "oz")

with tab3:
    render_game_tab("Powerball", "powerball")
