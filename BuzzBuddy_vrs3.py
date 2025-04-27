import pygame
import sys
import random
import math

# --- Constants ---
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 200, 0) # Status bar color / Flower Stem
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0) # Status bar color / Flower Center
GRAY = (200, 200, 200)
LIGHT_BLUE = (173, 216, 230) # Status bar color / Flappy background
BEE_YELLOW = (255, 223, 0)
WING_COLOR = (220, 220, 255)
BUTTON_COLOR_INACTIVE = (180, 180, 180)
BUTTON_COLOR_ACTIVE = (150, 150, 150)
XP_BAR_COLOR = (148, 0, 211) # Dark Violet for XP bar
# Flower Petal Colors (Examples)
PETAL_COLOR_1 = (255, 105, 180) # Pink
PETAL_COLOR_2 = (255, 0, 0)     # Red
PETAL_COLOR_3 = (138, 43, 226)  # BlueViolet

# --- Honeycomb Background Constants ---
HONEYCOMB_FILL = (255, 193, 7)
HONEYCOMB_OUTLINE = (217, 160, 0)
HEX_RADIUS = 30

# --- Flappy Game Constants ---
FLOWER_STEM_COLOR = GREEN
FLOWER_CENTER_COLOR = YELLOW
FLOWER_PETAL_COLORS = [PETAL_COLOR_1, PETAL_COLOR_2, PETAL_COLOR_3]
STEM_WIDTH = 15
FLOWER_HEAD_RADIUS = 35
PETAL_RADIUS = 15
FLOWER_GAP = 180
OBSTACLE_FREQUENCY = 1500
OBSTACLE_SPEED = 3
GRAVITY = 0.25
JUMP_STRENGTH = -6
FLAPPY_BEE_SCALE = 0.6

# --- Bee Facts ---
BEE_FACTS = [
    "Honey bees fly at 15 miles per hour.",
    "Honey bees' wings stroke 11,400 times per minute.",
    "A honey bee visits 50 to 100 flowers during one collection trip.",
    "Bees have 5 eyes.",
    "Male bees (drones) don't have stingers.",
    "Honey never spoils.",
    "A single bee colony can produce 60 to 100 pounds of honey per year.",
    "Bees communicate through dancing (the 'waggle dance').",
    "The queen bee can live for several years.",
    "Bees are responsible for pollinating about 80% of all flowering plants.",
    "A bee produces only about 1/12th of a teaspoon of honey in its lifetime.",
]

# --- Game States / Rooms ---
ROOMS = ["Pollen Storage", "Bathroom", "Nest"]
current_room_name = ROOMS[2] # Start in Nest

# --- Game Modes ---
MODE_PET = "pet"
MODE_FLAPPY = "flappy"
game_mode = MODE_PET

# --- Game Variables ---
pet_cleanliness_level = 100
pet_hunger_level = 100
pet_happy_level = 100
max_level = 100

last_stat_decrease_time = 0
stat_decrease_interval = 5000 # 5 seconds

# --- XP and Leveling Variables ---
bee_level = 1 # Start at level 1 (1 bee)
max_bee_level = 3
xp_current = 0
# XP needed to reach level 2, then level 3
xp_levels = {
    1: 50,  # XP needed to reach level 2 from level 1
    2: 100, # XP needed to reach level 3 from level 2
    # Level 3 is max, no more XP needed defined here
}
xp_next_level = xp_levels.get(bee_level, float('inf')) # Get XP for next level, infinity if max

# --- Pygame Setup ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("BuzzBuddy Pet")
clock = pygame.time.Clock()

# --- Font Loading ---
FONT_NAME = "hangyaboly.ttf" # <<<--- MAKE SURE THIS MATCHES YOUR FONT FILE NAME
try:
    # Adjust sizes as needed for the new font's appearance
    font_large = pygame.font.Font(FONT_NAME, 55)
    font_medium = pygame.font.Font(FONT_NAME, 40)
    font_small = pygame.font.Font(FONT_NAME, 30)
    font_game_score = pygame.font.Font(FONT_NAME, 60)
    print(f"Successfully loaded font: {FONT_NAME}")
except pygame.error as e:
    print(f"Error loading font '{FONT_NAME}': {e}")
    print("Using default Pygame font instead.")
    # Fallback to default font if custom font fails
    font_large = pygame.font.Font(None, 40)
    font_medium = pygame.font.Font(None, 32)
    font_small = pygame.font.Font(None, 24)
    font_game_score = pygame.font.Font(None, 50)
# --- End Font Loading ---

