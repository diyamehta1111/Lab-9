import pygame
import random
import time

# ============================================
# INITIALIZE PYGAME
# ============================================
pygame.init()
pygame.mixer.init()

# ============================================
# GAME WINDOW SETUP
# ============================================
screen_width = 800
screen_height = 400
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Cyclist Collector Game")
clock = pygame.time.Clock()

# ============================================
# COLORS
# ============================================
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (50, 100, 200)
RED = (200, 50, 50)
YELLOW = (255, 215, 0)
GREEN = (50, 200, 50)
BROWN = (139, 69, 19)
GRAY = (50, 50, 50)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)

# ============================================
# CREATE SIMPLE SOUND EFFECTS
# ============================================
try:
    import numpy as np
    
    def create_sound(frequency, duration):
        """Create a simple beep sound"""
        sample_rate = 22050
        n_samples = int(round(duration * sample_rate))
        buf = np.zeros((n_samples, 2), dtype=np.int16)
        for i in range(n_samples):
            value = int(32767 * 0.3 * ((i % int(sample_rate / frequency)) < (sample_rate / frequency / 2)))
            buf[i] = [value, value]
        sound = pygame.sndarray.make_sound(buf)
        return sound
    
    coin_sound = create_sound(800, 0.1)
    jump_sound = create_sound(400, 0.05)
    hit_sound = create_sound(200, 0.2)
    
except ImportError:
    print("NumPy not found - sounds disabled. Install with: pip install numpy")
    class DummySound:
        def play(self):
            pass
    coin_sound = DummySound()
    jump_sound = DummySound()
    hit_sound = DummySound()

# ============================================
# GROUND POSITION
# ============================================
ground_y = 300

# ============================================
# PLAYER (CYCLIST) VARIABLES
# ============================================
player_x = 100
player_y = ground_y - 60
player_width = 50
player_height = 60
player_velocity_y = 0
gravity = 0.8
jump_strength = -15
animation_frame = 0

# ============================================
# OBSTACLE VARIABLES
# ============================================
obstacle_width = 20
obstacle_height = 50
base_obstacle_speed = 5
obstacle_speed = base_obstacle_speed
obstacles = []

# ============================================
# COIN VARIABLES
# ============================================
coin_width = 25
coin_height = 25
coins = []
coin_timer = 0
coin_spawn_rate = 120

# ============================================
# LIFELINE (HEART) VARIABLES
# ============================================
heart_width = 30
heart_height = 30
hearts = []
heart_timer = 0
heart_spawn_rate = 600  # Spawn heart every 10 seconds (600 frames at 60 FPS)
player_lives = 3  # Start with 3 lives
max_lives = 5  # Maximum lives possible

# ============================================
# SCORE VARIABLES
# ============================================
score = 0
coins_collected = 0
distance = 0
high_score = 0

# ============================================
# POSITIVE DISENGAGEMENT VARIABLES
# ============================================
play_start_time = 0
play_duration = 0
break_offered = False
break_interval = 60
last_break_time = 0

# Skills tracking
skills_learned = []
all_skills = [
    "Perfect Timing",
    "Quick Reflexes",
    "Coin Hunter",
    "Risk Management",
    "Persistence",
    "Pattern Recognition"
]

# League system
player_league = "Beginner"
league_members = 0

# ============================================
# GAME STATE
# ============================================
game_state = "start"
break_quiz_active = False
user_input = ""
quiz_question = ""
quiz_answer = ""

# ============================================
# HELPER FUNCTIONS
# ============================================

def reset_game():
    """Reset all variables to start new game"""
    global player_y, player_velocity_y, obstacles, coins, hearts
    global score, coins_collected, distance, obstacle_speed, coin_timer, animation_frame
    global break_offered, play_start_time, player_lives, heart_timer
    
    player_y = ground_y - 60
    player_velocity_y = 0
    animation_frame = 0
    
    obstacles = []
    obstacles.append(screen_width)
    coins = []
    hearts = []
    
    score = 0
    coins_collected = 0
    distance = 0
    player_lives = 3
    
    obstacle_speed = base_obstacle_speed
    coin_timer = 0
    heart_timer = 0
    break_offered = False
    play_start_time = time.time()

