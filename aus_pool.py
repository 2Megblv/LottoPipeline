import numpy as np

def build_restricted_pool(pipeline, chaldean_num, game_type):
    """
    Builds the strategic 12-18 number restricted probability pool.
    - 3 "Hot" numbers (highest probability)
    - 3 "Cold" numbers (lowest probability)
    - 3 Personal Numerology numbers (based on chaldean_num)
    - 3 Daily numerical stream numbers (pseudo-randomly selected based on current day)
    """
    dl_predictions = pipeline.get_data("deep_learning_predictions")
    config = pipeline.config
    num_main = config['NUM_MAIN']

    if dl_predictions is None or len(dl_predictions) < num_main:
        dl_predictions = np.ones(num_main) / num_main

    main_probs = dl_predictions[:num_main]

    sorted_indices = np.argsort(main_probs)[::-1]

    hot_numbers = (sorted_indices[:3] + 1).tolist()
    cold_numbers = (sorted_indices[-3:] + 1).tolist()

    chaldean_numbers = []
    base_c = chaldean_num
    while len(chaldean_numbers) < 3 and base_c <= num_main:
        chaldean_numbers.append(base_c)
        base_c += 9

    if len(chaldean_numbers) < 3:
        chaldean_numbers.extend([1, 2, 3][:3-len(chaldean_numbers)])

    import datetime
    today_day = datetime.datetime.now().day
    np.random.seed(today_day)
    daily_numbers = np.random.choice(np.arange(1, num_main + 1), size=3, replace=False).tolist()
    np.random.seed(None)

    pool_set = set(hot_numbers + cold_numbers + chaldean_numbers + daily_numbers)

    idx_hot = 3
    idx_cold = 4
    while len(pool_set) < 12:
        pool_set.add(int(sorted_indices[idx_hot] + 1))
        pool_set.add(int(sorted_indices[-idx_cold] + 1))
        idx_hot += 1
        idx_cold += 1

    pool_list = sorted(list(pool_set))
    return pool_list