# --- Brush Creation ---
BRUSH_WIDTH = 35
BRUSH_HEIGHT = 45
BRUSH_HANDLE_HEIGHT = 30
BRUSH_HANDLE_COLOR = (139, 69, 19) # Saddle Brown
BRUSH_BRISTLE_COLOR = (210, 180, 140) # Tan

def create_brush_surface(width, height, handle_height, handle_color, bristle_color):
    """Creates a Pygame Surface with a simple brush drawn on it."""
    brush_surf = pygame.Surface((width, height), pygame.SRCALPHA) # Use SRCALPHA for transparency
    # Draw Handle
    handle_rect = pygame.Rect(0, 0, width, handle_height)
    pygame.draw.rect(brush_surf, handle_color, handle_rect)
    pygame.draw.rect(brush_surf, BLACK, handle_rect, 1) # Outline

    # Draw Bristles (simple lines)
    bristle_y_start = handle_height
    num_bristles = 10
    bristle_spacing = width / (num_bristles + 1)
    for i in range(num_bristles):
        bristle_x = int(bristle_spacing * (i + 1))
        pygame.draw.line(brush_surf, bristle_color, (bristle_x, bristle_y_start), (bristle_x, height), 2)

    return brush_surf

# Create the brush surface instance
brush_image = create_brush_surface(
    BRUSH_WIDTH, BRUSH_HEIGHT, BRUSH_HANDLE_HEIGHT,
    BRUSH_HANDLE_COLOR, BRUSH_BRISTLE_COLOR
)
brush_rect = brush_image.get_rect()
show_custom_cursor = False # Flag to control custom cursor visibility

# --- Pet Representation ---
pet_center_x = SCREEN_WIDTH // 2
pet_center_y = SCREEN_HEIGHT // 2 - 30
pet_body_width = 80
pet_body_height = 60
eye_radius_outer = 12
pupil_radius = 6
max_pupil_offset = eye_radius_outer - pupil_radius
bee_spacing_offset = pet_body_width * 0.7 # Horizontal distance between multiple bees

