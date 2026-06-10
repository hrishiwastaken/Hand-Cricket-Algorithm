import prediction
import data 
import random
import time
import sys

# Setting up a placeholder object to call reset function.
reset = data.Data(r"datastorecsv\I_ComboDistributive.csv")
# --- Constants ---
MIN_INPUT = 1
MAX_INPUT = 10

# --- Helper Functions (exit_game, get_validated_input, calculate_next_over) ---
def exit_game(message='\nExiting Game...'):
    """Prints an exit message and terminates the script."""
    reset.reset()
    print(message)
    time.sleep(1)
    sys.exit()

def get_validated_input(prompt, type_cast=int, check_range=False, min_val=0, max_val=0, options=None, allow_empty=False):
    """
    Gets input from the user, validates it, and handles 'exit'.
    (Modified to potentially allow empty input for specific cases if needed, though not used here currently)
    """
    while True:
        user_input = input(prompt).strip()
        if user_input.lower() == 'exit':
            exit_game()
        if allow_empty and user_input == "":
             return None # Return None if empty input is allowed and given

        try:
            value = type_cast(user_input)
            if options and value not in options:
                print(f"\nInvalid choice. Please enter one of {options}.")
            elif check_range and not (min_val <= value <= max_val):
                print(f"\nInvalid input. Please enter a number between {min_val} and {max_val}.")
            else:
                return value
        except ValueError:
            print(f"\nInvalid input. Please enter a valid {type_cast.__name__}.")
        except TypeError: # Handle case where type_cast fails on empty string if not allowed
             print(f"\nInvalid input. Please enter a valid {type_cast.__name__}.")


def calculate_next_over(current_over):
    """ Calculates the next over value correctly. """
    # Using round for comparison robustness
    if abs((current_over + 0.1) % 1.0 - 0.6) < 0.01:
        return float(int(current_over) + 1)
    else:
        # Ensure rounding to one decimal place after addition
        return round(current_over + 0.1, 1)

