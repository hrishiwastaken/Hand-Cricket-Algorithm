# prediction.py (Compiled Final Version)

from data import Data as d
from random import randint as random, choice as random_choice
import pandas as pd
import traceback

# --- Global Variables ---
difficulty = 2
pattern = []

# --- Data Objects ---
try:
    iComDistro = d(r"datastorecsv\I_ComboDistributive.csv")
    iHeatmap = d(r"datastorecsv\Instance_Heatmap.csv")
    iPattern = d(r"datastorecsv\Instance_Pattern.csv")
    iUCR = d(r"datastorecsv\Instance_UCR.csv")

    pComDistro = d(r"datastorecsv\P_ComboDistributive.csv")
    pHeatmap = d(r"datastorecsv\Permanent_Heatmap.csv")
    pPattern = d(r"datastorecsv\Permanent_Pattern.csv")
    pUCR = d(r"datastorecsv\Permanent_UCR.csv")
except Exception as e:
    print(f"CRITICAL ERROR during data object initialization: {e}")
    traceback.print_exc()
    import sys
    sys.exit(1)


# --- Data Storage and Processing ---

def store_choice(playerInput, comInput, Ball):
    """Processes a round's result, updating all relevant data files."""
    global pattern
    try:
        pInput_int = int(playerInput)
        cInput_int = int(comInput)
        if not (1 <= pInput_int <= 10 and 1 <= cInput_int <= 10):
            return
    except (ValueError, TypeError):
        return

    def heatmap():
        try:
            difference = abs(pInput_int - cInput_int)
            if difference == 0:
                accuracy_update, correct_update, closeby_update = 10, 1, 0
            elif difference == 1:
                accuracy_update, correct_update, closeby_update = 5, 0, 1
            else:
                accuracy_update, correct_update, closeby_update = -difference, 0, 0

            def update_heatmap_entry(data_obj, com_input):
                def get_safe(col):
                    val = data_obj.get_value(com_input, col)
                    return int(val) if pd.notna(val) else 0
                data_obj.update_value(com_input, "Accuracy", get_safe("Accuracy") + accuracy_update)
                data_obj.update_value(com_input, "Predictions", get_safe("Predictions") + 1)
                data_obj.update_value(com_input, "Correct", get_safe("Correct") + correct_update)
                data_obj.update_value(com_input, "Closeby", get_safe("Closeby") + closeby_update)

            update_heatmap_entry(iHeatmap, cInput_int)
            update_heatmap_entry(pHeatmap, cInput_int)
        except Exception as e:
            print(f"ERROR in heatmap update logic: {e}")

    def UCR():
        iUCR.add_row([pInput_int, cInput_int])
        pUCR.add_row([pInput_int, cInput_int])

    def patternLogic():
        nonlocal pInput_int
        global pattern
        def compression(val):
            if 1 <= val <= 3: return 1
            elif 4 <= val <= 5: return 2
            elif 6 <= val <= 7: return 3
            elif 8 <= val <= 10: return 4
            return None

        compressed_val = compression(pInput_int)
        if compressed_val:
            pattern.append(compressed_val)

        if len(pattern) >= 6:
            iPattern.add_row(pattern[:6])
            pPattern.add_row(pattern[:6])
            p_3_element = [round((pattern[0]+pattern[1])/2), round((pattern[2]+pattern[3])/2), round((pattern[4]+pattern[5])/2)]
            lookup_key = ','.join(map(str, p_3_element))
            for data_obj in [iComDistro, pComDistro]:
                rows = data_obj.get_row_numbers(lookup_key)
                if rows:
                    count = int(data_obj.get_value(rows[0], "Count") or 0)
                    data_obj.update_value(rows[0], "Count", count + 1)
            pattern = []

    if difficulty == 2:
        user_col = iUCR.get_column("User")
        if user_col is not None and len(user_col) >= 12:
            iUCR.reset()

    heatmap()
    UCR()
    patternLogic()

# --- Prediction Engine ---

def initialize(inDiff):
    """Sets the global difficulty level for the prediction engine."""
    global difficulty
    try:
        diff_level = int(inDiff)
        if diff_level in [1, 2, 3]:
            difficulty = diff_level
            print(f"Prediction difficulty set to: {difficulty}")
        else:
            difficulty = 2
    except (ValueError, TypeError):
        difficulty = 2