# --- UI Elements ---
# Status Bars
bar_width = 115
bar_height = 20
bar_y = 2
bar_spacing = 80
cleanliness_bar_x = (SCREEN_WIDTH // 2) - bar_width - bar_spacing
honey_bar_x = SCREEN_WIDTH // 2 - (bar_width // 2)
happy_bar_x = (SCREEN_WIDTH // 2) + bar_spacing
cleanliness_bar_rect = pygame.Rect(cleanliness_bar_x, bar_y, bar_width, bar_height)
honey_bar_rect = pygame.Rect(honey_bar_x, bar_y, bar_width, bar_height)
happy_bar_rect = pygame.Rect(happy_bar_x, bar_y, bar_width, bar_height)

# XP Bar (Positioned below the central bee spot)
xp_bar_width = 125
xp_bar_height = 10
xp_bar_y = pet_center_y + pet_body_height // 2 + 5 # Below bee
xp_bar_x = pet_center_x - xp_bar_width // 2
xp_bar_rect = pygame.Rect(xp_bar_x, xp_bar_y, xp_bar_width, xp_bar_height)

# Titles
title_y = bar_y + bar_height + 50
room_name_y = title_y + 30

# --- Room Specific Buttons (Position relative to original center) ---
button_y_offset = pet_body_height // 2 + 80 # Vertical offset from original bee center

# Nest "Play Game" Button
play_btn_width = 150
play_btn_height = 50
play_btn_rect = pygame.Rect(0, 0, play_btn_width, play_btn_height)
play_btn_rect.center = (pet_center_x, pet_center_y + button_y_offset)
play_text_surf = font_medium.render("Play!", True, BLACK) # Re-render text with new font
play_text_rect = play_text_surf.get_rect(center=play_btn_rect.center)

# Honey Storage "Feed" Button
feed_btn_width = 150
feed_btn_height = 50
feed_btn_rect = pygame.Rect(0, 0, feed_btn_width, feed_btn_height)
feed_btn_rect.center = (pet_center_x, pet_center_y + button_y_offset) # Use same offset
feed_text_surf = font_medium.render("Make", True, BLACK) # Re-render text with new font
feed_text_rect = feed_text_surf.get_rect(center=feed_btn_rect.center)

# Room Navigation Buttons
nav_btn_width = 110
nav_btn_height = 40
nav_btn_y = SCREEN_HEIGHT - nav_btn_height - 15
nav_btn_spacing = (SCREEN_WIDTH - (nav_btn_width * 3)) // 4
bathroom_btn_rect = pygame.Rect(nav_btn_spacing, nav_btn_y, nav_btn_width, nav_btn_height)
honey_storage_btn_rect = pygame.Rect(nav_btn_spacing * 2 + nav_btn_width, nav_btn_y, nav_btn_width, nav_btn_height)
nest_btn_rect = pygame.Rect(nav_btn_spacing * 3 + nav_btn_width * 2, nav_btn_y, nav_btn_width, nav_btn_height)
# Re-render navigation text with new font
bathroom_text_surf = font_medium.render("Bathroom", True, BLACK)
honey_storage_text_surf = font_medium.render("Pollen", True, BLACK)
nest_text_surf = font_medium.render("Nest", True, BLACK)
bathroom_text_rect = bathroom_text_surf.get_rect(center=bathroom_btn_rect.center)
honey_storage_text_rect = honey_storage_text_surf.get_rect(center=honey_storage_btn_rect.center)
nest_text_rect = nest_text_surf.get_rect(center=nest_btn_rect.center)


# --- Helper Function for Drawing Text ---
def draw_text(text, font_to_use, color, surface, x, y, center=False):
    textobj = font_to_use.render(text, True, color)
    textrect = textobj.get_rect()
    if center:
        textrect.center = (x, y)
    else:
        textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

# --- Helper Function to Draw Status/XP Bar ---
def draw_generic_bar(surface, rect, color, level, max_level, label="", show_percent=False):
    # Background
    pygame.draw.rect(surface, GRAY, rect)
    # Fill
    fill_width = 0
    # Ensure max_level is not zero before division
    if max_level > 0 and max_level != float('inf'):
        fill_width = int((level / max_level) * rect.width)
    elif max_level == float('inf'): # Handle case where max level is infinity (already maxed)
        fill_width = rect.width if level > 0 else 0 # Fill completely if maxed and has some level
    elif level >= max_level: # Handle reaching exactly max level if it's not infinity
         fill_width = rect.width

    if fill_width > 0:
        # Ensure fill_width doesn't exceed rect.width
        fill_width = min(fill_width, rect.width)
        fill_rect = pygame.Rect(rect.left, rect.top, fill_width, rect.height)
        pygame.draw.rect(surface, color, fill_rect)
    # Outline
    pygame.draw.rect(surface, BLACK, rect, 2)
    # Text Label
    display_text = ""
    if label:
        display_text = label
    elif show_percent:
         display_text = f"{int(level)}%"
    elif max_level != float('inf'): # For XP bar, show level/max
        display_text = f"{int(level)}/{int(max_level)} XP"
    else: # Max level reached for XP
        display_text = "MAX LEVEL"

    if display_text:
        # Use font_small for the bar labels
        draw_text(display_text, font_small, BLACK, surface, rect.centerx, rect.bottom + 10, center=True) # Adjusted spacing slightly


# --- Helper Function to Draw a Hexagon ---
def draw_hexagon(surface, color_fill, color_outline, center_x, center_y, radius):
    points = []
    for i in range(6):
        angle_deg = 60 * i - 30
        angle_rad = math.pi / 180 * angle_deg
        x = center_x + radius * math.cos(angle_rad)
        y = center_y + radius * math.sin(angle_rad)
        points.append((int(x), int(y)))
    pygame.draw.polygon(surface, color_fill, points)
    pygame.draw.polygon(surface, color_outline, points, 2)

# --- Helper Function to Draw Bee (With scaling) ---
def draw_bee(surface, center_x, center_y, mouse_pos, scale=1.0):
    # Scale dimensions
    scaled_body_width = int(pet_body_width * scale)
    scaled_body_height = int(pet_body_height * scale)
    scaled_eye_radius_outer = int(eye_radius_outer * scale)
    scaled_pupil_radius = int(pupil_radius * scale)
    scaled_max_pupil_offset = scaled_eye_radius_outer - scaled_pupil_radius

    # Ensure minimum size for small scales
    scaled_body_width = max(1, scaled_body_width)
    scaled_body_height = max(1, scaled_body_height)
    scaled_eye_radius_outer = max(1, scaled_eye_radius_outer)
    scaled_pupil_radius = max(1, scaled_pupil_radius)

    body_rect = pygame.Rect(0, 0, scaled_body_width, scaled_body_height)
    body_rect.center = (center_x, center_y)

    # --- Wings ---
    wing_width = int(scaled_body_width * 0.40)
    wing_height = int(scaled_body_height * 0.60)
    wing_offset_x = int(scaled_body_width * 0.28)
    wing_offset_y = int(scaled_body_height * 0.48)
    left_wing_rect = pygame.Rect(0, 0, wing_width, wing_height)
    left_wing_rect.center = (center_x - wing_offset_x, center_y - wing_offset_y)
    pygame.draw.ellipse(surface, WING_COLOR, left_wing_rect)
    pygame.draw.ellipse(surface, BLACK, left_wing_rect, 1)
    right_wing_rect = pygame.Rect(0, 0, wing_width, wing_height)
    right_wing_rect.center = (center_x + wing_offset_x, center_y - wing_offset_y)
    pygame.draw.ellipse(surface, WING_COLOR, right_wing_rect)
    pygame.draw.ellipse(surface, BLACK, right_wing_rect, 1)

    # --- Antennae ---
    # (Could add antennae drawing here if desired)

    # --- Body ---
    pygame.draw.ellipse(surface, BEE_YELLOW, body_rect)

    # --- Stripes ---
    stripe_height = int(scaled_body_height * 0.90)
    stripe_y = body_rect.top + (scaled_body_height - stripe_height) // 2
    stripe_width = max(1, int(10 * scale))
    stripe_start_x = body_rect.centerx - stripe_width * 1.5
    stripe1_rect = pygame.Rect(stripe_start_x, stripe_y, stripe_width, stripe_height)
    pygame.draw.rect(surface, BLACK, stripe1_rect)
    stripe2_rect = pygame.Rect(stripe_start_x + stripe_width * 2, stripe_y, stripe_width, stripe_height)
    pygame.draw.rect(surface, BLACK, stripe2_rect)

    # --- Stinger ---
    stinger_size = max(1, int(5 * scale))
    stinger_base_x = body_rect.left + stinger_size * 0.5
    stinger_point1 = (body_rect.left, body_rect.centery)
    stinger_point2 = (stinger_base_x, body_rect.centery - stinger_size // 2)
    stinger_point3 = (stinger_base_x, body_rect.centery + stinger_size // 2)
    pygame.draw.polygon(surface, BLACK, [stinger_point1, stinger_point2, stinger_point3])

    # --- Body Outline ---
    pygame.draw.ellipse(surface, BLACK, body_rect, max(1, int(2*scale)))

    # --- Eye Drawing ---
    eye_base_x = center_x + scaled_body_width * 0.25
    eye_base_y = center_y - scaled_body_height * 0.10

    pygame.draw.circle(surface, WHITE, (int(eye_base_x), int(eye_base_y)), scaled_eye_radius_outer)
    pygame.draw.circle(surface, BLACK, (int(eye_base_x), int(eye_base_y)), scaled_eye_radius_outer, 1)

    # Pupil position (tracks mouse only for full-size bee)
    pupil_x = eye_base_x
    pupil_y = eye_base_y
    if scale == 1.0: # Only do tracking for full size bee
        dx = mouse_pos[0] - eye_base_x
        dy = mouse_pos[1] - eye_base_y
        distance = math.hypot(dx, dy)
        if distance >= 1: # Avoid division by zero
            norm_dx = dx / distance
            norm_dy = dy / distance
            pupil_offset_x = norm_dx * scaled_max_pupil_offset
            pupil_offset_y = norm_dy * scaled_max_pupil_offset
            pupil_x = eye_base_x + pupil_offset_x
            pupil_y = eye_base_y + pupil_offset_y
        else: # Mouse is exactly on the eye center
            pupil_x = eye_base_x
            pupil_y = eye_base_y

    pygame.draw.circle(surface, BLACK, (int(pupil_x), int(pupil_y)), scaled_pupil_radius)

    # --- Eye Highlight ---
    highlight_radius = max(1, int(2 * scale))
    highlight_x_offset = scaled_pupil_radius * 0.4
    highlight_y_offset = -scaled_pupil_radius * 0.4
    highlight_x = pupil_x + highlight_x_offset
    highlight_y = pupil_y + highlight_y_offset
    pygame.draw.circle(surface, WHITE, (int(highlight_x), int(highlight_y)), highlight_radius)

    # Return the body rect for collision detection
    return body_rect


# --- Flappy Bird Game Function --- <--- MODIFIED FUNCTION
def run_flappy_game(surface, game_clock):
    bee_y = SCREEN_HEIGHT // 2
    bee_velocity = 0
    bee_x = SCREEN_WIDTH // 4 # Keep bee horizontally fixed

    flowers = [] # List to store flower rects [top_stem_rect, bottom_stem_rect, scored, petal_color_index]
    obstacle_timer = pygame.USEREVENT + 1
    pygame.time.set_timer(obstacle_timer, OBSTACLE_FREQUENCY)

    score = 0
    game_active = True
    game_over_message_shown = False
    petal_color_index = 0 # To cycle through petal colors
    random_fact = "" # Variable to store the selected fact

    while True: # Loop until player exits game over screen
        # --- Event Handling (Flappy) ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and game_active:
                    bee_velocity = JUMP_STRENGTH # Jump!
                if event.key == pygame.K_SPACE and not game_active:
                    return score # Exit mini-game and return score
            if event.type == pygame.MOUSEBUTTONDOWN and not game_active:
                 return score # Exit mini-game and return score
            if event.type == obstacle_timer and game_active:
                # Create new flowers
                gap_top_y = random.randint(FLOWER_HEAD_RADIUS + 50, SCREEN_HEIGHT - FLOWER_HEAD_RADIUS - 50 - FLOWER_GAP)
                gap_bottom_y = gap_top_y + FLOWER_GAP
                top_stem = pygame.Rect(SCREEN_WIDTH + (STEM_WIDTH//2), 0, STEM_WIDTH, gap_top_y)
                bottom_stem = pygame.Rect(SCREEN_WIDTH + (STEM_WIDTH//2), gap_bottom_y, STEM_WIDTH, SCREEN_HEIGHT - gap_bottom_y)
                flowers.append([top_stem, bottom_stem, False, petal_color_index])
                petal_color_index = (petal_color_index + 1) % len(FLOWER_PETAL_COLORS)

        # --- Game Logic (Flappy) ---
        bee_rect = pygame.Rect(0,0,0,0) # Initialize bee_rect
        if game_active:
            bee_velocity += GRAVITY
            bee_y += bee_velocity
            temp_bee_rect = pygame.Rect(0, 0, int(pet_body_width * FLAPPY_BEE_SCALE), int(pet_body_height * FLAPPY_BEE_SCALE))
            temp_bee_rect.center = (bee_x, int(bee_y))
            bee_rect = temp_bee_rect # Assign the calculated rect

            flowers_to_remove = []
            collision = False # Flag for collision detection
            for i, flower_pair in enumerate(flowers):
                flower_pair[0].x -= OBSTACLE_SPEED
                flower_pair[1].x -= OBSTACLE_SPEED
                if not flower_pair[2] and flower_pair[0].centerx < bee_x:
                    score += 1
                    flower_pair[2] = True
                # Check collision with stems
                if bee_rect.colliderect(flower_pair[0]) or bee_rect.colliderect(flower_pair[1]):
                    collision = True
                # Check collision with flower heads (circles) - More accurate
                top_flower_center_x = flower_pair[0].centerx
                top_flower_center_y = flower_pair[0].bottom
                bottom_flower_center_x = flower_pair[1].centerx
                bottom_flower_center_y = flower_pair[1].top
                # Simple circle collision check (distance between centers <= sum of radii)
                if math.hypot(bee_rect.centerx - top_flower_center_x, bee_rect.centery - top_flower_center_y) <= (bee_rect.width / 2 + FLOWER_HEAD_RADIUS):
                    collision = True
                if math.hypot(bee_rect.centerx - bottom_flower_center_x, bee_rect.centery - bottom_flower_center_y) <= (bee_rect.width / 2 + FLOWER_HEAD_RADIUS):
                    collision = True

                if flower_pair[0].right < -FLOWER_HEAD_RADIUS:
                    flowers_to_remove.append(flower_pair)

            for flower_pair in flowers_to_remove:
                flowers.remove(flower_pair)

            # Check boundary collision
            if bee_rect.top <= 0 or bee_rect.bottom >= SCREEN_HEIGHT:
                collision = True

            # --- Handle Game Over ---
            if collision:
                game_active = False
                # Select random fact ONCE when game ends
                if not game_over_message_shown: # Ensure fact is chosen only once
                    random_fact = random.choice(BEE_FACTS)
                    print(f"Game Over! Final Score: {score}")
                    game_over_message_shown = True # Mark game over message as shown


        # --- Drawing (Flappy) ---
        surface.fill(LIGHT_BLUE)
        num_petals = 6
        for top_stem, bottom_stem, _, p_color_index in flowers:
            petal_color = FLOWER_PETAL_COLORS[p_color_index]
            pygame.draw.rect(surface, FLOWER_STEM_COLOR, top_stem)
            pygame.draw.rect(surface, FLOWER_STEM_COLOR, bottom_stem)
            top_flower_center_x = top_stem.centerx
            top_flower_center_y = top_stem.bottom
            for i in range(num_petals):
                angle = (360 / num_petals) * i
                rad_angle = math.radians(angle)
                petal_x = top_flower_center_x + (FLOWER_HEAD_RADIUS - PETAL_RADIUS) * math.cos(rad_angle)
                petal_y = top_flower_center_y + (FLOWER_HEAD_RADIUS - PETAL_RADIUS) * math.sin(rad_angle)
                pygame.draw.circle(surface, petal_color, (int(petal_x), int(petal_y)), PETAL_RADIUS)
            pygame.draw.circle(surface, FLOWER_CENTER_COLOR, (top_flower_center_x, top_flower_center_y), PETAL_RADIUS)
            bottom_flower_center_x = bottom_stem.centerx
            bottom_flower_center_y = bottom_stem.top
            for i in range(num_petals):
                angle = (360 / num_petals) * i
                rad_angle = math.radians(angle)
                petal_x = bottom_flower_center_x + (FLOWER_HEAD_RADIUS - PETAL_RADIUS) * math.cos(rad_angle)
                petal_y = bottom_flower_center_y + (FLOWER_HEAD_RADIUS - PETAL_RADIUS) * math.sin(rad_angle)
                pygame.draw.circle(surface, petal_color, (int(petal_x), int(petal_y)), PETAL_RADIUS)
            pygame.draw.circle(surface, FLOWER_CENTER_COLOR, (bottom_flower_center_x, bottom_flower_center_y), PETAL_RADIUS)

        # Draw the bee only if game is active or just ended (to avoid drawing over game over text immediately)
        if game_active or not game_over_message_shown:
             draw_bee(surface, bee_x, int(bee_y), (0,0), scale=FLAPPY_BEE_SCALE) # Use (0,0) for mouse pos as it's not needed here

        # Use font_game_score for the score display (Keeping this white for contrast with flowers)
        draw_text(f"Score: {score}", font_game_score, WHITE, surface, SCREEN_WIDTH // 2, 50, center=True)

        # Game Over Message
        if not game_active:
            # Draw standard game over text using the loaded fonts
            # Keep "Game Over!" red for emphasis
            draw_text("Game Over!", font_large, RED, surface, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60, center=True)
            # Change score text to BLACK
            draw_text(f"Final Score: {score}", font_medium, BLACK, surface, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20, center=True) # <<< MODIFIED

            # --- Draw the Random Bee Fact ---
            line_y = SCREEN_HEIGHT // 2 + 20 # Adjusted Starting Y for fact text
            if random_fact: # Only draw if a fact was selected
                # Simple text wrapping
                fact_rect = pygame.Rect(20, line_y, SCREEN_WIDTH - 40, 100) # Area for fact text
                words = random_fact.split(' ')
                lines = []
                current_line = ""
                for word in words:
                    test_line = current_line + word + " "
                    # Use font_small for rendering test
                    test_surf = font_small.render(test_line, True, BLACK) # <<< MODIFIED (Test render color doesn't matter much, but keep consistent)
                    if test_surf.get_width() < fact_rect.width:
                        current_line = test_line
                    else:
                        lines.append(current_line)
                        current_line = word + " "
                lines.append(current_line) # Add the last line

                # Draw the wrapped lines using font_small and BLACK color
                for line in lines:
                    draw_text(line.strip(), font_small, BLACK, surface, fact_rect.centerx, line_y, center=True) # <<< MODIFIED
                    line_y += font_small.get_height() + 2 # Move down for next line (using original spacing from v3)

            # Draw exit instruction below the fact using font_small and BLACK color
            draw_text("Click or Space to Exit", font_small, BLACK, surface, SCREEN_WIDTH // 2, line_y + 10, center=True) # <<< MODIFIED

        pygame.display.flip()
        game_clock.tick(60)
# --- End Modified Function ---


# --- Main Game Loop ---
running = True
# Keep track of the bee rects drawn in the current frame for collision
current_frame_bee_rects = []

while running:
    current_time = pygame.time.get_ticks()
    mouse_pos = pygame.mouse.get_pos()
    mouse_pressed = pygame.mouse.get_pressed() # Get mouse button states

    # Reset bee rects for the new frame
    current_frame_bee_rects = []

    # --- Event Handling (Main Pet Mode) ---
    if game_mode == MODE_PET:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Room Navigation
                if bathroom_btn_rect.collidepoint(event.pos):
                    current_room_name = "Bathroom"
                elif honey_storage_btn_rect.collidepoint(event.pos):
                    current_room_name = "Pollen Storage" # Corrected room name
                elif nest_btn_rect.collidepoint(event.pos):
                    current_room_name = "Nest"

                # Check for room-specific button clicks (excluding Clean button)
                if current_room_name == "Nest" and play_btn_rect.collidepoint(event.pos):
                    print("Starting Flappy Game...")
                    game_mode = MODE_FLAPPY
                # elif current_room_name == "Bathroom": # No button click for cleaning
                #     pass
                elif current_room_name == "Pollen Storage" and feed_btn_rect.collidepoint(event.pos): # Corrected room name
                    pet_hunger_level = max_level # Fill honey bar completely
                    print(f"Fed! Honey: {int(pet_hunger_level)}")


    # --- Game Logic (Main Pet Mode) ---
    if game_mode == MODE_PET:
        # Decrease stats over time
        if current_time - last_stat_decrease_time > stat_decrease_interval:
            pet_cleanliness_level = max(0, pet_cleanliness_level - 2)
            pet_hunger_level = max(0, pet_hunger_level - 4)
            deficit = (max_level - pet_cleanliness_level) + (max_level - pet_hunger_level)
            happiness_decrease = max(1, deficit // 20)
            pet_happy_level = max(0, pet_happy_level - happiness_decrease)
            last_stat_decrease_time = current_time

        # --- Cursor Visibility ---
        if current_room_name == "Bathroom":
            if not show_custom_cursor:
                 pygame.mouse.set_visible(False)
                 show_custom_cursor = True
        else:
            if show_custom_cursor:
                 pygame.mouse.set_visible(True)
                 show_custom_cursor = False
        # --- End Cursor Visibility ---

        # --- Cleaning Logic --- (MODIFIED FOR HOVER)
        is_hover_cleaning = False # Renamed variable for clarity
        if current_room_name == "Bathroom": # Only check when in the bathroom
            brush_rect.center = mouse_pos # Update brush rect position to follow mouse
            # Need to draw bees first before checking collision here
            # We will check collision *after* drawing the bees

        # --- Drawing (Main Pet Mode) ---
        screen.fill(HONEYCOMB_FILL) # Fill background first

        # Draw Honeycomb Background
        hex_height = math.sqrt(3) * HEX_RADIUS
        hex_width = 2 * HEX_RADIUS
        vert_spacing = hex_height
        horiz_spacing = hex_width * 3/4
        current_y = -hex_height / 2
        row_index = 0
        while current_y < SCREEN_HEIGHT + hex_height:
            if row_index % 2 != 0: current_x = -horiz_spacing / 2
            else: current_x = -horiz_spacing
            while current_x < SCREEN_WIDTH + horiz_spacing:
                draw_hexagon(screen, HONEYCOMB_FILL, HONEYCOMB_OUTLINE,
                             current_x, current_y, HEX_RADIUS)
                current_x += horiz_spacing
            current_y += vert_spacing
            row_index += 1

        # Draw Status Bars
        draw_generic_bar(screen, cleanliness_bar_rect, LIGHT_BLUE, pet_cleanliness_level, max_level, "Clean")
        draw_generic_bar(screen, honey_bar_rect, GREEN, pet_hunger_level, max_level, "Honey")
        draw_generic_bar(screen, happy_bar_rect, YELLOW, pet_happy_level, max_level, "Happy")

        # Draw Titles using loaded fonts
        draw_text("Hive", font_large, BLACK, screen, SCREEN_WIDTH // 2, title_y, center=True) # Using "Hive" title from v3
        draw_text(current_room_name, font_small, BLACK, screen, SCREEN_WIDTH // 2, room_name_y, center=True)

        # --- Draw Bee(s) ---
        # Store the rects returned by draw_bee
        current_frame_bee_rects = [] # Clear rects before drawing
        if bee_level == 1:
            bee_rect = draw_bee(screen, pet_center_x, pet_center_y, mouse_pos)
            current_frame_bee_rects.append(bee_rect) # Store rect
        elif bee_level == 2:
            bee_rect1 = draw_bee(screen, pet_center_x - bee_spacing_offset, pet_center_y, mouse_pos)
            bee_rect2 = draw_bee(screen, pet_center_x + bee_spacing_offset, pet_center_y, mouse_pos)
            current_frame_bee_rects.extend([bee_rect1, bee_rect2]) # Store rects
        elif bee_level >= 3: # Draw 3 bees for level 3 and potentially beyond
            bee_rect1 = draw_bee(screen, pet_center_x - bee_spacing_offset, pet_center_y, mouse_pos)
            bee_rect2 = draw_bee(screen, pet_center_x, pet_center_y, mouse_pos)
            bee_rect3 = draw_bee(screen, pet_center_x + bee_spacing_offset, pet_center_y, mouse_pos)
            current_frame_bee_rects.extend([bee_rect1, bee_rect2, bee_rect3]) # Store rects

        # --- Perform Cleaning Logic AFTER drawing bees ---
        if current_room_name == "Bathroom":
            is_hover_cleaning = False
            brush_rect.center = mouse_pos # Ensure brush rect is updated
            for bee_rect in current_frame_bee_rects: # Check collision with bees drawn THIS frame
                if brush_rect.colliderect(bee_rect): # Check if brush cursor is over a bee
                    is_hover_cleaning = True
                    break # Stop checking once one bee is hit

            if is_hover_cleaning: # Increase cleanliness if hovering over a bee
                # Increase cleanliness gradually, ensure it doesn't exceed max
                clean_increase_rate = 0.5 # Slower rate for hover
                pet_cleanliness_level = min(max_level, pet_cleanliness_level + clean_increase_rate)
                # Optional: Add a small sound effect here?
        # --- End Cleaning Logic ---


        # --- Draw XP Bar ---
        if bee_level < max_bee_level:
             draw_generic_bar(screen, xp_bar_rect, XP_BAR_COLOR, xp_current, xp_next_level)
        else:
             draw_generic_bar(screen, xp_bar_rect, XP_BAR_COLOR, xp_current, xp_next_level) # Will show MAX LEVEL text


        # Draw room-specific buttons (excluding Clean button)
        if current_room_name == "Nest":
            pygame.draw.rect(screen, YELLOW, play_btn_rect)
            pygame.draw.rect(screen, BLACK, play_btn_rect, 2)
            screen.blit(play_text_surf, play_text_rect)
        elif current_room_name == "Bathroom":
             pass # No button to draw in the bathroom anymore
        elif current_room_name == "Pollen Storage": # Corrected room name
             pygame.draw.rect(screen, GREEN, feed_btn_rect) # Use Honey color
             pygame.draw.rect(screen, BLACK, feed_btn_rect, 2)
             screen.blit(feed_text_surf, feed_text_rect)

        # Draw Room Navigation Buttons
        nav_button_color = GRAY
        active_nav_button_color = BUTTON_COLOR_ACTIVE
        pygame.draw.rect(screen, active_nav_button_color if current_room_name == "Bathroom" else nav_button_color, bathroom_btn_rect)
        pygame.draw.rect(screen, active_nav_button_color if current_room_name == "Pollen Storage" else nav_button_color, honey_storage_btn_rect) # Corrected room name
        pygame.draw.rect(screen, active_nav_button_color if current_room_name == "Nest" else nav_button_color, nest_btn_rect)
        # Blit the pre-rendered text surfaces
        screen.blit(bathroom_text_surf, bathroom_text_rect)
        screen.blit(honey_storage_text_surf, honey_storage_text_rect)
        screen.blit(nest_text_surf, nest_text_rect)
        pygame.draw.rect(screen, BLACK, bathroom_btn_rect, 2)
        pygame.draw.rect(screen, BLACK, honey_storage_btn_rect, 2)
        pygame.draw.rect(screen, BLACK, nest_btn_rect, 2)

        # --- Draw Custom Cursor (Brush) ---
        if show_custom_cursor:
            brush_rect.center = mouse_pos # Ensure rect is centered on mouse
            screen.blit(brush_image, brush_rect)
        # --- End Custom Cursor Drawing ---

        pygame.display.flip()

    # --- Run Flappy Game Mode ---
    elif game_mode == MODE_FLAPPY:
        # --- Ensure default cursor is visible before starting game ---
        if show_custom_cursor:
            pygame.mouse.set_visible(True)
            show_custom_cursor = False
        # ---

        final_score = run_flappy_game(screen, clock) # Call the modified function

        # --- XP Gain and Level Up Logic ---
        if final_score > 0:
            xp_gain = final_score * 1 # 1 XP per point scored
            print(f"Gained {xp_gain} XP!")
            xp_current += xp_gain

            # Check for level up only if not already max level
            while bee_level < max_bee_level and xp_current >= xp_next_level:
                xp_current -= xp_next_level # Subtract cost of level up
                bee_level += 1
                xp_next_level = xp_levels.get(bee_level, float('inf')) # Get XP needed for the *new* next level
                print(f"*** LEVEL UP! Reached Bee Level {bee_level}! ***")
                if bee_level == max_bee_level:
                    print("*** Max Bee Level Reached! ***")
                    xp_current = 0 # Optional: Reset XP at max level
                    break # Exit the while loop if max level is reached

        # Update happy stat
        happy_gain = final_score * 0.5
        pet_happy_level = min(max_level, pet_happy_level + happy_gain)

        print(f"Returned to Nest. Happy +{happy_gain}")
        print(f"Current XP: {int(xp_current)}/{int(xp_next_level) if xp_next_level != float('inf') else 'MAX'}")
        print(f"New Stats: Clean={int(pet_cleanliness_level)}, Honey={int(pet_hunger_level)}, Happy={int(pet_happy_level)}")

        game_mode = MODE_PET
        current_room_name = "Nest" # Return to Nest after game

    clock.tick(60)

# --- Cleanup ---
pygame.quit()
sys.exit()