# --- Game Setup (game_setup) ---
def game_setup():
    """Handles the initial game configuration with navigation and toss on confirmation."""

    print("*" * 40)
    print(" Welcome to Hand Cricket Premium Edition!")
    print("          (ALPHA v2.0 - Setup)")
    print("*" * 40)
    input("Press Enter Key to Continue...\n(Type 'exit' at any prompt to exit the game)\n")

    # --- Store settings temporarily ---
    settings = {
        'gamemode': None, # 1: Legacy, 2: Custom
        'overs': None,
        'wickets': None, # Automatically set based on gamemode or custom input
        'difficulty': None, # 1: Easy, 2: Medium, 3: Hard
        'player_bats_first': None # Set only during confirmation/toss
    }
    gamemode_map = {1: "Legacy (1 Wicket)", 2: "Custom"}
    difficulty_map = {1: "Easy", 2: "Medium", 3: "Hard"}

    while True: # Main setup loop
        print("\n" + "=" * 15 + " Current Settings " + "=" * 15)
        # --- Display Current Settings ---
        gm_display = gamemode_map.get(settings['gamemode'], "Not Set")
        if settings['gamemode'] == 2 and settings['wickets'] is not None:
            gm_display += f" ({settings['wickets']} Wickets)"
        elif settings['gamemode'] == 1:
             settings['wickets'] = 1 # Ensure correct wicket count

        print(f" 1. Gamemode : {gm_display}")
        print(f" 2. Overs    : {settings['overs'] if settings['overs'] is not None else 'Not Set'}")
        print(f" 3. Difficulty: {difficulty_map.get(settings['difficulty'], 'Not Set')}")
        print("=" * 48)

        # --- Present Menu ---
        print("\nSetup Options:")
        print(" [1] Configure Gamemode, Wickets, and Overs")
        print(" [2] Select Difficulty")
        print(" [3] Confirm Settings, Conduct Toss, and Start Game")
        print(" [4] Exit Setup")

        choice = get_validated_input("Choose an option (1-4): ", options={1, 2, 3, 4})

        # --- Handle Menu Choice ---
        if choice == 1:
            print("\n--- Configure Gamemode ---")
            selected_gamemode = get_validated_input(
                "Select Gamemode:\n  1. Legacy (Single Wicket)\n  2. Custom (Multiple Wickets)\nEnter choice (1 or 2): ",
                options={1, 2}
            )
            settings['gamemode'] = selected_gamemode

            if selected_gamemode == 1:
                settings['wickets'] = 1
                print("   Legacy mode selected (1 wicket).")
                selected_overs = get_validated_input("Enter the number of overs (1-100): ", check_range=True, min_val=1, max_val=100)
                settings['overs'] = selected_overs
                print(f"   Number of overs set to: {selected_overs}")
            else: # Custom Mode
                selected_wickets = get_validated_input("Enter the number of wickets (1-10): ", check_range=True, min_val=1, max_val=10)
                settings['wickets'] = selected_wickets
                print(f"   Number of wickets set to: {selected_wickets}")
                selected_overs = get_validated_input("Enter the number of overs (1-100): ", check_range=True, min_val=1, max_val=100)
                settings['overs'] = selected_overs
                print(f"   Number of overs set to: {selected_overs}")
            time.sleep(1)

        elif choice == 2:
            print("\n--- Select Difficulty ---")
            selected_difficulty = get_validated_input(
                "Select Difficulty:\n  1. Easy\n  2. Medium\n  3. Hard\nEnter choice (1-3): ",
                options={1, 2, 3}
            )
            settings['difficulty'] = selected_difficulty
            print(f"   Difficulty set to: {difficulty_map[selected_difficulty]}")
            time.sleep(1)

        elif choice == 3:
            print("\n--- Confirming Settings & Conducting Toss ---")

            # --- Validation Check ---
            all_pre_toss_set = True
            missing = []
            if settings['gamemode'] is None: missing.append("Gamemode"); all_pre_toss_set = False
            if settings['overs'] is None: missing.append("Overs"); all_pre_toss_set = False
            if settings['gamemode'] is not None and settings['wickets'] is None: missing.append("Wickets"); all_pre_toss_set = False
            if settings['difficulty'] is None: missing.append("Difficulty"); all_pre_toss_set = False

            if all_pre_toss_set:
                print("\n--- Toss Time! ---")
                toss_choice = get_validated_input("Choose Odd or Even (1=Odd, 2=Even): ", options={1, 2})
                toss_player_num = get_validated_input(f"Enter your toss number ({MIN_INPUT}-{MAX_INPUT}): ", check_range=True, min_val=MIN_INPUT, max_val=MAX_INPUT)
                toss_comp_num = random.randint(MIN_INPUT, MAX_INPUT)
                toss_sum = toss_player_num + toss_comp_num
                is_even = toss_sum % 2 == 0
                toss_result_str = "Even" if is_even else "Odd"
                toss_result_num = 2 if is_even else 1

                print(f"\n > Your toss number : {toss_player_num}")
                print(f" > Computer's number: {toss_comp_num}")
                print(f" > Sum              : {toss_sum} ({toss_result_str})")
                time.sleep(0.5)

                player_won_toss = (toss_choice == toss_result_num)
                temp_player_bats_first = None

                if player_won_toss:
                    print("\n*** You Won the Toss! ***")
                    player_decision = get_validated_input("Choose to Bat or Bowl (1=Bat, 2=Bowl): ", options={1, 2})
                    temp_player_bats_first = (player_decision == 1)
                    decision_str = "Bat First" if temp_player_bats_first else "Bowl First"
                    print(f"   You chose to {decision_str}.")
                else:
                    print("\n--- You Lost the Toss ---")
                    comp_decision = random.randint(1, 2)
                    temp_player_bats_first = (comp_decision == 2)
                    decision_str = "Bat First" if comp_decision == 1 else "Bowl First"
                    print(f"   The Computer chose to {decision_str}.")

                settings['player_bats_first'] = temp_player_bats_first
                time.sleep(1.5)
                print("\nAll settings configured and toss completed!")
                print("Starting game...")
                time.sleep(1.5)
                break # Exit setup loop

            else:
                print("\nCannot start game yet. Please configure:")
                for item in missing: print(f"  - {item}")
                time.sleep(2)

        elif choice == 4:
            exit_game("Exiting setup...")

    # --- Prepare final config dictionary ---
    final_config = {
        'Gamemode': settings['gamemode'],
        'TotalOvers': float(settings['overs']),
        'TotalWickets': settings['wickets'],
        'Difficulty': settings['difficulty'],
        'PlayerBatsFirst': settings['player_bats_first']
    }

    print("\n--- Game Setup Complete ---")
    time.sleep(1)
    return final_config