def predict() -> int:
    """Calculates and returns the computer's prediction based on difficulty and historical data."""
    global difficulty

    def get_ucr_history(data_obj):
        """Safely retrieves and cleans the 'User' column from a UCR data object."""
        try:
            col = data_obj.get_column("User")
            if col is None or col.empty: return []
            return [int(x) for x in col if pd.notna(x) and 1 <= int(x) <= 10]
        except (ValueError, TypeError):
            return []

    # --- Prediction Helper Functions (Used by Hard Mode) ---

    def advanced_patterns():
        """Checks for obvious player patterns like repetition, sequences, and alternations."""
        history = get_ucr_history(iUCR)
        if len(history) < 3: return None
        if history[-1] == history[-2] == history[-3]: return history[-1]
        if len(history) >= 4:
            d1, d2, d3 = history[-1]-history[-2], history[-2]-history[-3], history[-3]-history[-4]
            if d1 == d2 == d3 and d1 != 0:
                pred = history[-1] + d1
                if 1 <= pred <= 10: return pred
        if history[-1] == history[-3]: return history[-2]
        return None

    def predict_from_contextual_ucr():
        """Finds times the AI made a similar move and predicts the player's most likely counter-move."""
        com_history = pUCR.get_column("Com")
        if com_history is None or com_history.empty: return None
        last_com_move = com_history.iloc[-1]
        pucr_df = pUCR.data
        if pucr_df is None: return None
        relevant_history = pucr_df[pucr_df['Com'] == last_com_move]
        if not relevant_history.empty:
            player_responses = relevant_history['User']
            if not player_responses.empty:
                return player_responses.mode()[0]
        return None

    def predict_from_best_heatmap_accuracy():
        """Finds the number with the highest historical 'Accuracy' score in the permanent heatmap."""
        pheatmap_df = pHeatmap.data
        if pheatmap_df is None or pheatmap_df.empty: return None
        best_option_row = pheatmap_df.loc[pheatmap_df['Accuracy'].idxmax()]
        return int(best_option_row['No.'])

    # --- Main Prediction Logic ---

    final_prediction = None

    # Difficulty 1: Simple random choice from combined history.
    if difficulty == 1:
        all_history = get_ucr_history(iUCR) + get_ucr_history(pUCR)
        if all_history:
            final_prediction = random_choice(all_history)

    # Difficulty 2: Mix of dynamic UCR and weighted Heatmap.
    elif difficulty == 2:
        if random(1, 2) == 1: # UCR Strategy
            ucr_history = get_ucr_history(pUCR)
            if ucr_history:
                final_prediction = random_choice(ucr_history[-20:])
        else: # Heatmap Strategy
            scores, numbers = pHeatmap.get_column("Accuracy"), pHeatmap.get_column("No.")
            if scores is not None and not scores.empty:
                weights = scores - scores.min() + 1
                weighted_list = []
                for num, weight in zip(numbers, weights):
                    weighted_list.extend([num] * int(weight))
                if weighted_list:
                    final_prediction = random_choice(weighted_list)

    # Difficulty 3: Ensemble (Hybrid) System using a priority of strategies.
    elif difficulty == 3:
        # Priority 1: Check for immediate, obvious patterns.
        pred_obvious = advanced_patterns()
        # Priority 2: Check for the player's learned reaction to the AI's moves.
        pred_context = predict_from_contextual_ucr()
        # Priority 3: Fall back to the statistically best number to play.
        pred_best_bet = predict_from_best_heatmap_accuracy()

        # Decision Logic: Use the highest-priority prediction that is available.
        if pred_obvious is not None:
            print("AI Strategy: Countering Obvious Pattern")
            final_prediction = pred_obvious
        elif pred_context is not None:
            print("AI Strategy: Contextual Prediction")
            final_prediction = pred_context
        else:
            print("AI Strategy: Statistical Best Bet")
            final_prediction = pred_best_bet

    # Fallback to a random number if no prediction was made by any strategy.
    if final_prediction is None or not (1 <= int(final_prediction) <= 10):
        final_prediction = random(1, 10)

    return int(final_prediction)