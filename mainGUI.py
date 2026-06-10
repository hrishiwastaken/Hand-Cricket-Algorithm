# hand_cricket_gui.py
import pygame
import sys
import random
import time
import traceback # For more detailed error reporting
import data

# Setting up a placeholder object to call reset function.
reset = data.Data(r"datastorecsv\I_ComboDistributive.csv")

try:
    import prediction # Ensure prediction.py is in the same directory
    print("Imported prediction successfully.")
except ImportError:
    print("ERROR: Could not import prediction.py! Make sure it's in the same folder.")
    sys.exit()
except Exception as e:
    print(f"Error importing prediction: {e}")
    sys.exit()


# --- Pygame Initialization ---
print("--- Initializing Pygame ---")
try:
    init_status = pygame.init()
    print(f"pygame.init() status (failures, successes): {init_status}")
    if init_status[1] > 0:
        print(f"WARNING: {init_status[1]} pygame modules failed to initialize.")
    pygame.font.init()
    print("Pygame font system initialized.")
except Exception as e:
    print(f"CRITICAL ERROR during Pygame init: {e}")
    traceback.print_exc()
    sys.exit()


# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 650
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (80, 80, 80)
BLUE = (30, 144, 255) # Dodger Blue
LIGHT_BLUE = (173, 216, 230) # Light Blue (for hover)
GREEN = (50, 205, 50) # Lime Green
RED = (255, 69, 0) # Red-Orange
GOLD = (255, 215, 0)
BACKGROUND_COLOR = (240, 248, 255) # Alice Blue
print("Constants and colors defined.")


# --- Fonts ---
print("Loading fonts...")
FONT_TITLE = None; FONT_HEADING = None; FONT_NORMAL = None; FONT_BUTTON = None; FONT_SCORE = None; FONT_SMALL = None
try:
    FONT_TITLE = pygame.font.SysFont("arial", 60, bold=True)
    FONT_HEADING = pygame.font.SysFont("arial", 36, bold=True)
    FONT_NORMAL = pygame.font.SysFont("arial", 24)
    FONT_BUTTON = pygame.font.SysFont("arial", 20, bold=True)
    FONT_SCORE = pygame.font.SysFont("arial", 30)
    FONT_SMALL = pygame.font.SysFont("arial", 18)
    print("Arial fonts loaded.")
except Exception as e_sysfont:
    print(f"Warning: Arial font not found or failed ({e_sysfont}), using default.")
    try:
        FONT_TITLE = pygame.font.Font(None, 70); FONT_HEADING = pygame.font.Font(None, 45); FONT_NORMAL = pygame.font.Font(None, 30)
        FONT_BUTTON = pygame.font.Font(None, 28); FONT_SCORE = pygame.font.Font(None, 36); FONT_SMALL = pygame.font.Font(None, 24)
        print("Default fonts loaded."); assert FONT_TITLE is not None # Check default load
    except Exception as e_defaultfont: print(f"CRITICAL ERROR loading default fonts: {e_defaultfont}"); pygame.quit(); reset.reset(); sys.exit()


# --- Screen Setup ---
print("Setting display mode...")
screen = None
try:
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    if not screen: raise RuntimeError("pygame.display.set_mode failed.")
    pygame.display.set_caption("Hand Cricket Premium")
    print("Display mode and caption set.")
except Exception as e: print(f"CRITICAL ERROR setting display mode: {e}"); traceback.print_exc(); pygame.quit(); reset.reset(); sys.exit()


clock = pygame.time.Clock()
print("Clock created.")


# Game States
WELCOME = "welcome"; SETUP = "setup"; TOSS_CALL = "toss_call"; TOSS_NUMBER = "toss_number"; TOSS_RESULT = "toss_result"
TOSS_CHOICE = "toss_choice"; PLAYING = "playing"; INNINGS_BREAK = "innings_break"; GAME_OVER = "game_over"


# --- Game Variables (Global State) ---
print("Initializing game variables...")
game_state = WELCOME
game_settings = {'gamemode': None,'overs': None,'wickets': None,'difficulty': 1,'player_bats_first': None}
temp_toss_call = None; temp_toss_player_num = None; temp_toss_comp_num = None; temp_toss_sum = None; temp_toss_winner = None
message_display_time = 0; message_text = ""; next_state_after_message = None
current_innings = 1; player_score = 0; player_wickets = 0; player_overs_bowled = 0.0
computer_score = 0; computer_wickets = 0; computer_overs_bowled = 0.0; target = None
current_player_input = None; current_computer_input = None; last_ball_result = ""
ball_result_timer = 0; player_is_batting_now = None
input_locked_this_turn = False # <<< New state variable for input lock

# Input Pad Buttons (Data)
INPUT_BTN_SIZE = 50; INPUT_BTN_GAP = 10; INPUT_PAD_COLS = 5
INPUT_PAD_X_START = (SCREEN_WIDTH - (INPUT_PAD_COLS * INPUT_BTN_SIZE + (INPUT_PAD_COLS - 1) * INPUT_BTN_GAP)) // 2
INPUT_PAD_Y_PLAY = SCREEN_HEIGHT - 180; INPUT_PAD_Y_TOSS = SCREEN_HEIGHT - 250
input_buttons_data = [{'num': i} for i in range(1, 11)]
print("Game variables initialized.")


# --- Helper Functions ---

def draw_text(text, font, color, surface, x, y, center_x=False, center_y=False):
    """Draws text on a surface, handling potential font errors."""
    if font is None:
        print(f"Error: Font not loaded, cannot draw text '{text}'")
        return pygame.Rect(x, y, 0, 0)
    try:
        text_obj = font.render(str(text), True, color) # Ensure text is string
        text_rect = text_obj.get_rect()

        # --- CORRECTED Coordinate Assignment ---
        if center_x:
            text_rect.centerx = x
        else: # else on a new line
            text_rect.left = x

        if center_y:
            text_rect.centery = y
        else: # else on a new line
            text_rect.top = y
        # --------------------------------------

        surface.blit(text_obj, text_rect)
        return text_rect
    except Exception as e:
        print(f"Error rendering or blitting text '{text}': {e}")
        try: # Fallback error text
            d_font = pygame.font.Font(None, 24); text_obj = d_font.render(f"ERR:'{str(text)}'", True, RED)
            text_rect = text_obj.get_rect(topleft=(x,y)); surface.blit(text_obj, text_rect); return text_rect
        except Exception: return pygame.Rect(x, y, 0, 0)