def draw_cyclist(x, y, frame):
    """
    Draw a simple person riding a bicycle
    
    Parameters:
    - x: horizontal position (left-right) of the cyclist
    - y: vertical position (up-down) of the cyclist
    - frame: animation frame number for pedaling and wheel rotation
    
    The cyclist is made of:
    1. Head (circle)
    2. Body (line leaning forward)
    3. Arms (two lines reaching to handlebars)
    4. Legs (animated to show pedaling motion)
    5. Bicycle frame (triangle shape)
    6. Two wheels with rotating spokes
    """
    
    # 1. DRAW HEAD
    # Simple black circle for the head
    pygame.draw.circle(screen, BLACK, (int(x + 25), int(y + 5)), 8)
    
    # 2. DRAW BODY
    # Line from head to hip, leaning forward for cycling posture
    pygame.draw.line(screen, BLACK, (x + 25, y + 13), (x + 30, y + 30), 3)
    
    # 3. DRAW ARMS - HOLDING HANDLEBARS
    # Upper arm from shoulder to elbow
    pygame.draw.line(screen, BLACK, (x + 25, y + 18), (x + 35, y + 25), 3)
    # Lower arm from elbow to handlebars
    pygame.draw.line(screen, BLACK, (x + 35, y + 25), (x + 40, y + 35), 2)
    
    # 4. DRAW LEGS - ANIMATED PEDALING MOTION
    # Use frame number to create cycling animation
    leg_angle = frame % 40  # Creates a cycle from 0 to 39
    
    if leg_angle < 20:
        # First half of pedal cycle: Left leg down, right leg up
        pygame.draw.line(screen, BLACK, (x + 30, y + 30), (x + 25, y + 45), 3)  # Left leg extended
        pygame.draw.line(screen, BLACK, (x + 30, y + 30), (x + 35, y + 38), 3)  # Right leg bent
    else:
        # Second half: Right leg down, left leg up
        pygame.draw.line(screen, BLACK, (x + 30, y + 30), (x + 35, y + 45), 3)  # Right leg extended
        pygame.draw.line(screen, BLACK, (x + 30, y + 30), (x + 25, y + 38), 3)  # Left leg bent
    
    # 5. DRAW BICYCLE FRAME
    bike_y = y + 45  # Vertical position of bike frame
    
    # Main frame forms a triangle (like a real bicycle)
    pygame.draw.line(screen, BLUE, (x + 15, bike_y), (x + 40, bike_y - 10), 3)  # Top tube (horizontal)
    pygame.draw.line(screen, BLUE, (x + 15, bike_y), (x + 28, bike_y + 10), 3)  # Seat tube (diagonal down)
    pygame.draw.line(screen, BLUE, (x + 28, bike_y + 10), (x + 45, bike_y + 10), 3)  # Down tube (bottom)
    
    # Handlebars at the front
    pygame.draw.line(screen, GRAY, (x + 40, bike_y - 10), (x + 40, bike_y - 5), 2)
    
    # Seat at the back
    pygame.draw.line(screen, BLACK, (x + 13, bike_y - 2), (x + 20, bike_y - 2), 3)
    
    # 6. DRAW WHEELS
    wheel_radius = 12
    
    # Back wheel (left side)
    pygame.draw.circle(screen, BLACK, (int(x + 15), int(bike_y + 10)), wheel_radius, 2)
    
    # Front wheel (right side)
    pygame.draw.circle(screen, BLACK, (int(x + 45), int(bike_y + 10)), wheel_radius, 2)
    
    # 7. DRAW WHEEL SPOKES - ANIMATED ROTATION
    # Alternates between + shape and X shape to show spinning
    if frame % 8 < 4:
        # Draw + shaped spokes (vertical and horizontal)
        
        # Back wheel spokes
        pygame.draw.line(screen, GRAY, (x + 15, bike_y + 10 - 8), (x + 15, bike_y + 10 + 8), 1)  # Vertical
        pygame.draw.line(screen, GRAY, (x + 15 - 8, bike_y + 10), (x + 15 + 8, bike_y + 10), 1)  # Horizontal
        
        # Front wheel spokes
        pygame.draw.line(screen, GRAY, (x + 45, bike_y + 10 - 8), (x + 45, bike_y + 10 + 8), 1)  # Vertical
        pygame.draw.line(screen, GRAY, (x + 45 - 8, bike_y + 10), (x + 45 + 8, bike_y + 10), 1)  # Horizontal
    else:
        # Draw X shaped spokes (diagonal)
        
        # Back wheel spokes (top-left to bottom-right, top-right to bottom-left)
        pygame.draw.line(screen, GRAY, (x + 15 - 6, bike_y + 10 - 6), (x + 15 + 6, bike_y + 10 + 6), 1)
        pygame.draw.line(screen, GRAY, (x + 15 - 6, bike_y + 10 + 6), (x + 15 + 6, bike_y + 10 - 6), 1)
        
        # Front wheel spokes
        pygame.draw.line(screen, GRAY, (x + 45 - 6, bike_y + 10 - 6), (x + 45 + 6, bike_y + 10 + 6), 1)
        pygame.draw.line(screen, GRAY, (x + 45 - 6, bike_y + 10 + 6), (x + 45 + 6, bike_y + 10 - 6), 1)

