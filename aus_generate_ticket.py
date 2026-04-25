import numpy as np
from aus_data import fetch_all_aus_draws

def count_even_odd(numbers):
    evens = sum(1 for n in numbers if n % 2 == 0)
    odds = len(numbers) - evens
    return evens, odds

def has_more_than_three_consecutive(numbers):
    sorted_nums = sorted(numbers)
    consecutive_count = 1
    max_consecutive = 1
    for i in range(1, len(sorted_nums)):
        if sorted_nums[i] == sorted_nums[i-1] + 1:
            consecutive_count += 1
            if consecutive_count > max_consecutive:
                max_consecutive = consecutive_count
        else:
            consecutive_count = 1
    return max_consecutive > 3

def is_valid_combination(line, historical_lines, num_pick):
    evens, odds = count_even_odd(line)
    if evens == 0 or odds == 0:
        return False

    if num_pick == 6:
        if evens < 2 or odds < 2:
            return False
    elif num_pick == 7:
        if evens < 2 or odds < 2:
            return False

    if has_more_than_three_consecutive(line):
        return False

    line_set = set(line)
    for hist_line in historical_lines:
        if line_set == set(hist_line):
            return False

    return True

def generate_aus_ticket(pipeline, game_type, restricted_pool, num_lines=12, is_system_8=False, powerhit=False):
    config = pipeline.config
    num_pick = config['NUM_PICK']
    num_pb = config['NUM_POWERBALL']

    draw_pick_size = 8 if is_system_8 else num_pick

    if powerhit:
        num_lines = 1
        draw_pick_size = num_pick

    hist_draws = fetch_all_aus_draws(game_type)
    historical_lines = [draw['numbers'] for draw in hist_draws]

    dl_predictions = pipeline.get_data("deep_learning_predictions")
    if dl_predictions is None:
        dl_predictions = np.ones(config['NUM_TOTAL']) / config['NUM_TOTAL']

    pool_probs = []
    for num in restricted_pool:
        pool_probs.append(dl_predictions[num - 1])

    pool_probs = np.array(pool_probs)
    pool_probs_sum = pool_probs.sum()
    if pool_probs_sum > 0:
        pool_probs = pool_probs / pool_probs_sum
    else:
        pool_probs = np.ones(len(restricted_pool)) / len(restricted_pool)

    pb_probs = None
    if num_pb > 0:
        pb_probs = dl_predictions[config['NUM_MAIN'] : config['NUM_MAIN'] + num_pb]
        pb_sum = pb_probs.sum()
        if pb_sum > 0:
            pb_probs = pb_probs / pb_sum
        else:
            pb_probs = np.ones(num_pb) / num_pb

    ticket = []
    for _ in range(num_lines):
        attempts = 0
        while attempts < 1000:
            attempts += 1
            cand_main = sorted(np.random.choice(restricted_pool, size=draw_pick_size, replace=False, p=pool_probs))

            if is_valid_combination(cand_main, historical_lines, draw_pick_size):
                max_overlap = 3 if draw_pick_size == 6 else 4
                overlap_failed = False
                for existing_line in ticket:
                    if len(set(cand_main) & set(existing_line['line'])) > max_overlap:
                        overlap_failed = True
                        break

                if not overlap_failed:
                    cand_pb = None
                    if num_pb > 0:
                        if powerhit:
                            cand_pb = "PowerHit (All 1-20)"
                        else:
                            cand_pb = int(np.random.choice(np.arange(1, num_pb + 1), p=pb_probs))

                    ticket.append({
                        "line": cand_main,
                        "powerball": cand_pb
                    })
                    break

        if attempts >= 1000 and len(ticket) <= _:
            cand_main = sorted(np.random.choice(restricted_pool, size=draw_pick_size, replace=False))
            cand_pb = None
            if num_pb > 0:
                cand_pb = "PowerHit" if powerhit else int(np.random.choice(np.arange(1, num_pb + 1)))
            ticket.append({
                "line": cand_main,
                "powerball": cand_pb
            })

    return ticket
