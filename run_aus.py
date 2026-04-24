import steps.frequency as freq
import steps.decay as decay
import steps.clustering as cluster
import steps.bayesian_fusion as bayes
import steps.monte_carlo as mc
import steps.redundancy as red
import steps.markov as markov
import steps.entropy as ent
import steps.deep_learning as dl
import config.quantum_features as qf

def set_game_params(num_main, num_powerball, num_total):
    modules = [freq, decay, cluster, bayes, mc, red, markov, ent, dl]
    for mod in modules:
        if hasattr(mod, 'NUM_MAIN'):
            mod.NUM_MAIN = num_main
        if hasattr(mod, 'NUM_MAIN_NUMBERS'):
            mod.NUM_MAIN_NUMBERS = num_main
        if hasattr(mod, 'NUM_POWERBALL'):
            mod.NUM_POWERBALL = num_powerball
        if hasattr(mod, 'NUM_POWERBALLS'):
            mod.NUM_POWERBALLS = num_powerball
        if hasattr(mod, 'NUM_POWERBALL_NUMBERS'):
            mod.NUM_POWERBALL_NUMBERS = num_powerball
        if hasattr(mod, 'NUM_TOTAL'):
            mod.NUM_TOTAL = num_total
        if hasattr(mod, 'TOTAL_NUMBERS'):
            mod.TOTAL_NUMBERS = num_total
        if hasattr(mod, 'TOTAL_NUM'):
            mod.TOTAL_NUM = num_total
        if hasattr(mod, 'NUM_TOTAL_NUMBERS'):
            mod.NUM_TOTAL_NUMBERS = num_total

    if hasattr(qf, 'NUM_QUBITS'):
        qf.NUM_QUBITS = min(num_total, qf.NUM_QUBITS)

    if hasattr(qf, '_quantum_predictor'):
        import tensorflow.keras as keras
        qf._quantum_predictor = keras.Sequential([
            keras.layers.Input(shape=(qf.QUANTUM_FEATURE_LEN,)),
            keras.layers.Dense(128, activation="relu"),
            keras.layers.Dense(64, activation="relu"),
            keras.layers.Dense(num_total, activation="sigmoid"),
        ])
        qf._quantum_predictor.compile(
            optimizer=keras.optimizers.Adam(learning_rate=1e-3),
            loss=keras.losses.BinaryCrossentropy(),
            metrics=[
                keras.metrics.BinaryAccuracy(name="binary_accuracy"),
                keras.metrics.AUC(name="auc", multi_label=True, num_labels=num_total),
                keras.metrics.MeanAbsoluteError(name="mae"),
            ],
        )