def draw_button(text, x, y, w, h, inactive_color, active_color, text_color=BLACK, font=None, border_radius=5):
    global FONT_BUTTON
    button_font = font if font is not None else FONT_BUTTON
    if button_font is None: print(f"Error: Font missing for button '{text}'"); return False, pygame.Rect(x,y,w,h)
    mouse_pos = pygame.mouse.get_pos(); mouse_pressed = pygame.mouse.get_pressed(); clicked_now = False
    button_rect = pygame.Rect(x, y, w, h); on_button = button_rect.collidepoint(mouse_pos)
    current_color = active_color if on_button else inactive_color
    if on_button and mouse_pressed[0] == 1:
         pygame.time.wait(75) # <<< Reduced debounce delay
         mouse_pressed = pygame.mouse.get_pressed(); on_button_after_wait = button_rect.collidepoint(pygame.mouse.get_pos())
         if mouse_pressed[0] == 1 and on_button_after_wait: clicked_now = True
    try: pygame.draw.rect(screen, current_color, button_rect, border_radius=border_radius)
    except Exception as e: print(f"Error drawing button rect: {e}"); pygame.draw.rect(screen, RED, button_rect, 2)
    try:
        text_surf = button_font.render(str(text), True, text_color); text_rect = text_surf.get_rect(center=button_rect.center); screen.blit(text_surf, text_rect)
    except Exception as e: print(f"Error drawing button text '{text}': {e}")
    return clicked_now, button_rect


# --- Core Game Logic / State Management ---

def reset_innings_vars():
    """Resets variables needed between innings or for starting over."""
    global current_player_input, current_computer_input, last_ball_result, ball_result_timer
    global temp_toss_call, temp_toss_player_num, temp_toss_comp_num, temp_toss_sum, temp_toss_winner
    global input_locked_this_turn # <<< Reset input lock
    # print("Resetting innings/temporary variables.")
    current_player_input = None; current_computer_input = None; last_ball_result = ""
    ball_result_timer = 0; temp_toss_call = None; temp_toss_player_num = None
    temp_toss_comp_num = None; temp_toss_sum = None; temp_toss_winner = None
    input_locked_this_turn = False # <<< Ensure unlocked


def reset_game_variables():
     """Resets ALL major game state variables for a new game."""
     global game_settings, current_innings, player_score, player_wickets, player_overs_bowled
     global computer_score, computer_wickets, computer_overs_bowled, target, player_is_batting_now
     global game_state
     print("Resetting ALL game variables.")
     game_settings = {k: None for k in game_settings}; game_settings['difficulty'] = 1
     current_innings = 1; player_score = 0; player_wickets = 0; computer_score = 0; computer_wickets = 0
     player_overs_bowled = 0.0; computer_overs_bowled = 0.0; target = None; player_is_batting_now = None
     reset_innings_vars() # Also resets input lock


def process_ball(player_num):
    """Processes one ball of the game based on player input."""
    global player_score, player_wickets, player_overs_bowled, computer_score, computer_wickets
    global computer_overs_bowled, last_ball_result, ball_result_timer, game_state
    global current_innings, target, player_is_batting_now, current_player_input, current_computer_input
    global input_locked_this_turn

    # --- Initial State Check ---
    if player_is_batting_now is None:
        print("CRITICAL ERROR in process_ball: player_is_batting_now is None!")
        schedule_message("Internal Error! Resetting.", 2500, WELCOME); reset_game_variables(); return

    total_wickets_allowed = game_settings.get('wickets'); total_overs_allowed = game_settings.get('overs')
    if total_wickets_allowed is None or total_overs_allowed is None:
         print("CRITICAL ERROR: Game settings incomplete in process_ball!"); schedule_message("Setup Error! Resetting.", 2500, WELCOME); reset_game_variables(); return
    total_overs_allowed = float(total_overs_allowed)

    # --- Get Computer Prediction ---
    # Still needed for computer BOWLING and for learning in store_choice
    comp_num_prediction = prediction.predict()
    if not (1 <= comp_num_prediction <= 10):
        print(f"WARNING: predict() returned {comp_num_prediction}. Clamping to random.")
        comp_num_prediction = random.randint(1, 10)

    # --- Determine ACTUAL numbers used & Set Display Variables ---
    batting_num = 0
    bowling_num = 0
    actual_computer_num_this_ball = 0 # Track the number computer *actually* used

    current_player_input = player_num # Player's choice is always stored

    if player_is_batting_now:
        # Player is batting
        batting_num = player_num
        bowling_num = comp_num_prediction # Computer uses its prediction when bowling
        actual_computer_num_this_ball = comp_num_prediction # Computer used the prediction
    else:
        # Computer is batting
        computer_batting_choice = random.randint(1, 10) # Generate random choice
        batting_num = computer_batting_choice           # Computer bats random
        bowling_num = player_num                        # Player bowls their input
        actual_computer_num_this_ball = computer_batting_choice # Computer used the random choice

    # Set the number displayed for the computer based on the actual number used
    current_computer_input = actual_computer_num_this_ball

    # --- Determine Ball Outcome ---
    score_before = player_score if player_is_batting_now else computer_score
    wickets_before = player_wickets if player_is_batting_now else computer_wickets
    overs_bowled_before = player_overs_bowled if player_is_batting_now else computer_overs_bowled

    is_out = (batting_num == bowling_num)

    runs_scored_this_ball = 0
    score_after = score_before
    wickets_after = wickets_before # Start with previous value

    if is_out:
        wickets_after += 1 # Increment wicket count LOCALLY
        current_batting_team = "Player" if player_is_batting_now else "Computer"
        last_ball_result = f"OUT! ({batting_num} vs {bowling_num}) ({current_batting_team})"
    else:
        runs_scored_this_ball = batting_num
        score_after += runs_scored_this_ball
        run_str = "run" if runs_scored_this_ball == 1 else "runs"
        last_ball_result = f"{runs_scored_this_ball} {run_str}!"

    ball_result_timer = pygame.time.get_ticks() + 1500 # Schedule result display

    # --- Update GLOBAL Scores/Wickets ---
    if player_is_batting_now:
        player_score = score_after
        player_wickets = wickets_after # Assign updated value
    else:
        computer_score = score_after
        computer_wickets = wickets_after # Assign updated value

    # --- Store the choice data using prediction.py ---
    ball_fraction = round(overs_bowled_before % 1.0, 1)
    try:
        # Always store player input vs computer *prediction* for learning
        prediction.store_choice(player_num, comp_num_prediction, ball_fraction)
    except Exception as e:
        print(f"ERROR calling prediction.store_choice: {e}")
        traceback.print_exc() # Keep traceback for this error source

    # --- Check End of Innings Conditions ---
    # Use the locally calculated 'wickets_after' for the check
    end_of_wickets = wickets_after >= total_wickets_allowed
    target_reached = (target is not None and score_after >= target)

    # --- Advance Over ---
    overs_after = overs_bowled_before
    end_of_overs = False
    # Don't advance over if innings ended by wickets or target chase this ball
    if not (end_of_wickets or target_reached):
        overs_after = calculate_next_over(overs_bowled_before)
        # Assign the updated over count
        if player_is_batting_now: player_overs_bowled = overs_after
        else: computer_overs_bowled = overs_after
        # Now check if the *new* over count reached the limit
        if overs_after >= total_overs_allowed:
             end_of_overs = True

    # --- Final Innings End Check ---
    innings_ends_this_ball = end_of_wickets or target_reached or end_of_overs

    if innings_ends_this_ball:
        next_st = INNINGS_BREAK if current_innings == 1 else GAME_OVER
        schedule_message("End of Innings!", 2000, next_st)

    input_locked_this_turn = True # Lock input after processing ball


