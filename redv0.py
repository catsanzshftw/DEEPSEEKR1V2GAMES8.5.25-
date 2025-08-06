import pygame
import sys
import random
import math
import os
from pygame.locals import *

# Initialize pygame
pygame.init()
pygame.font.init()

# Game constants
WIDTH, HEIGHT = 600, 400
FPS = 60
TILE_SIZE = 32
GRASS_TILE = (0, 128, 0)  # Dark green for grass
PATH_TILE = (200, 200, 200)  # Light gray for paths
WATER_TILE = (0, 0, 255)  # Blue for water
TREE_TILE = (0, 100, 0)  # Dark green for trees
BUILDING_TILE = (150, 75, 0)  # Brown for buildings

# Player colors
PLAYER_COLORS = {
    "down": (255, 0, 0),    # Red
    "up": (200, 0, 0),      # Darker red
    "left": (220, 0, 0),    # Medium red
    "right": (240, 0, 0)    # Light red
}

# Create the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pokémon Red-Style Game")
clock = pygame.time.Clock()

# Load fonts
title_font = pygame.font.SysFont("Arial", 36, bold=True)
menu_font = pygame.font.SysFont("Arial", 24)
battle_font = pygame.font.SysFont("Arial", 18)
small_font = pygame.font.SysFont("Arial", 14)

# Game states
MAIN_MENU = 0
OVERWORLD = 1
BATTLE = 2
INVENTORY = 3
game_state = MAIN_MENU

