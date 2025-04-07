import asyncio

from src.flappy import Flappy

import asyncio
import os
import json
import pygame
from src.flappy import Flappy
from src.entities import Score, Background, Pipes, Player, Floor, WelcomeMessage, GameOver

# Save original methods
original_score_init = Score.__init__
original_score_tick = Score.tick
original_background_tick = Background.tick
original_pipes_tick = Pipes.tick
original_player_tick = Player.tick

# Path for high score file
high_score_file = os.path.join(os.path.dirname(__file__), "high_score.json")

def load_high_score():
    """Load high score from file, or return 0 if file doesn't exist"""
    try:
        if os.path.exists(high_score_file):
            with open(high_score_file, 'r') as f:
                data = json.load(f)
                return data.get('high_score', 0)
    except Exception as e:
        print(f"Error loading high score: {e}")
    return 0

def save_high_score(high_score):
    """Save high score to file"""
    try:
        with open(high_score_file, 'w') as f:
            json.dump({'high_score': high_score}, f)
    except Exception as e:
        print(f"Error saving high score: {e}")

# Override Score.__init__ to include high score
def new_score_init(self, config):
    original_score_init(self, config)
    self.high_score = load_high_score()

# Override Score.tick to display high score
def new_score_tick(self):
    original_score_tick(self)
    # Draw high score at the top right
    font = pygame.font.Font(None, 24)
    high_score_text = font.render(f"Highscore: {self.high_score}", True, (255, 255, 255))
    self.config.screen.blit(high_score_text, 
                          (self.config.window.width - high_score_text.get_width() - 10, 10))

# Add the set_high_score method to Score
def set_high_score(self, high_score):
    self.high_score = high_score

# Track the current asset set being used
current_asset_set = 0

# Define multiple asset sets to cycle through
asset_sets = [
    # Set 0 (Default, for score < 20)
    {
        'background': 'assets/sprites/background-day.png',
        'pipe-lower': 'assets/sprites/pipe-green.png',
        'pipe-upper': 'assets/sprites/pipe-green.png',
        'player': ['assets/sprites/yellowbird-upflap.png', 
                  'assets/sprites/yellowbird-midflap.png', 
                  'assets/sprites/yellowbird-downflap.png']
    },
    # Set 1 (First change, for 20 <= score < 40)
    {
        'background': 'assets/sprites/background-night.png',
        'pipe-lower': 'assets/sprites/pipe-red.png',
        'pipe-upper': 'assets/sprites/pipe-red.png',
        'player': ['assets/sprites/redbird-upflap.png', 
                  'assets/sprites/redbird-midflap.png', 
                  'assets/sprites/redbird-downflap.png']
    },
    # Set 2 (Second change, for 40 <= score < 60)
    {
        'background': 'assets/sprites/background-day.png',  # Back to day but with blue bird
        'pipe-lower': 'assets/sprites/pipe-green.png',      # Back to green pipes
        'pipe-upper': 'assets/sprites/pipe-green.png',
        'player': ['assets/sprites/bluebird-upflap.png', 
                  'assets/sprites/bluebird-midflap.png', 
                  'assets/sprites/bluebird-downflap.png']
    }
]