def calculate_next_over(current_over):
    next_ball_over = round(current_over + 0.1, 1)
    if abs(next_ball_over % 1.0 - 0.6) < 0.01: return float(int(current_over) + 1)
    else: return next_ball_over


def schedule_message(text, duration_ms, next_state):
    global message_text, message_display_time, next_state_after_message
    # print(f"Scheduling message: '{text}' for {duration_ms}ms, next state: {next_state}") # Reduce noise
    message_text = text; message_display_time = pygame.time.get_ticks() + duration_ms; next_state_after_message = next_state

def check_scheduled_message():
    global game_state, message_display_time, next_state_after_message
    if message_display_time > 0 and pygame.time.get_ticks() >= message_display_time:
        intended_next_state = next_state_after_message
        # print(f"Message timer expired. Intended next state: {intended_next_state}")
        message_display_time = 0; next_state_after_message = None
        if intended_next_state is not None: game_state = intended_next_state
        else: print("Warning: Next state after message was None.")


# --- Drawing Functions for Each State ---

def draw_welcome_screen():
    screen.fill(BACKGROUND_COLOR)
    draw_text("Hand Cricket", FONT_TITLE, BLUE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 - 40, center_x=True)
    draw_text("Premium GUI Edition", FONT_NORMAL, DARK_GRAY, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 + 30, center_x=True)
    start_clicked, _ = draw_button("Start Game", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50, 200, 50, BLUE, LIGHT_BLUE, WHITE)
    quit_clicked, _ = draw_button("Quit", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 120, 200, 50, DARK_GRAY, LIGHT_GRAY, WHITE)
    next_state = WELCOME
    if start_clicked: reset_game_variables(); next_state = SETUP
    if quit_clicked: pygame.quit(); reset.reset(); sys.exit()
    return next_state