# --- Core Game Logic ---

def play_innings(total_overs, total_wickets, player_is_batting, target=None):
    """
    Simulates a single innings of the game.
    Args: ... (same as before)
    Returns: ... (same as before)
    """
    score = 0
    wickets_fallen = 0
    overs_bowled = 0.0

    print(f"\n--- {'Player' if player_is_batting else 'Computer'} Batting ---")
    if target is not None:
        print(f"Target: {target} runs")
    time.sleep(0.5)

    while True:
        # --- Check Innings End Conditions ---
        overs_limit_reached = overs_bowled >= total_overs
        wickets_limit_reached = wickets_fallen >= total_wickets

        if overs_limit_reached or wickets_limit_reached:
            print("\n--- End of Innings ---")
            if overs_limit_reached: print(f"Reason: Overs ({overs_bowled:.1f}/{total_overs:.1f}) completed.")
            if wickets_limit_reached: print(f"Reason: All out ({wickets_fallen}/{total_wickets} wickets).")
            break

        if target is not None and score >= target:
            # Target chased check (already handled below, but good to have exit condition)
            break

        # --- Display Status Before the Ball ---
        print("-" * 25)
        print(f" Score: {score}/{wickets_fallen}")
        print(f" Overs: {overs_bowled:.1f}/{total_overs:.1f}")
        if target is not None:
            runs_needed = target - score
            balls_in_over = int(round((overs_bowled - int(overs_bowled)) * 10))
            overs_completed = int(overs_bowled)
            total_balls = int(total_overs * 6)
            balls_bowled = overs_completed * 6 + balls_in_over
            balls_remaining = total_balls - balls_bowled
            if balls_remaining < 0: balls_remaining = 0
            ball_str = "ball" if balls_remaining == 1 else "balls"
            print(f" Need {runs_needed} runs to win" + (f" from {balls_remaining} {ball_str}" if balls_remaining >= 0 else ""))
        print("-" * 25)

        # --- Get Inputs for the Current Ball ---
        prompt_verb = "Bat" if player_is_batting else "Bowl"
        player_num = get_validated_input(f"Player {prompt_verb} ({MIN_INPUT}-{MAX_INPUT}): ", check_range=True, min_val=MIN_INPUT, max_val=MAX_INPUT)

        # Calculate the fractional part of the over (0.0 to 0.5)
        current_ball_fraction = round(overs_bowled % 1.0, 1)
        # Get computer's prediction, passing the ball fraction
        computer_num = prediction.predict()

        # --- Store Choices ---
        prediction.store_choice(player_num, computer_num, current_ball_fraction)

        # --- Display Player and Computer Choices ---
        print(f" > Player Input:   {player_num}")
        print(f" > Computer Input: {computer_num}")
        time.sleep(0.3)

        # --- Determine Ball Outcome ---
        batting_num = player_num if player_is_batting else computer_num
        bowling_num = computer_num if player_is_batting else player_num

        if batting_num == bowling_num:
            wickets_fallen += 1
            print(f" !! OUT !! Wicket {wickets_fallen}/{total_wickets}. Score remains {score}.")
        else:
            runs_scored = batting_num
            score += runs_scored
            run_str = "run" if runs_scored == 1 else "runs"
            print(f" >> {runs_scored} {run_str} scored! Score is now {score}/{wickets_fallen}.")

        # --- Update Overs ---
        is_last_wicket = (batting_num == bowling_num and wickets_fallen >= total_wickets)
        target_chased_this_ball = (target is not None and score >= target)
        # Check against state *before* potential over advancement
        can_advance_over = not (overs_bowled >= total_overs or is_last_wicket or target_chased_this_ball)

        if can_advance_over:
             overs_bowled = calculate_next_over(overs_bowled) # Use the precise calculator


        # Check if target was chased *on this ball*
        if target is not None and score >= target:
             print(f"\n--- Target Chased! ({score} runs) ---")
             time.sleep(1)
             break # Exit the loop immediately after chasing


        time.sleep(0.8)

    # --- Innings Summary ---
    print(f"\nFinal Innings Score: {score}/{wickets_fallen} in {overs_bowled:.1f} overs")
    time.sleep(1.5)
    return score, wickets_fallen, overs_bowled