# Player data
player_pos = [WIDTH // 2, HEIGHT // 2]
player_direction = "down"
player_speed = 3
player_level = 5
player_pokemon = "Pikachu"
player_health = 100
player_max_health = 100
player_exp = 0
player_next_level = 100
player_money = 500
inventory = {
    "Potion": 3,
    "Poké Ball": 5,
    "Great Ball": 2,
    "Antidote": 2
}

# Battle data
enemy_pokemon = "Charmander"
enemy_level = 4
enemy_health = 80
enemy_max_health = 80
battle_option = 0
battle_options = ["Fight", "Bag", "Pokémon", "Run"]
battle_move = 0
battle_moves = ["Tackle", "Growl", "Thunderbolt", "Tail Whip"]
battle_text = ""
battle_text_timer = 0
battle_state = "player_choice"  # player_choice, enemy_turn, battle_text, victory, defeat

# Create a simple world map
def generate_map(width, height):
    world_map = []
    for y in range(height):
        row = []
        for x in range(width):
            # Create paths along the center
            if (x > width//2 - 3 and x < width//2 + 3) or (y > height//2 - 3 and y < height//2 + 3):
                row.append("path")
            # Create water on edges
            elif x < 3 or x > width - 4 or y < 3 or y > height - 4:
                row.append("water")
            # Create trees in some areas
            elif (x > 10 and x < 20 and y > 10 and y < 20) or (x > 30 and x < 40 and y > 30 and y < 40):
                row.append("tree")
            # Create buildings
            elif (x == 15 and y == 5) or (x == 35 and y == 25) or (x == 5 and y == 35):
                row.append("building")
            # The rest is grass
            else:
                row.append("grass")
        world_map.append(row)
    return world_map

# Generate a 20x15 map (since 20*32=640, 15*32=480 - we'll only show part of it)
world_map = generate_map(20, 15)

# Camera position (to show part of the world)
camera_x = max(0, min(player_pos[0] - WIDTH // 2, len(world_map[0]) * TILE_SIZE - WIDTH))
camera_y = max(0, min(player_pos[1] - HEIGHT // 2, len(world_map) * TILE_SIZE - HEIGHT))

# Pokemon data
pokemon_data = {
    "Pikachu": {"type": "Electric", "color": (255, 215, 0)},
    "Charmander": {"type": "Fire", "color": (255, 69, 0)},
    "Bulbasaur": {"type": "Grass", "color": (0, 128, 0)},
    "Squirtle": {"type": "Water", "color": (0, 105, 148)},
    "Pidgey": {"type": "Flying", "color": (205, 133, 63)},
    "Rattata": {"type": "Normal", "color": (128, 128, 128)}
}

# Draw the world map
def draw_world():
    # Calculate which tiles are visible
    start_x = max(0, camera_x // TILE_SIZE)
    start_y = max(0, camera_y // TILE_SIZE)
    end_x = min(len(world_map[0]), (camera_x + WIDTH) // TILE_SIZE + 1)
    end_y = min(len(world_map), (camera_y + HEIGHT) // TILE_SIZE + 1)
    
    for y in range(start_y, end_y):
        for x in range(start_x, end_x):
            tile_x = x * TILE_SIZE - camera_x
            tile_y = y * TILE_SIZE - camera_y
            
            if world_map[y][x] == "grass":
                pygame.draw.rect(screen, GRASS_TILE, (tile_x, tile_y, TILE_SIZE, TILE_SIZE))
                # Draw grass pattern
                for i in range(3):
                    offset_x = random.randint(0, TILE_SIZE-5)
                    offset_y = random.randint(0, TILE_SIZE-5)
                    pygame.draw.line(screen, (0, 180, 0), 
                                    (tile_x + offset_x, tile_y + offset_y),
                                    (tile_x + offset_x, tile_y + offset_y + 3), 2)
            elif world_map[y][x] == "path":
                pygame.draw.rect(screen, PATH_TILE, (tile_x, tile_y, TILE_SIZE, TILE_SIZE))
            elif world_map[y][x] == "water":
                pygame.draw.rect(screen, WATER_TILE, (tile_x, tile_y, TILE_SIZE, TILE_SIZE))
                # Draw wave pattern
                for i in range(4):
                    offset_x = random.randint(0, TILE_SIZE-5)
                    offset_y = random.randint(0, TILE_SIZE-5)
                    pygame.draw.arc(screen, (100, 100, 255), 
                                   (tile_x + offset_x, tile_y + offset_y, 10, 5), 
                                   0, math.pi, 2)
            elif world_map[y][x] == "tree":
                pygame.draw.rect(screen, GRASS_TILE, (tile_x, tile_y, TILE_SIZE, TILE_SIZE))
                pygame.draw.rect(screen, TREE_TILE, (tile_x + TILE_SIZE//3, tile_y, TILE_SIZE//3, TILE_SIZE))
                pygame.draw.circle(screen, (0, 80, 0), (tile_x + TILE_SIZE//2, tile_y - 5), TILE_SIZE//2)
            elif world_map[y][x] == "building":
                pygame.draw.rect(screen, BUILDING_TILE, (tile_x, tile_y, TILE_SIZE, TILE_SIZE))
                pygame.draw.rect(screen, (100, 100, 255), (tile_x + TILE_SIZE//4, tile_y + TILE_SIZE//3, TILE_SIZE//2, TILE_SIZE//3))

# Draw the player
def draw_player():
    player_screen_x = player_pos[0] - camera_x
    player_screen_y = player_pos[1] - camera_y
    
    # Draw player body
    pygame.draw.circle(screen, PLAYER_COLORS[player_direction], 
                      (player_screen_x, player_screen_y - 5), 10)
    
    # Draw player legs
    leg_offset = 0
    if pygame.time.get_ticks() % 500 < 250:
        leg_offset = 3
    
    if player_direction == "down":
        pygame.draw.line(screen, (0, 0, 0), 
                        (player_screen_x - 5, player_screen_y + 5),
                        (player_screen_x - 5, player_screen_y + 15 + leg_offset), 2)
        pygame.draw.line(screen, (0, 0, 0), 
                        (player_screen_x + 5, player_screen_y + 5),
                        (player_screen_x + 5, player_screen_y + 15 - leg_offset), 2)
    elif player_direction == "up":
        pygame.draw.line(screen, (0, 0, 0), 
                        (player_screen_x - 5, player_screen_y + 5),
                        (player_screen_x - 5, player_screen_y + 15 - leg_offset), 2)
        pygame.draw.line(screen, (0, 0, 0), 
                        (player_screen_x + 5, player_screen_y + 5),
                        (player_screen_x + 5, player_screen_y + 15 + leg_offset), 2)
    elif player_direction == "left":
        pygame.draw.line(screen, (0, 0, 0), 
                        (player_screen_x - 2, player_screen_y + 5),
                        (player_screen_x - 2 - leg_offset, player_screen_y + 15), 2)
        pygame.draw.line(screen, (0, 0, 0), 
                        (player_screen_x + 2, player_screen_y + 5),
                        (player_screen_x + 2 + leg_offset, player_screen_y + 15), 2)
    elif player_direction == "right":
        pygame.draw.line(screen, (0, 0, 0), 
                        (player_screen_x - 2, player_screen_y + 5),
                        (player_screen_x - 2 + leg_offset, player_screen_y + 15), 2)
        pygame.draw.line(screen, (0, 0, 0), 
                        (player_screen_x + 2, player_screen_y + 5),
                        (player_screen_x + 2 - leg_offset, player_screen_y + 15), 2)

# Draw HUD
def draw_hud():
    # Top bar
    pygame.draw.rect(screen, (50, 50, 50), (0, 0, WIDTH, 30))
    
    # Player info
    name_text = menu_font.render(f"{player_pokemon}", True, (255, 255, 255))
    screen.blit(name_text, (10, 5))
    
    level_text = menu_font.render(f"Lv: {player_level}", True, (255, 255, 255))
    screen.blit(level_text, (WIDTH - 80, 5))
    
    # Health bar
    pygame.draw.rect(screen, (100, 100, 100), (150, 10, 200, 15))
    health_width = max(0, min(200, int(200 * player_health / player_max_health)))
    pygame.draw.rect(screen, (0, 255, 0), (150, 10, health_width, 15))
    pygame.draw.rect(screen, (0, 0, 0), (150, 10, 200, 15), 1)
    
    health_text = small_font.render(f"HP: {player_health}/{player_max_health}", True, (255, 255, 255))
    screen.blit(health_text, (360, 10))
    
    # Exp bar
    exp_percent = player_exp / player_next_level
    pygame.draw.rect(screen, (70, 70, 70), (10, HEIGHT - 20, WIDTH - 20, 10))
    pygame.draw.rect(screen, (0, 0, 255), (10, HEIGHT - 20, int((WIDTH - 20) * exp_percent), 10))
    pygame.draw.rect(screen, (0, 0, 0), (10, HEIGHT - 20, WIDTH - 20, 10), 1)

# Draw battle screen
def draw_battle():
    # Background
    screen.fill((200, 230, 255))
    
    # Draw enemy pokemon
    enemy_x, enemy_y = WIDTH - 150, 80
    pygame.draw.circle(screen, pokemon_data[enemy_pokemon]["color"], (enemy_x, enemy_y), 50)
    enemy_text = battle_font.render(f"{enemy_pokemon} Lv{enemy_level}", True, (0, 0, 0))
    screen.blit(enemy_text, (enemy_x - 40, enemy_y + 60))
    
    # Enemy health bar
    pygame.draw.rect(screen, (100, 100, 100), (WIDTH - 220, 20, 200, 15))
    health_width = max(0, min(200, int(200 * enemy_health / enemy_max_health)))
    pygame.draw.rect(screen, (0, 255, 0), (WIDTH - 220, 20, health_width, 15))
    pygame.draw.rect(screen, (0, 0, 0), (WIDTH - 220, 20, 200, 15), 1)
    
    # Draw player pokemon
    player_x, player_y = 150, HEIGHT - 100
    pygame.draw.circle(screen, pokemon_data[player_pokemon]["color"], (player_x, player_y), 50)
    player_text = battle_font.render(f"{player_pokemon} Lv{player_level}", True, (0, 0, 0))
    screen.blit(player_text, (player_x - 40, player_y + 60))
    
    # Player health bar
    pygame.draw.rect(screen, (100, 100, 100), (20, HEIGHT - 120, 200, 15))
    health_width = max(0, min(200, int(200 * player_health / player_max_health)))
    pygame.draw.rect(screen, (0, 255, 0), (20, HEIGHT - 120, health_width, 15))
    pygame.draw.rect(screen, (0, 0, 0), (20, HEIGHT - 120, 200, 15), 1)
    
    # Battle menu
    if battle_state == "player_choice":
        pygame.draw.rect(screen, (200, 200, 200), (10, HEIGHT - 100, WIDTH - 20, 90))
        pygame.draw.rect(screen, (0, 0, 0), (10, HEIGHT - 100, WIDTH - 20, 90), 2)
        
        for i, option in enumerate(battle_options):
            color = (0, 0, 0) if i != battle_option else (255, 0, 0)
            option_text = battle_font.render(option, True, color)
            screen.blit(option_text, (30 + (i % 2) * 280, HEIGHT - 80 + (i // 2) * 30))
    
    elif battle_state == "move_selection":
        pygame.draw.rect(screen, (200, 200, 200), (10, HEIGHT - 100, WIDTH - 20, 90))
        pygame.draw.rect(screen, (0, 0, 0), (10, HEIGHT - 100, WIDTH - 20, 90), 2)
        
        for i, move in enumerate(battle_moves):
            color = (0, 0, 0) if i != battle_move else (255, 0, 0)
            move_text = battle_font.render(move, True, color)
            screen.blit(move_text, (30 + (i % 2) * 280, HEIGHT - 80 + (i // 2) * 30))
    
    elif battle_state == "battle_text":
        pygame.draw.rect(screen, (200, 200, 200), (10, HEIGHT - 100, WIDTH - 20, 90))
        pygame.draw.rect(screen, (0, 0, 0), (10, HEIGHT - 100, WIDTH - 20, 90), 2)
        
        text_lines = battle_text.split("\n")
        for i, line in enumerate(text_lines):
            text_surface = battle_font.render(line, True, (0, 0, 0))
            screen.blit(text_surface, (20, HEIGHT - 90 + i * 25))
    
    # Battle text
    if battle_text:
        text_lines = battle_text.split("\n")
        for i, line in enumerate(text_lines):
            text_surface = battle_font.render(line, True, (0, 0, 0))
            screen.blit(text_surface, (20, HEIGHT - 90 + i * 25))

# Draw inventory screen
def draw_inventory():
    screen.fill((100, 100, 200))
    
    title = title_font.render("INVENTORY", True, (255, 255, 0))
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 20))
    
    # Player info
    money_text = menu_font.render(f"Money: ${player_money}", True, (255, 255, 255))
    screen.blit(money_text, (20, 80))
    
    # Draw items
    y_pos = 120
    for i, (item, quantity) in enumerate(inventory.items()):
        color = (255, 255, 0) if i == battle_option else (255, 255, 255)
        item_text = menu_font.render(f"{item}: {quantity}", True, color)
        screen.blit(item_text, (50, y_pos))
        y_pos += 40
    
    # Back option
    back_text = menu_font.render("Press ESC to return", True, (255, 255, 255))
    screen.blit(back_text, (WIDTH//2 - back_text.get_width()//2, HEIGHT - 50))

# Draw main menu
def draw_main_menu():
    screen.fill((0, 100, 200))
    
    # Title
    title = title_font.render("POKÉMON RED", True, (255, 255, 0))
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 80))
    
    # Menu options
    options = ["New Game", "Continue", "Options", "Quit"]
    for i, option in enumerate(options):
        color = (255, 255, 0) if i == battle_option else (255, 255, 255)
        option_text = menu_font.render(option, True, color)
        screen.blit(option_text, (WIDTH//2 - option_text.get_width()//2, 180 + i * 50))
    
    # Copyright
    copyright_text = small_font.render("© 2024 PyGame Pokémon Project", True, (200, 200, 200))
    screen.blit(copyright_text, (WIDTH//2 - copyright_text.get_width()//2, HEIGHT - 30))

# Handle overworld movement
def move_player(dx, dy):
    global player_pos, camera_x, camera_y, player_direction
    
    # Set direction
    if dx > 0:
        player_direction = "right"
    elif dx < 0:
        player_direction = "left"
    elif dy > 0:
        player_direction = "down"
    elif dy < 0:
        player_direction = "up"
    
    # Calculate new position
    new_x = player_pos[0] + dx
    new_y = player_pos[1] + dy
    
    # Check map bounds
    if 0 <= new_x < len(world_map[0]) * TILE_SIZE and 0 <= new_y < len(world_map) * TILE_SIZE:
        # Check if tile is walkable (not water or tree)
        tile_x = int(new_x // TILE_SIZE)
        tile_y = int(new_y // TILE_SIZE)
        
        if world_map[tile_y][tile_x] not in ["water", "tree"]:
            player_pos[0] = new_x
            player_pos[1] = new_y
            
            # Update camera to follow player
            camera_x = max(0, min(player_pos[0] - WIDTH // 2, len(world_map[0]) * TILE_SIZE - WIDTH))
            camera_y = max(0, min(player_pos[1] - HEIGHT // 2, len(world_map) * TILE_SIZE - HEIGHT))
            
            # Random encounter in grass
            if world_map[tile_y][tile_x] == "grass" and random.random() < 0.005:
                start_battle()

# Start a battle
def start_battle():
    global game_state, battle_state, enemy_pokemon, enemy_level, enemy_health, enemy_max_health
    game_state = BATTLE
    battle_state = "player_choice"
    
    # Choose a random enemy pokemon
    enemy_pokemon = random.choice(list(pokemon_data.keys()))
    enemy_level = random.randint(max(1, player_level - 2), player_level + 2)
    enemy_max_health = 60 + enemy_level * 10
    enemy_health = enemy_max_health
    
    # Set battle text
    global battle_text, battle_text_timer
    battle_text = f"Wild {enemy_pokemon} appeared!"
    battle_text_timer = 120  # Show for 2 seconds

# Handle battle logic
def handle_battle():
    global battle_state, battle_text, battle_text_timer, player_health, enemy_health
    global player_exp, player_level, player_next_level, game_state
    
    if battle_state == "battle_text":
        battle_text_timer -= 1
        if battle_text_timer <= 0:
            if "fainted" in battle_text:
                if "Wild" in battle_text:  # Player won
                    battle_state = "victory"
                    
                    # Gain experience
                    exp_gain = enemy_level * 10
                    player_exp += exp_gain
                    battle_text = f"You defeated {enemy_pokemon}!\nGained {exp_gain} EXP!"
                    battle_text_timer = 180
                    
                    # Level up
                    if player_exp >= player_next_level:
                        player_level += 1
                        player_exp = 0
                        player_next_level *= 1.5
                        player_max_health += 20
                        player_health = player_max_health
                        battle_text += f"\n{player_pokemon} grew to Lv {player_level}!"
                else:  # Player lost
                    battle_state = "defeat"
                    battle_text = "You blacked out!\nYou rush to the nearest Pokémon Center..."
                    battle_text_timer = 180
            elif battle_state == "victory":
                game_state = OVERWORLD
                player_health = player_max_health  # Restore health after battle
            elif battle_state == "defeat":
                game_state = OVERWORLD
                player_health = player_max_health  # Restore health
            else:
                battle_state = "player_choice"
    
    elif battle_state == "enemy_turn":
        # Enemy attacks
        damage = random.randint(5, 15)
        player_health = max(0, player_health - damage)
        battle_text = f"Enemy {enemy_pokemon} used Scratch!\nIt did {damage} damage!"
        battle_text_timer = 120
        battle_state = "battle_text"
        
        if player_health <= 0:
            battle_text = f"{player_pokemon} fainted!"
            battle_text_timer = 120

# Main game loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        
        elif event.type == KEYDOWN:
            if game_state == MAIN_MENU:
                if event.key == K_DOWN:
                    battle_option = (battle_option + 1) % 4
                elif event.key == K_UP:
                    battle_option = (battle_option - 1) % 4
                elif event.key == K_RETURN:
                    if battle_option == 0:  # New Game
                        game_state = OVERWORLD
                    elif battle_option == 3:  # Quit
                        running = False
            
            elif game_state == OVERWORLD:
                if event.key == K_RIGHT:
                    move_player(player_speed, 0)
                elif event.key == K_LEFT:
                    move_player(-player_speed, 0)
                elif event.key == K_DOWN:
                    move_player(0, player_speed)
                elif event.key == K_UP:
                    move_player(0, -player_speed)
                elif event.key == K_i:  # Inventory
                    game_state = INVENTORY
                    battle_option = 0
                elif event.key == K_b:  # Force battle for testing
                    start_battle()
            
            elif game_state == BATTLE:
                if battle_state == "player_choice":
                    if event.key == K_RIGHT:
                        battle_option = (battle_option + 1) % 4
                    elif event.key == K_LEFT:
                        battle_option = (battle_option - 1) % 4
                    elif event.key == K_DOWN:
                        battle_option = min(battle_option + 2, 3)
                    elif event.key == K_UP:
                        battle_option = max(battle_option - 2, 0)
                    elif event.key == K_RETURN:
                        if battle_option == 0:  # Fight
                            battle_state = "move_selection"
                            battle_move = 0
                        elif battle_option == 1:  # Bag
                            battle_text = "You opened your bag."
                            battle_text_timer = 90
                            battle_state = "battle_text"
                        elif battle_option == 2:  # Pokémon
                            battle_text = "You have only one Pokémon."
                            battle_text_timer = 90
                            battle_state = "battle_text"
                        elif battle_option == 3:  # Run
                            if random.random() < 0.8:  # 80% chance to escape
                                battle_text = "Got away safely!"
                                battle_text_timer = 90
                                battle_state = "battle_text"
                            else:
                                battle_text = "Couldn't escape!"
                                battle_text_timer = 90
                                battle_state = "battle_text"
                
                elif battle_state == "move_selection":
                    if event.key == K_RIGHT:
                        battle_move = (battle_move + 1) % 4
                    elif event.key == K_LEFT:
                        battle_move = (battle_move - 1) % 4
                    elif event.key == K_DOWN:
                        battle_move = min(battle_move + 2, 3)
                    elif event.key == K_UP:
                        battle_move = max(battle_move - 2, 0)
                    elif event.key == K_RETURN:
                        # Player attacks
                        damage = random.randint(10, 25)
                        enemy_health = max(0, enemy_health - damage)
                        battle_text = f"{player_pokemon} used {battle_moves[battle_move]}!\nIt did {damage} damage!"
                        battle_text_timer = 120
                        battle_state = "battle_text"
                        
                        if enemy_health <= 0:
                            battle_text = f"Wild {enemy_pokemon} fainted!"
                            battle_text_timer = 120
                        else:
                            battle_state = "enemy_turn"  # Enemy's turn after player attack
                    elif event.key == K_ESCAPE:
                        battle_state = "player_choice"
            
            elif game_state == INVENTORY:
                if event.key == K_DOWN:
                    battle_option = (battle_option + 1) % len(inventory)
                elif event.key == K_UP:
                    battle_option = (battle_option - 1) % len(inventory)
                elif event.key == K_RETURN:
                    item = list(inventory.keys())[battle_option]
                    if item == "Potion" and player_health < player_max_health:
                        player_health = min(player_max_health, player_health + 30)
                        inventory[item] -= 1
                        if inventory[item] <= 0:
                            del inventory[item]
                elif event.key == K_ESCAPE:
                    game_state = OVERWORLD
    
    # Update game state
    if game_state == BATTLE:
        handle_battle()
    
    # Draw everything
    if game_state == MAIN_MENU:
        draw_main_menu()
    elif game_state == OVERWORLD:
        draw_world()
        draw_player()
        draw_hud()
    elif game_state == BATTLE:
        draw_battle()
    elif game_state == INVENTORY:
        draw_inventory()
    
    # Update display
    pygame.display.flip()
    clock.tick(FPS)

# Clean up
pygame.quit()
sys.exit()