def check_collision(x1, y1, w1, h1, x2, y2, w2, h2):
    """Check if two rectangles overlap"""
    if (x1 < x2 + w2 and
        x1 + w1 > x2 and
        y1 < y2 + h2 and
        y1 + h1 > y2):
        return True
    return False

def update_league():
    """Update player league based on score"""
    global player_league, league_members
    
    if score < 100:
        player_league = "Beginner League"
        league_members = random.randint(45, 67)
    elif score < 300:
        player_league = "Intermediate League"
        league_members = random.randint(28, 42)
    elif score < 500:
        player_league = "Advanced League"
        league_members = random.randint(15, 25)
    else:
        player_league = "Pro League"
        league_members = random.randint(8, 15)

def add_skill():
    """Add a new skill to the player's skills"""
    global skills_learned
    
    if coins_collected >= 5 and "Coin Hunter" not in skills_learned:
        skills_learned.append("Coin Hunter")
    if distance >= 300 and "Persistence" not in skills_learned:
        skills_learned.append("Persistence")
    if score >= 200 and "Quick Reflexes" not in skills_learned:
        skills_learned.append("Quick Reflexes")
    if coins_collected >= 10 and "Perfect Timing" not in skills_learned:
        skills_learned.append("Perfect Timing")

def get_next_skill():
    """Get a skill the player hasn't learned yet"""
    for skill in all_skills:
        if skill not in skills_learned:
            return skill
    return "Master Cyclist"

def check_break_time():
    """Check if it's time to offer a break"""
    global break_offered, last_break_time, play_duration
    
    play_duration = time.time() - play_start_time
    
    if play_duration - last_break_time >= break_interval and not break_offered:
        return True
    return False

def create_break_quiz():
    """Create a quiz question for the break"""
    global quiz_question, quiz_answer
    
    questions = [
        ("How many points do you get per coin?", "10"),
        ("What key do you press to jump?", "space"),
        ("What color are the coins?", "yellow"),
        ("What are you avoiding?", "obstacles"),
    ]
    
    q, a = random.choice(questions)
    quiz_question = q
    quiz_answer = a.lower()

def draw_heart(x, y):
    """Draw a heart shape for lifeline"""
    # Draw heart using two circles and a triangle
    heart_color = (255, 20, 20)  # Bright red
    
    # Left circle of heart
    pygame.draw.circle(screen, heart_color, (int(x + 8), int(y + 8)), 8)
    # Right circle of heart
    pygame.draw.circle(screen, heart_color, (int(x + 22), int(y + 8)), 8)
    # Bottom triangle
    points = [(x + 2, y + 10), (x + 15, y + 25), (x + 28, y + 10)]
    pygame.draw.polygon(screen, heart_color, points)

# ============================================
# MAIN GAME LOOP
# ============================================
game_running = True

