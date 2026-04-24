# Modified By: Callam
# Project: Lotto Generator
# Purpose: Core Data Pipeline and Dynamic Parameter Management

import os
import logging
from typing import Any, Dict, Tuple, List
import numpy as np

MIN_PROB = 1e-12

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

def get_dynamic_params(num_draws: int) -> Tuple[int, int]:
    dynamic_epochs = min(50 + (num_draws // 100), 100)
    return None, dynamic_epochs

class DataPipeline:
    def __init__(self, game_type="nz_lotto") -> None:
        self.data: Dict[str, Any] = {}
        configs = {
            'saturday': {'NUM_MAIN': 45, 'NUM_POWERBALL': 0, 'NUM_PICK': 6, 'NUM_TOTAL': 45},
            'oz': {'NUM_MAIN': 47, 'NUM_POWERBALL': 0, 'NUM_PICK': 7, 'NUM_TOTAL': 47},
            'powerball': {'NUM_MAIN': 35, 'NUM_POWERBALL': 20, 'NUM_PICK': 7, 'NUM_TOTAL': 55},
            'nz_lotto': {'NUM_MAIN': 40, 'NUM_POWERBALL': 10, 'NUM_PICK': 6, 'NUM_TOTAL': 50}
        }
        self.config = configs.get(game_type, configs['nz_lotto'])
        self.game_type = game_type
        logging.info(f"Initialized DataPipeline for {game_type}.")

    def add_data(self, key: str, value: Any) -> None:
        self.data[key] = value

    def get_data(self, key: str) -> Any:
        return self.data.get(key)

    def clear_pipeline(self) -> None:
        self.data.clear()

def hit_rate_analysis(
    tickets: List[Dict[str, Any]],
    historical_data: List[Dict[str, Any]]
) -> Tuple[int, Dict[int, int]]:
    exact_matches = 0
    partial_matches = {4: 0, 5: 0, 6: 0}

    if not tickets or not historical_data:
        return exact_matches, partial_matches

    for draw in historical_data:
        draw_main = set(draw.get("numbers", []))
        draw_powerball = draw.get("powerball")

        for ticket in tickets:
            ticket_main = set(ticket["line"])
            ticket_powerball = ticket["powerball"]

            matches = len(ticket_main & draw_main)

            if matches >= 4:
                partial_matches[matches] += 1

            if matches == 6 and ticket_powerball == draw_powerball:
                exact_matches += 1

    return exact_matches, partial_matches