# --- run_game Function ---
def run_game(game_config):
    """Runs the main game flow based on the configuration."""

    total_overs = game_config['TotalOvers']
    total_wickets = game_config['TotalWickets']
    player_bats_first = game_config['PlayerBatsFirst']

    # --- Innings 1 ---
    print("\n=== INNINGS 1 ===")
    score1, wickets1, overs1 = play_innings(
        total_overs=total_overs,
        total_wickets=total_wickets,
        player_is_batting=player_bats_first
    )
    target = score1 + 1
    # Store details more granularly for final summary
    player1_details = (score1, wickets1, overs1) if player_bats_first else (None, None, None)
    computer1_details = (score1, wickets1, overs1) if not player_bats_first else (None, None, None)

    # --- Innings 2 ---
    print("\n=== INNINGS 2 ===")
    score2, wickets2, overs2 = play_innings(
        total_overs=total_overs,
        total_wickets=total_wickets,
        player_is_batting=not player_bats_first, # Opposite of first innings
        target=target
    )
    player2_details = (score2, wickets2, overs2) if not player_bats_first else (None, None, None)
    computer2_details = (score2, wickets2, overs2) if player_bats_first else (None, None, None)

    # --- Determine Winner ---
    print("\n=== GAME OVER ===")
    time.sleep(1)
    print("\n--- Final Scores ---")

    # Unpack details safely, providing defaults if innings didn't happen (unlikely here)
    p_s1, p_w1, p_o1 = player1_details if player1_details[0] is not None else (0, 0, 0.0)
    c_s1, c_w1, c_o1 = computer1_details if computer1_details[0] is not None else (0, 0, 0.0)
    p_s2, p_w2, p_o2 = player2_details if player2_details[0] is not None else (0, 0, 0.0)
    c_s2, c_w2, c_o2 = computer2_details if computer2_details[0] is not None else (0, 0, 0.0)

    # Display scores clearly
    if player_bats_first:
        print(f"Player (Innings 1):   {p_s1}/{p_w1} ({p_o1:.1f} Ov)")
        print(f"Computer (Innings 2): {c_s2}/{c_w2} ({c_o2:.1f} Ov)")
    else:
        print(f"Computer (Innings 1): {c_s1}/{c_w1} ({c_o1:.1f} Ov)")
        print(f"Player (Innings 2):   {p_s2}/{p_w2} ({p_o2:.1f} Ov)")
    print(f"Target was: {target}")
    print("-" * 20)

    # Determine result based on second innings
    second_batting_score = score2
    second_batting_wickets = wickets2
    first_innings_score = score1
    second_batting_player = not player_bats_first

    if second_batting_score >= target:
        winner = "Player" if second_batting_player else "Computer"
        wickets_left = total_wickets - second_batting_wickets
        print(f"{winner} wins by {wickets_left} wicket{'s' if wickets_left != 1 else ''}!")
    elif second_batting_score < first_innings_score:
        winner = "Computer" if second_batting_player else "Player" # Team that batted first wins
        runs_margin = first_innings_score - second_batting_score
        print(f"{winner} wins by {runs_margin} run{'s' if runs_margin != 1 else ''}!")
    else: # second_batting_score == first_innings_score
        print("It's a TIE!")


# --- Main Execution ---
if __name__ == "__main__":
    try:
        game_settings = game_setup()
        # Initializing prediction module
        prediction.initialize(game_settings['Difficulty'])
        run_game(game_settings)
    except KeyboardInterrupt:
        exit_game("\nGame interrupted by user.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
        exit_game("Exiting due to error.")