def draw_setup_screen():
    global game_settings
    screen.fill(BACKGROUND_COLOR)
    draw_text("Game Setup", FONT_HEADING, BLUE, screen, SCREEN_WIDTH // 2, 50, center_x=True)
    y_offset = 120; input_area_x = 280; input_width = SCREEN_WIDTH - input_area_x - 50

    # Gamemode
    draw_text("Gamemode:", FONT_NORMAL, BLACK, screen, 50, y_offset + 5)
    gm_btn_width = (input_width - 10) // 2
    legacy_clicked, _ = draw_button("Legacy (1 Wkt)", input_area_x, y_offset, gm_btn_width, 40, LIGHT_GRAY if game_settings['gamemode'] != 1 else BLUE, LIGHT_BLUE)
    custom_clicked, _ = draw_button("Custom Wickets", input_area_x + gm_btn_width + 10, y_offset, gm_btn_width, 40, LIGHT_GRAY if game_settings['gamemode'] != 2 else BLUE, LIGHT_BLUE)
    if legacy_clicked: game_settings['gamemode'] = 1; game_settings['wickets'] = 1
    if custom_clicked:
        if game_settings['gamemode'] != 2: game_settings['wickets'] = None
        game_settings['gamemode'] = 2
    y_offset += 60

    # Wickets
    if game_settings['gamemode'] == 2:
        draw_text("Wickets (1-10):", FONT_NORMAL, BLACK, screen, 50, y_offset + 5)
        wkt_options=list(range(1, 11)); wkt_btn_size=45; wkt_btn_gap=8; wkt_cols=5
        num_rows = (len(wkt_options) + wkt_cols - 1) // wkt_cols
        for i, w in enumerate(wkt_options):
            col=i%wkt_cols; row=i//wkt_cols; bx=input_area_x+col*(wkt_btn_size+wkt_btn_gap); by=y_offset+row*(wkt_btn_size+wkt_btn_gap)
            w_clicked, _ = draw_button(str(w), bx, by, wkt_btn_size, wkt_btn_size, LIGHT_GRAY if game_settings['wickets'] != w else BLUE, LIGHT_BLUE)
            if w_clicked: game_settings['wickets'] = w
        y_offset += num_rows * (wkt_btn_size + wkt_btn_gap) + 10
    elif game_settings['gamemode'] == 1:
         draw_text("Wickets:", FONT_NORMAL, BLACK, screen, 50, y_offset+5); draw_text("1 (Legacy)", FONT_NORMAL, DARK_GRAY, screen, input_area_x, y_offset+5); y_offset += 60
    else: draw_text("Wickets:", FONT_NORMAL, DARK_GRAY, screen, 50, y_offset+5); draw_text("(Select Gamemode)", FONT_NORMAL, DARK_GRAY, screen, input_area_x, y_offset+5); y_offset += 60

    # Overs
    draw_text("Overs:", FONT_NORMAL, BLACK, screen, 50, y_offset + 5)
    over_options = [10, 20, 30, 40, 50]; ov_btn_width = max(50, (input_width - (len(over_options) - 1) * 10) // len(over_options))
    for i, o in enumerate(over_options):
         o_clicked, _ = draw_button(str(o), input_area_x + i * (ov_btn_width + 10), y_offset, ov_btn_width, 40, LIGHT_GRAY if game_settings['overs'] != o else BLUE, LIGHT_BLUE)
         if o_clicked: game_settings['overs'] = o
    y_offset += 60

    # Difficulty
    draw_text("Difficulty:", FONT_NORMAL, BLACK, screen, 50, y_offset + 5)
    diff_btn_width = max(80, (input_width - 2*10) // 3)
    e_clicked, _ = draw_button("Easy", input_area_x, y_offset, diff_btn_width, 40, LIGHT_GRAY if game_settings['difficulty'] != 1 else GREEN, LIGHT_BLUE)
    m_clicked, _ = draw_button("Medium", input_area_x + diff_btn_width + 10, y_offset, diff_btn_width, 40, LIGHT_GRAY if game_settings['difficulty'] != 2 else GOLD, LIGHT_BLUE)
    h_clicked, _ = draw_button("Hard", input_area_x + 2*(diff_btn_width+10), y_offset, diff_btn_width, 40, LIGHT_GRAY if game_settings['difficulty'] != 3 else RED, LIGHT_BLUE)
    if e_clicked: game_settings['difficulty'] = 1
    elif m_clicked: game_settings['difficulty'] = 2
    elif h_clicked: game_settings['difficulty'] = 3
    y_offset += 75

    # Validation & Buttons
    ready = all(game_settings.get(k) is not None for k in ['gamemode', 'overs', 'wickets'])
    confirm_y = SCREEN_HEIGHT - 100; back_y = confirm_y; next_state = SETUP
    if ready:
        confirm_clicked, _ = draw_button("Confirm & Proceed to Toss", SCREEN_WIDTH // 2 - 150, confirm_y, 300, 50, GREEN, LIGHT_BLUE, WHITE)
        if confirm_clicked:
            if game_settings['gamemode'] == 1: game_settings['wickets'] = 1
            reset_innings_vars()
            schedule_message("Settings Confirmed!", 1000, TOSS_CALL) # <<< Feedback Message
            next_state = SETUP # Stay in setup until message timer finishes
    else:
        missing = [k.capitalize() for k in ['gamemode', 'overs', 'wickets'] if game_settings.get(k) is None and not (k=='wickets' and game_settings.get('gamemode')==1)]
        if game_settings.get('gamemode') == 2 and game_settings.get('wickets') is None and 'Wickets' not in missing: missing.append("Wickets (Custom)")
        if missing: draw_text("Select: " + ", ".join(missing), FONT_SMALL, RED, screen, SCREEN_WIDTH//2, confirm_y - 30, center_x=True)
        pygame.draw.rect(screen, LIGHT_GRAY, (SCREEN_WIDTH // 2 - 150, confirm_y, 300, 50), border_radius=5)
        draw_text("Confirm & Proceed", FONT_BUTTON, DARK_GRAY, screen, SCREEN_WIDTH//2, confirm_y + 25, center_x=True, center_y=True)

    back_clicked, _ = draw_button("Back", 50, back_y, 100, 40, DARK_GRAY, LIGHT_GRAY, WHITE)
    if back_clicked: reset_game_variables(); next_state = WELCOME
    return next_state

def draw_toss_call_screen():
    global temp_toss_call, input_locked_this_turn # <<< Reset lock when entering
    screen.fill(BACKGROUND_COLOR)
    draw_text("Toss Time!", FONT_HEADING, BLUE, screen, SCREEN_WIDTH // 2, 100, center_x=True)
    draw_text("Call Odd or Even", FONT_NORMAL, BLACK, screen, SCREEN_WIDTH // 2, 200, center_x=True)
    btn_y = 280; btn_w = 120; btn_h = 50
    odd_clicked, _ = draw_button("Odd", SCREEN_WIDTH // 2 - 150, btn_y, btn_w, btn_h, BLUE, LIGHT_BLUE, WHITE)
    even_clicked, _ = draw_button("Even", SCREEN_WIDTH // 2 + 30, btn_y, btn_w, btn_h, BLUE, LIGHT_BLUE, WHITE)
    next_state = TOSS_CALL; msg = None
    if odd_clicked: temp_toss_call = 1; next_state = TOSS_NUMBER; msg = "Called Odd"
    if even_clicked: temp_toss_call = 2; next_state = TOSS_NUMBER; msg = "Called Even"
    if next_state == TOSS_NUMBER:
         global temp_toss_player_num, temp_toss_comp_num, temp_toss_sum, temp_toss_winner
         temp_toss_player_num = temp_toss_comp_num = temp_toss_sum = temp_toss_winner = None
         input_locked_this_turn = False # <<< Unlock input for number selection
         schedule_message(msg, 1000, next_state) # <<< Feedback Message
         return TOSS_CALL # Stay until message finishes
    back_clicked, _ = draw_button("Back", 50, SCREEN_HEIGHT - 70, 100, 40, DARK_GRAY, LIGHT_GRAY, WHITE)
    if back_clicked: next_state = SETUP
    return next_state

def draw_toss_number_screen():
    global temp_toss_player_num, temp_toss_comp_num, temp_toss_sum, temp_toss_winner
    global input_locked_this_turn # <<< Read and modify lock state

    screen.fill(BACKGROUND_COLOR)
    draw_text("Toss: Choose Your Number", FONT_HEADING, BLUE, screen, SCREEN_WIDTH // 2, 100, center_x=True)
    draw_text("(1 to 10)", FONT_NORMAL, DARK_GRAY, screen, SCREEN_WIDTH // 2, 150, center_x=True)

    # Only draw input pad if input isn't locked
    clicked_num = None
    if not input_locked_this_turn:
        draw_text("Click or Press Number Key (1-9, 0 for 10)", FONT_SMALL, BLACK, screen, SCREEN_WIDTH // 2, INPUT_PAD_Y_TOSS - 30, center_x=True)
        for i, btn_data in enumerate(input_buttons_data[:10]):
            row=i//INPUT_PAD_COLS; col=i%INPUT_PAD_COLS; bx=INPUT_PAD_X_START+col*(INPUT_BTN_SIZE+INPUT_BTN_GAP); by=INPUT_PAD_Y_TOSS+row*(INPUT_BTN_SIZE+INPUT_BTN_GAP)
            num_clicked, _ = draw_button(str(btn_data['num']), bx, by, INPUT_BTN_SIZE, INPUT_BTN_SIZE, BLUE, LIGHT_BLUE, WHITE)
            if num_clicked: clicked_num = btn_data['num']
    else:
        # Optionally display something indicating input is locked/processing
        draw_text("Processing...", FONT_NORMAL, DARK_GRAY, screen, SCREEN_WIDTH // 2, INPUT_PAD_Y_TOSS + 50, center_x=True)


    next_state = TOSS_NUMBER # Default: stay
    if clicked_num is not None:
        # Process the click (logic moved to main loop for keyboard)
        # Here we just signal that a number was chosen via mouse
        process_toss_number(clicked_num) # Use helper
        # process_toss_number will set lock and determine next state
        next_state = game_state # Reflect state change from helper

    back_clicked, _ = draw_button("Back", 50, SCREEN_HEIGHT - 70, 100, 40, DARK_GRAY, LIGHT_GRAY, WHITE)
    if back_clicked:
        temp_toss_player_num = None # Clear number selection
        next_state = TOSS_CALL

    return next_state

# Helper function to process toss number input (from mouse or keyboard)
def process_toss_number(number):
    global temp_toss_player_num, temp_toss_comp_num, temp_toss_sum, temp_toss_winner
    global input_locked_this_turn, game_state # Need to modify state

    if input_locked_this_turn: return # Ignore if already locked

    print(f"Toss number chosen: {number}")
    temp_toss_player_num = number
    temp_toss_comp_num = random.randint(1, 10)
    temp_toss_sum = temp_toss_player_num + temp_toss_comp_num
    toss_result_num = 2 if (temp_toss_sum % 2 == 0) else 1

    if temp_toss_call is None:
        print("Error: Toss call missing!"); game_state = TOSS_CALL # Go back
    else:
        temp_toss_winner = 'player' if temp_toss_call == toss_result_num else 'computer'
        game_settings['player_bats_first'] = None # Clear setting before result display
        schedule_message(f"You chose {number}", 1000, TOSS_RESULT) # <<< Feedback
        game_state = TOSS_NUMBER # Stay until message finishes

    input_locked_this_turn = True # <<< Lock input


def draw_toss_result_screen():
    global game_settings, player_is_batting_now, temp_toss_call, temp_toss_player_num, temp_toss_comp_num, temp_toss_sum, temp_toss_winner
    screen.fill(BACKGROUND_COLOR)
    draw_text("Toss Result", FONT_HEADING, BLUE, screen, SCREEN_WIDTH // 2, 80, center_x=True)
    y_pos = 150
    if temp_toss_call is not None: draw_text(f"You Called : {'Odd' if temp_toss_call == 1 else 'Even'}", FONT_NORMAL, BLACK, screen, SCREEN_WIDTH//2, y_pos, center_x=True); y_pos += 40
    if temp_toss_player_num is not None: draw_text(f"Your Number: {temp_toss_player_num}", FONT_NORMAL, BLACK, screen, SCREEN_WIDTH // 2, y_pos, center_x=True); y_pos += 40
    if temp_toss_comp_num is not None: draw_text(f"CPU Number : {temp_toss_comp_num}", FONT_NORMAL, BLACK, screen, SCREEN_WIDTH // 2, y_pos, center_x=True); y_pos += 40
    if temp_toss_sum is not None: sum_result = "Even" if temp_toss_sum % 2 == 0 else "Odd"; draw_text(f"Sum = {temp_toss_sum} ({sum_result})", FONT_NORMAL, BLACK, screen, SCREEN_WIDTH // 2, y_pos, center_x=True); y_pos += 60
    else: draw_text("Calculating...", FONT_NORMAL, DARK_GRAY, screen, SCREEN_WIDTH // 2, y_pos + 40, center_x=True); y_pos += 100

    next_state = TOSS_RESULT
    if temp_toss_winner is not None and temp_toss_sum is not None:
        proceed_y = y_pos + 70; comp_choice_y = y_pos + 60; start_game_y = y_pos + 110
        if temp_toss_winner == 'player':
            draw_text("You Won the Toss!", FONT_HEADING, GREEN, screen, SCREEN_WIDTH // 2, y_pos, center_x=True)
            proceed_clicked, _ = draw_button("Choose Bat/Bowl", SCREEN_WIDTH // 2 - 100, proceed_y, 200, 50, BLUE, LIGHT_BLUE, WHITE)
            if proceed_clicked: game_settings['player_bats_first'] = None; next_state = TOSS_CHOICE
        else: # Computer won
            draw_text("Computer Won the Toss", FONT_HEADING, RED, screen, SCREEN_WIDTH // 2, y_pos, center_x=True)
            if game_settings.get('player_bats_first') is None: game_settings['player_bats_first'] = (random.randint(1, 2) == 2)
            pbf_setting = game_settings.get('player_bats_first', False)
            choice_text = "Computer chose to Bat" if not pbf_setting else "Computer chose to Bowl"
            draw_text(choice_text, FONT_NORMAL, BLACK, screen, SCREEN_WIDTH//2, comp_choice_y, center_x=True)
            proceed_clicked, _ = draw_button("Start Game", SCREEN_WIDTH // 2 - 100, start_game_y, 200, 50, GREEN, LIGHT_BLUE, WHITE)
            if proceed_clicked:
                 player_is_batting_now = game_settings.get('player_bats_first')
                 if player_is_batting_now is None: print("ERROR starting game!"); next_state = TOSS_CALL
                 else:
                     reset_innings_vars()
                     prediction.initialize(game_settings['difficulty'])
                     schedule_message(f"{choice_text}, Starting Game...", 1500, PLAYING) # <<< Feedback
                     next_state = TOSS_RESULT # Stay until message finishes
    elif temp_toss_winner is None or temp_toss_sum is None:
        back_clicked, _ = draw_button("Back", 50, SCREEN_HEIGHT - 70, 100, 40, DARK_GRAY, LIGHT_GRAY, WHITE)
        if back_clicked: temp_toss_comp_num = None; temp_toss_sum = None; temp_toss_winner = None; return TOSS_NUMBER
    return next_state

def draw_toss_choice_screen():
    global game_settings, player_is_batting_now, temp_toss_winner
    screen.fill(BACKGROUND_COLOR)
    draw_text("You Won the Toss!", FONT_HEADING, GREEN, screen, SCREEN_WIDTH // 2, 150, center_x=True)
    draw_text("Choose your action:", FONT_NORMAL, BLACK, screen, SCREEN_WIDTH // 2, 250, center_x=True)
    btn_y = 330; btn_w = 120; btn_h = 50
    bat_clicked, _ = draw_button("Bat First", SCREEN_WIDTH // 2 - 150, btn_y, btn_w, btn_h, BLUE, LIGHT_BLUE, WHITE)
    bowl_clicked, _ = draw_button("Bowl First", SCREEN_WIDTH // 2 + 30, btn_y, btn_w, btn_h, BLUE, LIGHT_BLUE, WHITE)
    next_state = TOSS_CHOICE; message = None
    if bat_clicked: game_settings['player_bats_first'] = True; message = "You chose Bat First"; next_state = PLAYING
    if bowl_clicked: game_settings['player_bats_first'] = False; message = "You chose Bowl First"; next_state = PLAYING
    if next_state == PLAYING:
        player_is_batting_now = game_settings.get('player_bats_first')
        if player_is_batting_now is None: print("ERROR setting up play state!"); schedule_message("Setup Error!", 2000, SETUP); return TOSS_CHOICE
        else: reset_innings_vars(); prediction.initialize(game_settings['difficulty']); schedule_message(message + ", Starting Game...", 1500, next_state); return TOSS_CHOICE # State change via message
    back_clicked, _ = draw_button("Back", 50, SCREEN_HEIGHT - 70, 100, 40, DARK_GRAY, LIGHT_GRAY, WHITE)
    if back_clicked: game_settings['player_bats_first'] = None; temp_toss_winner = None; next_state = TOSS_RESULT
    return next_state

def draw_play_screen():
    global ball_result_timer, player_is_batting_now, current_player_input, current_computer_input
    global player_score, player_wickets, player_overs_bowled, computer_score, computer_wickets, computer_overs_bowled
    global input_locked_this_turn # <<< Read and modify lock state

    if player_is_batting_now is None: print("CRITICAL ERROR: draw_play_screen called but player_is_batting_now is None!"); schedule_message("Internal Error! Resetting.", 2500, WELCOME); reset_game_variables(); return PLAYING

    screen.fill(BACKGROUND_COLOR)
    batting_now_text = "Player" if player_is_batting_now else "Computer"; bowling_now_text = "Computer" if player_is_batting_now else "Player"
    current_score = player_score if player_is_batting_now else computer_score; current_wickets = player_wickets if player_is_batting_now else computer_wickets
    current_overs = player_overs_bowled if player_is_batting_now else computer_overs_bowled
    total_overs_allowed = float(game_settings.get('overs', 0.0)); total_wickets_allowed = game_settings.get('wickets', 1)

    # Scoreboard
    sb_h = 120; pygame.draw.rect(screen, DARK_GRAY, (0, 0, SCREEN_WIDTH, sb_h))
    draw_text(f"Innings {current_innings}", FONT_SCORE, WHITE, screen, SCREEN_WIDTH // 2, 25, center_x=True)
    draw_text(f"{batting_now_text}: {current_score}/{current_wickets}", FONT_SCORE, WHITE, screen, 50, 65)
    draw_text(f"Overs: {current_overs:.1f}/{total_overs_allowed:.0f}", FONT_SCORE, WHITE, screen, SCREEN_WIDTH - 250, 65)

    # Target/Runs Needed
    if target is not None:
        draw_text(f"Target: {target}", FONT_SCORE, GOLD, screen, SCREEN_WIDTH // 2, 65, center_x=True)
        runs_needed = max(0, target - current_score)
        needed_disp_text = f"{runs_needed} needed" if runs_needed > 0 else "Target Reached!"
        if total_overs_allowed > 0:
            balls_in_over = int(round((current_overs - int(current_overs)) * 10)) % 6; overs_completed = int(current_overs)
            total_balls = int(total_overs_allowed * 6); balls_bowled_total = overs_completed * 6 + balls_in_over
            if current_overs >= total_overs_allowed: balls_bowled_total = total_balls
            balls_rem = max(0, total_balls - balls_bowled_total); ball_str_rem = "ball" if balls_rem == 1 else "balls"
            show_balls = (current_wickets < total_wickets_allowed and not (target is not None and current_score >= target) and runs_needed > 0)
            balls_disp_text = f" from {balls_rem} {ball_str_rem}" if show_balls else ""
            combined_needed_text = needed_disp_text + balls_disp_text
        else: combined_needed_text = f"{runs_needed} runs needed"
        draw_text(combined_needed_text, FONT_SMALL, WHITE, screen, SCREEN_WIDTH // 2, 95, center_x=True)

    # Status Text
    draw_text(f"{batting_now_text} Batting | {bowling_now_text} Bowling", FONT_NORMAL, BLUE, screen, SCREEN_WIDTH // 2, sb_h + 30, center_x=True)

    # Previous Choices
    y_choices = sb_h + 80
    if current_player_input is not None: draw_text(f"Player Chose: {current_player_input}", FONT_NORMAL, BLACK, screen, 150, y_choices)
    if current_computer_input is not None: draw_text(f"CPU Chose: {current_computer_input}", FONT_NORMAL, BLACK, screen, SCREEN_WIDTH - 300, y_choices)

    # Result Timer
    res_y = y_choices + 60
    if ball_result_timer > 0:
        if pygame.time.get_ticks() < ball_result_timer:
            res_col = RED if "OUT" in last_ball_result else GREEN; draw_text(last_ball_result, FONT_HEADING, res_col, screen, SCREEN_WIDTH // 2, res_y, center_x=True)
        else:
            ball_result_timer = 0 # Reset timer
            input_locked_this_turn = False # <<< Unlock input when result disappears

    # Input Pad / Prompt
    if ball_result_timer == 0:
        # Reset lock just in case it wasn't reset by timer check (e.g., first ball)
        input_locked_this_turn = False # <<< Ensure unlocked before prompt
        prompt = f"Your Turn: {'Bat' if player_is_batting_now else 'Bowl'} (1-10)"; draw_text(prompt, FONT_NORMAL, BLACK, screen, SCREEN_WIDTH//2, INPUT_PAD_Y_PLAY - 40, center_x=True)
        draw_text("Click or Press Number Key (1-9, 0 for 10)", FONT_SMALL, DARK_GRAY, screen, SCREEN_WIDTH // 2, INPUT_PAD_Y_PLAY - 15, center_x=True)
        for i, btn_data in enumerate(input_buttons_data):
            row=i//INPUT_PAD_COLS; col=i%INPUT_PAD_COLS; bx=INPUT_PAD_X_START+col*(INPUT_BTN_SIZE+INPUT_BTN_GAP); by=INPUT_PAD_Y_PLAY+row*(INPUT_BTN_SIZE+INPUT_BTN_GAP)
            num_clicked, _ = draw_button(str(btn_data['num']), bx, by, INPUT_BTN_SIZE, INPUT_BTN_SIZE, BLUE, LIGHT_BLUE, WHITE)
            if num_clicked:
                 if not input_locked_this_turn: # Double check lock before processing click
                     process_ball(btn_data['num'])
                     # input_locked_this_turn = True # process_ball now handles locking
                     break # Exit pad loop after click
    elif input_locked_this_turn: # If result timer active but lock somehow still true (shouldn't happen often)
         # Optionally display processing message if needed, but result timer usually covers this
         pass

    return PLAYING

def draw_innings_break_screen():
    global target, player_is_batting_now, current_innings
    screen.fill(BACKGROUND_COLOR)
    draw_text("Innings Break", FONT_HEADING, BLUE, screen, SCREEN_WIDTH // 2, 100, center_x=True)
    draw_text("Innings 1 Score:", FONT_NORMAL, BLACK, screen, SCREEN_WIDTH // 2, 200, center_x=True)
    inn1_score=None; inn1_wickets=None; inn1_overs=None; inn1_team="Error"; pbf = game_settings.get('player_bats_first'); current_target = None
    if pbf is not None:
         inn1_score = player_score if pbf else computer_score; inn1_wickets = player_wickets if pbf else computer_wickets
         inn1_overs = player_overs_bowled if pbf else computer_overs_bowled; inn1_team = "Player" if pbf else "Computer"
         draw_text(f"{inn1_team}: {inn1_score}/{inn1_wickets} ({inn1_overs:.1f} Ov)", FONT_SCORE, BLACK, screen, SCREEN_WIDTH//2, 250, center_x=True)
         current_target = inn1_score + 1; target = current_target
         draw_text(f"Target for Innings 2: {target}", FONT_SCORE, RED, screen, SCREEN_WIDTH // 2, 350, center_x=True)
    else: draw_text("Error determining scores!", FONT_NORMAL, RED, screen, SCREEN_WIDTH // 2, 250, center_x=True)

    continue_y = 450; next_state = INNINGS_BREAK
    if current_target is not None:
         continue_clicked, _ = draw_button("Start Innings 2", SCREEN_WIDTH // 2 - 100, continue_y, 200, 50, GREEN, LIGHT_BLUE, WHITE)
         if continue_clicked:
            current_innings = 2; reset_innings_vars(); current_pbf = game_settings.get('player_bats_first')
            if current_pbf is None: print("Error switching innings!"); next_state = SETUP; reset_game_variables()
            else:
                player_is_batting_now = not current_pbf
                schedule_message("Starting Innings 2...", 1500, PLAYING) # <<< Feedback
                next_state = INNINGS_BREAK # Stay until message finishes
    else:
         back_clicked, _ = draw_button("Return to Setup", SCREEN_WIDTH//2 - 100, continue_y, 200, 50, RED, LIGHT_BLUE, WHITE)
         if back_clicked: reset_game_variables(); next_state = SETUP
    return next_state

def draw_game_over_screen():
    global current_innings, player_score, player_wickets, player_overs_bowled, computer_score, computer_wickets, computer_overs_bowled, target, player_is_batting_now, game_settings
    screen.fill(BACKGROUND_COLOR)
    draw_text("Game Over", FONT_HEADING, BLUE, screen, SCREEN_WIDTH // 2, 80, center_x=True)
    winner = None; margin_text = ""; pbf = game_settings.get('player_bats_first'); current_target = target
    if pbf is None or current_target is None:
        print(f"Error in game over: pbf={pbf}, target={current_target}"); winner = "ERROR"; margin_text = "(State Error)"
        inn1_score = max(player_score, computer_score); inn2_score = min(player_score, computer_score); inn2_wickets = 0
    else:
        inn1_score = player_score if pbf else computer_score; inn2_score = computer_score if pbf else player_score
        inn2_wickets = computer_wickets if pbf else player_wickets; wickets_allowed = game_settings.get('wickets', 1)
        if inn2_score >= current_target: winner = "Computer" if pbf else "Player"; wickets_left = max(0, wickets_allowed - inn2_wickets); margin_text = f"by {wickets_left} wicket{'s' if wickets_left != 1 else ''}"
        elif inn2_score < inn1_score: winner = "Player" if pbf else "Computer"; runs_margin = inn1_score - inn2_score; margin_text = f"by {runs_margin} run{'s' if runs_margin != 1 else ''}"
        else: winner = "TIE"

    result_color = GREEN if winner == "Player" else (RED if winner == "Computer" else (GOLD if winner == "TIE" else BLACK))
    if winner == "TIE": draw_text("It's a Tie!", FONT_HEADING, result_color, screen, SCREEN_WIDTH//2, 180, center_x=True)
    elif winner == "ERROR": draw_text("Game Over (Error)", FONT_HEADING, result_color, screen, SCREEN_WIDTH//2, 180, center_x=True)
    else: draw_text(f"{winner} Wins!", FONT_HEADING, result_color, screen, SCREEN_WIDTH // 2, 180, center_x=True); draw_text(margin_text, FONT_NORMAL, BLACK, screen, SCREEN_WIDTH // 2, 230, center_x=True)

    y_pos = 300; draw_text("--- Final Scores ---", FONT_NORMAL, DARK_GRAY, screen, SCREEN_WIDTH//2, y_pos, center_x=True); y_pos += 40
    if pbf is not None:
        inn1_team = "Player" if pbf else "Computer"; inn1_wickets_final = player_wickets if pbf else computer_wickets; inn1_overs_final = player_overs_bowled if pbf else computer_overs_bowled
        inn2_team = "Computer" if pbf else "Player"; inn2_score_final = computer_score if pbf else player_score; inn2_wickets_final = computer_wickets if pbf else player_wickets; inn2_overs_final = computer_overs_bowled if pbf else player_overs_bowled
        draw_text(f"{inn1_team} (Inn 1): {inn1_score}/{inn1_wickets_final} ({inn1_overs_final:.1f} Ov)", FONT_SCORE, BLACK, screen, SCREEN_WIDTH//2, y_pos, center_x=True); y_pos += 40
        draw_text(f"{inn2_team} (Inn 2): {inn2_score_final}/{inn2_wickets_final} ({inn2_overs_final:.1f} Ov)", FONT_SCORE, BLACK, screen, SCREEN_WIDTH//2, y_pos, center_x=True); y_pos += 40
        if current_target is not None: draw_text(f"(Target: {current_target})", FONT_SMALL, DARK_GRAY, screen, SCREEN_WIDTH//2, y_pos, center_x=True)
    else:
        draw_text(f"Player Score : {player_score}/{player_wickets} ({player_overs_bowled:.1f})", FONT_SCORE, BLACK, screen, SCREEN_WIDTH//2, y_pos, center_x=True); y_pos += 40
        draw_text(f"CPU Score    : {computer_score}/{computer_wickets} ({computer_overs_bowled:.1f})", FONT_SCORE, BLACK, screen, SCREEN_WIDTH//2, y_pos, center_x=True); y_pos += 40
        draw_text("(Error determining innings)", FONT_SMALL, RED, screen, SCREEN_WIDTH//2, y_pos, center_x=True)

    play_again_clicked, _ = draw_button("Play Again", SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT - 100, 120, 50, BLUE, LIGHT_BLUE, WHITE)
    quit_clicked, _ = draw_button("Quit Game", SCREEN_WIDTH // 2 + 30, SCREEN_HEIGHT - 100, 120, 50, DARK_GRAY, LIGHT_GRAY, WHITE)
    next_state = GAME_OVER
    if play_again_clicked: reset_game_variables(); next_state = WELCOME
    if quit_clicked: pygame.quit(); reset.reset(); sys.exit()
    return next_state


# --- Main Game Loop ---
print("--- Entering Main Loop ---")
running = True
while running:
    current_frame_state = game_state # State at the start of this frame's logic

    # --- Event Handling ---
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT: print("Quit event received. Exiting."); reset.reset() ;running = False
        if event.type == pygame.KEYDOWN:
            # --- Keyboard Input Handling ---
            if not input_locked_this_turn: # Only process if not locked
                num_pressed = None
                if event.key >= pygame.K_1 and event.key <= pygame.K_9: num_pressed = event.key - pygame.K_0
                elif event.key == pygame.K_0: num_pressed = 10

                if num_pressed is not None:
                    # Process based on the state *at the start of the frame*
                    if current_frame_state == PLAYING:
                        print(f"Keyboard Input (Play): {num_pressed}")
                        process_ball(num_pressed)
                    elif current_frame_state == TOSS_NUMBER:
                        print(f"Keyboard Input (Toss): {num_pressed}")
                        process_toss_number(num_pressed)
                    # Keyboard input handled, state might have changed via schedule_message

    if not running: break # Exit loop immediately if running flag is false

    # --- State Logic and Drawing ---
    try:
        # 1. Check Message Timer FIRST (might change global game_state)
        if message_display_time > 0:
            check_scheduled_message() # Updates global 'game_state' if timer expired
            # IMPORTANT: After check, use the potentially updated global game_state
            current_frame_state = game_state

        # 2. Draw Based on Current State (or Message)
        if message_display_time > 0: # Draw message if timer is STILL active
            screen.fill(BACKGROUND_COLOR)
            draw_text(message_text, FONT_HEADING, BLUE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, center_x=True, center_y=True)
            # State remains as is until timer expires (handled by check_scheduled_message)
            next_state_output = current_frame_state
        else:
            # No active message, draw the normal state screen
            # The draw function returns the state it *wants* to transition to
            if current_frame_state == WELCOME: next_state_output = draw_welcome_screen()
            elif current_frame_state == SETUP: next_state_output = draw_setup_screen()
            elif current_frame_state == TOSS_CALL: next_state_output = draw_toss_call_screen()
            elif current_frame_state == TOSS_NUMBER: next_state_output = draw_toss_number_screen()
            elif current_frame_state == TOSS_RESULT: next_state_output = draw_toss_result_screen()
            elif current_frame_state == TOSS_CHOICE: next_state_output = draw_toss_choice_screen()
            elif current_frame_state == PLAYING: next_state_output = draw_play_screen()
            elif current_frame_state == INNINGS_BREAK: next_state_output = draw_innings_break_screen()
            elif current_frame_state == GAME_OVER: next_state_output = draw_game_over_screen()
            else:
                print(f"Error: Unknown game state '{current_frame_state}'")
                next_state_output = WELCOME; reset_game_variables()

            # Update the global game state ONLY with the output from the draw function
            # IF no message timer was started *during* the draw function call
            # (check_scheduled_message handles state change if timer expires)
            if message_display_time == 0: # Check if message timer is still inactive
                 game_state = next_state_output


    except Exception as e:
        # General error catching during main loop processing
        print(f"\n!!! UNCAUGHT ERROR during game loop (state: {current_frame_state}) !!!"); print(f"Error: {e}"); traceback.print_exc()
        try: schedule_message(f"Error: {e}. Resetting.", 4000, WELCOME); game_state = WELCOME
        except Exception as e2: print(f"FATAL ERROR during error recovery: {e2}"); running = False

    # --- Update Display ---
    pygame.display.flip()

    # --- Frame Rate Control ---
    clock.tick(FPS)

# --- Quit Pygame ---
print("Exiting Pygame.")
reset.reset()
pygame.quit()
sys.exit()