while game_running:
    
    # ========================================
    # HANDLE EVENTS
    # ========================================
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_running = False
        
        if event.type == pygame.KEYDOWN:
            # Handle text input for break quiz
            if break_quiz_active:
                if event.key == pygame.K_RETURN:
                    if user_input.lower() == quiz_answer:
                        break_quiz_active = False
                        user_input = ""
                        last_break_time = time.time()
                        break_offered = False
                    else:
                        game_state = "break_screen"
                        break_quiz_active = False
                        user_input = ""
                elif event.key == pygame.K_BACKSPACE:
                    user_input = user_input[:-1]
                else:
                    user_input = user_input + event.unicode
            
            elif game_state == "start":
                if event.key == pygame.K_SPACE:
                    game_state = "playing"
                    reset_game()
            
            elif game_state == "playing":
                if event.key == pygame.K_SPACE:
                    if player_y >= ground_y - 60:
                        player_velocity_y = jump_strength
                        jump_sound.play()
                elif event.key == pygame.K_p:
                    game_state = "paused"
            
            elif game_state == "paused":
                if event.key == pygame.K_p:
                    game_state = "playing"
            
            elif game_state == "break_screen":
                if event.key == pygame.K_SPACE:
                    game_state = "playing"
                    last_break_time = time.time()
                    break_offered = False
            
            elif game_state == "game_over":
                if event.key == pygame.K_SPACE:
                    game_state = "playing"
                    reset_game()
    
    # ========================================
    # UPDATE GAME
    # ========================================
    if game_state == "playing":
        
        animation_frame = animation_frame + 1
        
        # Update player physics
        player_velocity_y = player_velocity_y + gravity
        player_y = player_y + player_velocity_y
        
        if player_y >= ground_y - 60:
            player_y = ground_y - 60
            player_velocity_y = 0
        
        # Move obstacles
        for i in range(len(obstacles)):
            obstacles[i] = obstacles[i] - obstacle_speed
        
        if len(obstacles) > 0 and obstacles[0] < -obstacle_width:
            obstacles.pop(0)
            if len(obstacles) > 0:
                new_x = obstacles[-1] + random.randint(300, 500)
            else:
                new_x = screen_width
            obstacles.append(new_x)
        
        # Check collision with obstacles
        for obstacle_x in obstacles:
            if check_collision(player_x, player_y, player_width, player_height,
                             obstacle_x, ground_y - obstacle_height, obstacle_width, obstacle_height):
                
                # Lose a life instead of instant game over
                player_lives = player_lives - 1
                hit_sound.play()
                
                # Remove the obstacle that was hit
                obstacles.remove(obstacle_x)
                
                # Check if game over (no lives left)
                if player_lives <= 0:
                    # Update high score
                    if score > high_score:
                        high_score = score
                    else:
                        high_score = score + random.randint(5, 15)
                    
                    game_state = "game_over"
                break  # Exit loop after hit
        
        # Spawn coins
        coin_timer = coin_timer + 1
        if coin_timer >= coin_spawn_rate:
            coin_x = screen_width
            if random.random() < 0.5:
                coin_y = ground_y - coin_height
            else:
                coin_y = ground_y - 100 - random.randint(0, 50)
            coins.append([coin_x, coin_y])
            coin_timer = 0
        
        # Spawn hearts (lifelines) - rarer than coins
        heart_timer = heart_timer + 1
        if heart_timer >= heart_spawn_rate:
            heart_x = screen_width
            # Hearts appear in the air
            heart_y = ground_y - 80 - random.randint(0, 40)
            hearts.append([heart_x, heart_y])
            heart_timer = 0
        
        # Move coins
        for coin in coins:
            coin[0] = coin[0] - obstacle_speed
        
        # Move hearts
        for heart in hearts:
            heart[0] = heart[0] - obstacle_speed
        
        coins = [coin for coin in coins if coin[0] > -coin_width]
        hearts = [heart for heart in hearts if heart[0] > -heart_width]
        
        # Check coin collection
        for coin in coins[:]:
            if check_collision(player_x, player_y, player_width, player_height,
                             coin[0], coin[1], coin_width, coin_height):
                coins.remove(coin)
                coins_collected = coins_collected + 1
                score = score + 10
                coin_sound.play()
                add_skill()
        
        # Check heart collection (lifeline bonus!)
        for heart in hearts[:]:
            if check_collision(player_x, player_y, player_width, player_height,
                             heart[0], heart[1], heart_width, heart_height):
                hearts.remove(heart)
                # Add a life (up to max)
                if player_lives < max_lives:
                    player_lives = player_lives + 1
                    coin_sound.play()  # Happy sound for getting extra life
                    score = score + 20  # Bonus points for collecting heart
        
        # Update score
        distance = distance + 1
        if distance % 10 == 0:
            score = score + 1
        
        # Update league
        update_league()
        
        # Check for break time
        if check_break_time() and not break_quiz_active:
            break_offered = True
            break_quiz_active = True
            create_break_quiz()
        
        # Make game easier after score 300
        if score >= 300:
            if obstacle_speed > base_obstacle_speed:
                obstacle_speed = obstacle_speed - 0.05
        elif distance % 500 == 0 and distance > 0:
            obstacle_speed = obstacle_speed + 0.3
    
    # ========================================
    # DRAW EVERYTHING
    # ========================================
    screen.fill(WHITE)
    pygame.draw.line(screen, BLACK, (0, ground_y), (screen_width, ground_y), 2)
    
    if game_state == "start":
        font_large = pygame.font.Font(None, 64)
        title = font_large.render("CYCLIST COLLECTOR", True, BLACK)
        title_rect = title.get_rect(center=(screen_width // 2, 60))
        screen.blit(title, title_rect)
        
        font_small = pygame.font.Font(None, 24)
        
        instructions = [
            ("HOW TO PLAY:", 130, BLACK),
            ("Press SPACE to JUMP over obstacles", 160, BLACK),
            ("Collect YELLOW coins for 10 points each", 185, YELLOW),
            ("Collect RED HEARTS for extra lives! ❤️", 210, (255, 20, 20)),
            ("You start with 3 lives", 235, BLACK),
            ("Press P to PAUSE anytime", 260, BLACK),
            ("", 285, BLACK),
            ("BREAK SYSTEM:", 310, PURPLE),
            ("You'll get break reminders every minute", 335, PURPLE),
            ("", 360, BLACK),
            ("HOW TO WIN:", 385, GREEN),
            ("Unlock skills and reach Pro League!", 410, GREEN),
        ]
        
        for text, y_pos, color in instructions:
            if text:
                text_surface = font_small.render(text, True, color)
                text_rect = text_surface.get_rect(center=(screen_width // 2, y_pos))
                screen.blit(text_surface, text_rect)
        
        font_medium = pygame.font.Font(None, 32)
        start_text = font_medium.render("Press SPACE to Start", True, BLUE)
        start_rect = start_text.get_rect(center=(screen_width // 2, screen_height - 30))
        screen.blit(start_text, start_rect)
    
    elif break_quiz_active and game_state == "playing":
        draw_cyclist(player_x, player_y, animation_frame)
        
        for obstacle_x in obstacles:
            pygame.draw.rect(screen, RED, 
                           (obstacle_x, ground_y - obstacle_height, obstacle_width, obstacle_height))
        
        for coin in coins:
            pygame.draw.circle(screen, YELLOW, 
                             (int(coin[0] + coin_width // 2), int(coin[1] + coin_height // 2)), 
                             coin_width // 2)
        
        # Draw hearts (lifelines)
        for heart in hearts:
            draw_heart(heart[0], heart[1])
        
        overlay = pygame.Surface((screen_width, screen_height))
        overlay.set_alpha(200)
        overlay.fill(WHITE)
        screen.blit(overlay, (0, 0))
        
        font_large = pygame.font.Font(None, 48)
        font_medium = pygame.font.Font(None, 32)
        
        minutes_played = int(play_duration / 60)
        
        quiz_title = font_large.render("Time for a Quick Break?", True, PURPLE)
        quiz_rect = quiz_title.get_rect(center=(screen_width // 2, 100))
        screen.blit(quiz_title, quiz_rect)
        
        time_text = font_medium.render(f"You've been playing for {minutes_played} minute(s)!", True, BLACK)
        time_rect = time_text.get_rect(center=(screen_width // 2, 150))
        screen.blit(time_text, time_rect)
        
        question_text = font_medium.render("Answer this to keep playing:", True, BLACK)
        question_rect = question_text.get_rect(center=(screen_width // 2, 200))
        screen.blit(question_text, question_rect)
        
        quiz_text = font_medium.render(quiz_question, True, BLUE)
        quiz_text_rect = quiz_text.get_rect(center=(screen_width // 2, 240))
        screen.blit(quiz_text, quiz_text_rect)
        
        input_box = pygame.Rect(screen_width // 2 - 150, 280, 300, 40)
        pygame.draw.rect(screen, BLACK, input_box, 2)
        input_surface = font_medium.render(user_input, True, BLACK)
        screen.blit(input_surface, (input_box.x + 10, input_box.y + 5))
        
        hint_text = font_medium.render("Press ENTER to submit", True, GRAY)
        hint_rect = hint_text.get_rect(center=(screen_width // 2, 340))
        screen.blit(hint_text, hint_rect)
    
    elif game_state == "playing" or game_state == "paused":
        
        draw_cyclist(player_x, player_y, animation_frame)
        
        for obstacle_x in obstacles:
            pygame.draw.rect(screen, RED, 
                           (obstacle_x, ground_y - obstacle_height, obstacle_width, obstacle_height))
        
        for coin in coins:
            pygame.draw.circle(screen, YELLOW, 
                             (int(coin[0] + coin_width // 2), int(coin[1] + coin_height // 2)), 
                             coin_width // 2)
        
        # Draw hearts (lifelines)
        for heart in hearts:
            draw_heart(heart[0], heart[1])
        
        font = pygame.font.Font(None, 28)
        score_text = font.render(f"Score: {score}", True, BLACK)
        screen.blit(score_text, (10, 10))
        
        coins_text = font.render(f"Coins: {coins_collected}", True, YELLOW)
        screen.blit(coins_text, (10, 40))
        
        # Draw lives indicator with hearts
        lives_text = font.render(f"Lives:", True, BLACK)
        screen.blit(lives_text, (10, 70))
        
        for i in range(player_lives):
            # Draw small hearts for each life
            heart_x = 70 + (i * 25)
            heart_y = 72
            small_heart_color = (255, 20, 20)
            # Small heart circles
            pygame.draw.circle(screen, small_heart_color, (int(heart_x + 4), int(heart_y + 4)), 4)
            pygame.draw.circle(screen, small_heart_color, (int(heart_x + 11), int(heart_y + 4)), 4)
            # Small heart triangle
            points = [(heart_x + 1, heart_y + 5), (heart_x + 7.5, heart_y + 12), (heart_x + 14, heart_y + 5)]
            pygame.draw.polygon(screen, small_heart_color, points)
        
        league_text = font.render(f"{player_league} ({league_members} players)", True, PURPLE)
        screen.blit(league_text, (10, 100))
        
        if score >= 200:
            encourage = font.render("You're really getting this game! 🌟", True, GREEN)
            screen.blit(encourage, (screen_width - 350, 10))
        elif score >= 100:
            encourage = font.render("You're getting it! Keep going!", True, GREEN)
            screen.blit(encourage, (screen_width - 320, 10))
        
        if game_state == "paused":
            font_large = pygame.font.Font(None, 72)
            pause_text = font_large.render("PAUSED", True, BLACK)
            pause_rect = pause_text.get_rect(center=(screen_width // 2, screen_height // 2))
            screen.blit(pause_text, pause_rect)
            
            font_small = pygame.font.Font(None, 36)
            resume_text = font_small.render("Press P to Resume", True, BLACK)
            resume_rect = resume_text.get_rect(center=(screen_width // 2, screen_height // 2 + 60))
            screen.blit(resume_text, resume_rect)
    
    elif game_state == "break_screen":
        font_large = pygame.font.Font(None, 64)
        font_medium = pygame.font.Font(None, 36)
        font_small = pygame.font.Font(None, 28)
        
        break_title = font_large.render("Great Job! Take a Break 🎉", True, GREEN)
        break_rect = break_title.get_rect(center=(screen_width // 2, 80))
        screen.blit(break_title, break_rect)
        
        progress_text = font_medium.render(f"You've earned {score} points!", True, BLACK)
        progress_rect = progress_text.get_rect(center=(screen_width // 2, 140))
        screen.blit(progress_text, progress_rect)
        
        if len(skills_learned) > 0:
            skills_title = font_medium.render("Skills Mastered:", True, BLUE)
            skills_rect = skills_title.get_rect(center=(screen_width // 2, 190))
            screen.blit(skills_title, skills_rect)
            
            y_offset = 230
            for skill in skills_learned:
                skill_text = font_small.render(f"✓ {skill}", True, GREEN)
                skill_rect = skill_text.get_rect(center=(screen_width // 2, y_offset))
                screen.blit(skill_text, skill_rect)
                y_offset = y_offset + 30
        
        next_skill = get_next_skill()
        next_text = font_small.render(f"Next time: Try for '{next_skill}'!", True, ORANGE)
        next_rect = next_text.get_rect(center=(screen_width // 2, y_offset + 20))
        screen.blit(next_text, next_rect)
        
        continue_text = font_medium.render("Press SPACE when ready to continue", True, BLUE)
        continue_rect = continue_text.get_rect(center=(screen_width // 2, screen_height - 40))
        screen.blit(continue_text, continue_rect)
    
    elif game_state == "game_over":
        font_large = pygame.font.Font(None, 64)
        font_medium = pygame.font.Font(None, 36)
        font_small = pygame.font.Font(None, 26)
        
        y_position = 40
        
        game_over_text = font_large.render("GAME OVER!", True, RED)
        game_over_rect = game_over_text.get_rect(center=(screen_width // 2, y_position))
        screen.blit(game_over_text, game_over_rect)
        y_position = y_position + 60
        
        score_text = font_medium.render(f"Final Score: {score}", True, BLACK)
        score_rect = score_text.get_rect(center=(screen_width // 2, y_position))
        screen.blit(score_text, score_rect)
        y_position = y_position + 45
        
        high_text = font_small.render(f"High Score: {high_score}", True, BLUE)
        high_rect = high_text.get_rect(center=(screen_width // 2, y_position))
        screen.blit(high_text, high_rect)
        y_position = y_position + 35
        
        coins_text = font_small.render(f"Coins Collected: {coins_collected}", True, YELLOW)
        coins_rect = coins_text.get_rect(center=(screen_width // 2, y_position))
        screen.blit(coins_text, coins_rect)
        y_position = y_position + 40
        
        league_text = font_small.render(f"League: {player_league}", True, PURPLE)
        league_rect = league_text.get_rect(center=(screen_width // 2, y_position))
        screen.blit(league_text, league_rect)
        y_position = y_position + 30
        
        members_text = font_small.render(f"You joined {league_members} other players!", True, PURPLE)
        members_rect = members_text.get_rect(center=(screen_width // 2, y_position))
        screen.blit(members_text, members_rect)
        y_position = y_position + 40
        
        if len(skills_learned) > 0:
            skills_title = font_small.render("Skills You Mastered:", True, GREEN)
            skills_rect = skills_title.get_rect(center=(screen_width // 2, y_position))
            screen.blit(skills_title, skills_rect)
            y_position = y_position + 30
            
            for skill in skills_learned[:3]:
                skill_text = font_small.render(f"✓ {skill}", True, GREEN)
                skill_rect = skill_text.get_rect(center=(screen_width // 2, y_position))
                screen.blit(skill_text, skill_rect)
                y_position = y_position + 28
        
        restart_text = font_medium.render("Press SPACE to Play Again", True, BLUE)
        restart_rect = restart_text.get_rect(center=(screen_width // 2, screen_height - 25))
        screen.blit(restart_text, restart_rect)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()