# Determine which asset set to use based on score
def get_asset_set_for_score(score):
    if score < 20:
        return 0  # Default set
    
    # Calculate which set to use for scores >= 20
    # This will cycle through sets 1, 2, etc. as score increases
    threshold_index = (score // 20) % (len(asset_sets) - 1)
    if threshold_index == 0:
        threshold_index = len(asset_sets) - 1  # Use the last set if division is exact
    return threshold_index

# Override Background.tick to change image based on score thresholds
def new_background_tick(self):
    # Access the current score
    score_value = getattr(Flappy, 'current_score', 0)
    
    # Get the appropriate asset set
    asset_set_index = get_asset_set_for_score(score_value)
    
    # If we need to switch assets
    global current_asset_set
    if asset_set_index != current_asset_set:
        # Save current set as the active one
        current_asset_set = asset_set_index
        
        # Switch background
        try:
            bg_path = asset_sets[asset_set_index]['background']
            self.image = pygame.image.load(bg_path).convert()
        except Exception as e:
            print(f"Error loading background at score {score_value}: {e}")
    
    # Run original tick method with potentially updated image
    original_background_tick(self)

# Override Pipes.tick to change image based on score thresholds
def new_pipes_tick(self):
    # Access the current score
    score_value = getattr(Flappy, 'current_score', 0)
    
    # Get the appropriate asset set
    asset_set_index = get_asset_set_for_score(score_value)
    
    # If we need to switch assets
    global current_asset_set
    if asset_set_index != current_asset_set:
        # Update pipes
        try:
            pipe_lower_path = asset_sets[asset_set_index]['pipe-lower']
            pipe_upper_path = asset_sets[asset_set_index]['pipe-upper']
            
            pipe_lower_img = pygame.image.load(pipe_lower_path).convert_alpha()
            pipe_upper_img = pygame.transform.rotate(pipe_lower_img, 180)
            
            # Update all pipes
            for pipe in self.lower:
                pipe.image = pipe_lower_img
            for pipe in self.upper:
                pipe.image = pipe_upper_img
        except Exception as e:
            print(f"Error loading pipes at score {score_value}: {e}")
    
    # Run the original method
    original_pipes_tick(self)

# Override Player.tick to change image based on score thresholds
def new_player_tick(self):
    # Access the current score
    score_value = getattr(Flappy, 'current_score', 0)
    
    # Get the appropriate asset set
    asset_set_index = get_asset_set_for_score(score_value)
    
    # If we need to switch assets
    global current_asset_set
    if asset_set_index != current_asset_set:
        # Switch player images
        try:
            bird_paths = asset_sets[asset_set_index]['player']
            
            # Load bird images based on the class structure
            if hasattr(self, 'images') and isinstance(self.image, list):
                # Handle the case with multiple animation frames
                self.images = [pygame.image.load(img).convert_alpha() for img in bird_paths]
            elif hasattr(self, 'image'):
                # Handle the case with a single image
                self.image = pygame.image.load(bird_paths[0]).convert_alpha()
        except Exception as e:
            print(f"Error loading player at score {score_value}: {e}")
    
    # Run the original method
    original_player_tick(self)

# Save original play method
original_play = Flappy.play
# Override play method to update high score
async def new_play(self):
    self.score.reset()
    self.player.set_mode(self.player.mode.NORMAL)
    
    # Reset asset set when starting a new game
    global current_asset_set
    current_asset_set = 0
    
    # Set initial score
    Flappy.current_score = 0

    while True:
        # Update the static current_score variable for other entities to access
        Flappy.current_score = self.score.score
        
        if self.player.collided(self.pipes, self.floor):
            # Update high score if needed
            if self.score.score > self.score.high_score:
                self.score.high_score = self.score.score
                save_high_score(self.score.high_score)
            return

        for i, pipe in enumerate(self.pipes.upper):
            if self.player.crossed(pipe):
                self.score.add()
                # Update the static current_score variable
                Flappy.current_score = self.score.score
                # Check if current score exceeds high score
                if self.score.score > self.score.high_score:
                    self.score.high_score = self.score.score
                    save_high_score(self.score.high_score)

        for event in pygame.event.get():
            self.check_quit_event(event)
            if self.is_tap_event(event):
                self.player.flap()

        self.background.tick()
        self.floor.tick()
        self.pipes.tick()
        self.score.tick()
        self.player.tick()

        pygame.display.update()
        await asyncio.sleep(0)
        self.config.tick()

# Override the check_quit_event method to save high score before quitting
original_check_quit_event = Flappy.check_quit_event
def new_check_quit_event(self, event):
    if event.type == pygame.QUIT or (
        event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
    ):
        # Save high score before quitting if needed
        if hasattr(self, 'score') and hasattr(self.score, 'high_score'):
            save_high_score(self.score.high_score)
        original_check_quit_event(self, event)

# Add static variable to Flappy for tracking current score
Flappy.current_score = 0

# Apply the monkey patches
Score.__init__ = new_score_init
Score.tick = new_score_tick
Score.set_high_score = set_high_score
Background.tick = new_background_tick
Pipes.tick = new_pipes_tick
Player.tick = new_player_tick
Flappy.play = new_play
Flappy.check_quit_event = new_check_quit_event

# Modify Flappy.start to use the score's high score directly
original_flappy_start = Flappy.start
async def new_flappy_start(self):
    while True:
        self.background = Background(self.config)
        self.floor = Floor(self.config)
        self.player = Player(self.config)
        self.welcome_message = WelcomeMessage(self.config)
        self.game_over_message = GameOver(self.config)
        self.pipes = Pipes(self.config)
        self.score = Score(self.config)
        # No need to set high score, it's loaded in the Score.__init__ now
        await self.splash()
        await self.play()
        await self.game_over()

Flappy.start = new_flappy_start

if __name__ == "__main__":
    print("Current Date and Time (UTC - YYYY-MM-DD HH:MM:SS formatted): 2025-03-22 21:08:28")
    print("Current User's Login: Uday-Bais")
    asyncio.run(Flappy().start())
if __name__ == "__main__":
    asyncio.run(Flappy().start())
