import pygame
import sys
import random
import os

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 40
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 150, 255)      # Player fallback
RED = (255, 50, 50)       # Monster fallback
GREEN = (50, 255, 50)     # Exit fallback
YELLOW = (255, 255, 0)    # Text & UI
PURPLE = (200, 50, 200)   # Item fallback
DARK_GRAY = (40, 40, 40)  
DULL_GREEN = (35, 50, 30) # Floor (Gloomy Grass)
HEDGE_GREEN = (20, 40, 20)# Hedge Wall fallback
GOLD = (255, 215, 0)      # Key fallback

# Setup screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Gloomy Hedge Maze")
clock = pygame.time.Clock()

# Helper function to load images safely
def load_image(filename, size, fallback_color, remove_white=False):
    surface = pygame.Surface(size, pygame.SRCALPHA)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(base_dir, filename)
    
    if os.path.exists(filepath):
        try:
            img = pygame.image.load(filepath).convert_alpha()
            if remove_white:
                img.set_colorkey((255, 255, 255))
                mask = pygame.mask.from_surface(img)
                rects = mask.get_bounding_rects()
                if rects:
                    union_rect = rects[0].unionall(rects)
                    img = img.subsurface(union_rect)
            surface = pygame.transform.scale(img, size)
            return surface
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
    surface.fill(fallback_color)
    return surface

# 5 Levels Array (20 cols x 15 rows)
levels = [
    # Level 1 - Introduction, easy
    [
        "####################",
        "#P                 #",
        "# ####   #####   ###",
        "# #      #   #     #",
        "# #  #####   ###   #",
        "# #          #   K #",
        "# ########## #     #",
        "#I         H #     #",
        "##########   #   ###",
        "#        #   #     #",
        "#   #### #   ###   #",
        "#   #    #   #   E #",
        "#   #  ###   #   ###",
        "#        #         #",
        "####################"
    ],
    # Level 2 - Few monsters
    [
        "####################",
        "#P       #   H     #",
        "# ####   #   #   ###",
        "# #      #   #     #",
        "# #  #####   ###   #",
        "# #  I       #   V #",
        "# ########## #     #",
        "#            #    K#",
        "##########   #   ###",
        "#        #   #     #",
        "#   #### #   ###   #",
        "#   #    #   #   E #",
        "#   #  ###   #   ###",
        "#H       #         #",
        "####################"
    ],
    # Level 3 - More complex paths and monsters
    [
        "####################",
        "#P   #             #",
        "# #### ######### ###",
        "#      #       #   #",
        "###### # ##### ### #",
        "#I   # # #   #   # #",
        "# #### # # # ### # #",
        "#      #   #     # #",
        "######## ######### #",
        "#        # I       #",
        "# ###### # #########",
        "# V      #      K  #",
        "### #### ######### #",
        "#H             H E #",
        "####################"
    ],
    # Level 4 - Harder maze, tight corridors
    [
        "####################",
        "#P       #I        #",
        "# ###### # ##### ###",
        "#      # # #       #",
        "# V    # # # H     #",
        "###### # # #########",
        "#      # #         #",
        "# ###### #######   #",
        "#              I #",
        "##########   # # ###",
        "# V      #   # #   #",
        "# ###### #   # ### #",
        "#      # #   # K #E#",
        "#H     #     #H    #",
        "####################"
    ],
    # Level 5 - Ultimate challenge (Redesigned for Boss)
    [
        "####################",
        "#P    #H   #      I#",
        "# ### # ## # #######",
        "# # I #  # # # V   #",
        "# # ###  # # #   # #",
        "# #      # H #   # #",
        "# ######## ###   # #",
        "#           #   # #",
        "#####  ## ##  #   # #",
        "# I    # #V  #   # #",
        "# #### # #   #   # #",
        "#   # # #   #######",
        "# K  # # #     T  E#",
        "######## #   #######",
        "####################"
    ]
]

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Visual image 8 times bigger (approx 304x304)
        self.visual_image = load_image("player.png", ((TILE_SIZE - 2) * 8, (TILE_SIZE - 2) * 8), BLUE, remove_white=True)
        self.image = pygame.Surface((TILE_SIZE - 2, TILE_SIZE - 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = x + 1
        self.rect.y = y + 1
        self.speed = 4
        
        # Item mechanics
        self.inverted_timer = 0
        self.inverted = False
        self.has_key = False

    def update(self, walls):
        if self.inverted_timer > 0:
            self.inverted_timer -= 1
        else:
            self.inverted = False

        keys = pygame.key.get_pressed()
        dx = 0
        dy = 0

        up_key = pygame.K_DOWN if self.inverted else pygame.K_UP
        down_key = pygame.K_UP if self.inverted else pygame.K_DOWN
        left_key = pygame.K_RIGHT if self.inverted else pygame.K_LEFT
        right_key = pygame.K_LEFT if self.inverted else pygame.K_RIGHT

        if keys[left_key]: dx = -self.speed
        if keys[right_key]: dx = self.speed
        if keys[up_key]: dy = -self.speed
        if keys[down_key]: dy = self.speed

        self.rect.x += dx
        self.collide_with_walls(walls, dx, 0)
        self.rect.y += dy
        self.collide_with_walls(walls, 0, dy)

    def collide_with_walls(self, walls, dx, dy):
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                if dx > 0: self.rect.right = wall.rect.left
                if dx < 0: self.rect.left = wall.rect.right
                if dy > 0: self.rect.bottom = wall.rect.top
                if dy < 0: self.rect.top = wall.rect.bottom

class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = load_image("hedge.png", (TILE_SIZE, TILE_SIZE), HEDGE_GREEN)
        if not os.path.exists("hedge.png"):
            pygame.draw.rect(self.image, (15, 30, 15), (5, 5, TILE_SIZE-10, TILE_SIZE-10))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = load_image("exit.png", (TILE_SIZE, TILE_SIZE), GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Item(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = load_image("item.png", (TILE_SIZE - 20, TILE_SIZE - 20), PURPLE)
        self.rect = self.image.get_rect()
        self.rect.x = x + 10
        self.rect.y = y + 10

class Key(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = load_image("key.png", (TILE_SIZE - 20, TILE_SIZE - 20), GOLD)
        self.rect = self.image.get_rect()
        self.rect.x = x + 10
        self.rect.y = y + 10

class Trigger(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 0)) # Invisible
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Monster(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, is_boss=False):
        super().__init__()
        self.direction = direction
        self.speed = 3 if not is_boss else 0
        self.is_boss = is_boss
        
        size = (TILE_SIZE - 10, TILE_SIZE - 10)
        if is_boss:
            size = (TILE_SIZE, TILE_SIZE) # Boss is bigger

        monster_imgs = ["monster1.jpg", "monster2.jpg", "monster3.png", "monster4.jpg"]
        if is_boss:
            chosen_img = "monster4.jpg" # Boss uses the 4th one
        else:
            chosen_img = random.choice(monster_imgs)
            
        self.image = load_image(chosen_img, size, RED)
        self.rect = self.image.get_rect()
        self.rect.centerx = x + TILE_SIZE // 2
        self.rect.centery = y + TILE_SIZE // 2

    def update(self, walls):
        if self.is_boss:
            return # Boss doesn't move immediately
            
        dx = 0
        dy = 0
        
        if self.direction == 'H':
            dx = self.speed
        elif self.direction == 'V':
            dy = self.speed

        self.rect.x += dx
        self.collide_with_walls(walls, dx, 0)
        self.rect.y += dy
        self.collide_with_walls(walls, 0, dy)

    def collide_with_walls(self, walls, dx, dy):
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                if dx > 0:
                    self.rect.right = wall.rect.left
                    self.speed *= -1
                elif dx < 0:
                    self.rect.left = wall.rect.right
                    self.speed *= -1
                elif dy > 0:
                    self.rect.bottom = wall.rect.top
                    self.speed *= -1
                elif dy < 0:
                    self.rect.top = wall.rect.bottom
                    self.speed *= -1

def create_level(level_index):
    walls = pygame.sprite.Group()
    monsters = pygame.sprite.Group()
    exits = pygame.sprite.Group()
    items = pygame.sprite.Group()
    keys_group = pygame.sprite.Group()
    triggers = pygame.sprite.Group()
    player = None

    if level_index >= len(levels):
        return None, None, None, None, None, None, None

    current_map = levels[level_index]

    x = 0
    y = 0
    for row in current_map:
        for col in row:
            if col == "#": walls.add(Wall(x, y))
            elif col == "P": player = Player(x, y)
            elif col == "E": exits.add(Exit(x, y))
            elif col == "I": items.add(Item(x, y))
            elif col == "K": keys_group.add(Key(x, y))
            elif col == "H": monsters.add(Monster(x, y, 'H'))
            elif col == "V": monsters.add(Monster(x, y, 'V'))
            elif col == "T": triggers.add(Trigger(x, y))
            x += TILE_SIZE
        y += TILE_SIZE
        x = 0
        
    return player, walls, monsters, exits, items, keys_group, triggers

def draw_text(text, font, text_col, x, y, center=False):
    img = font.render(text, True, text_col)
    if center:
        rect = img.get_rect(center=(x, y))
        screen.blit(img, rect)
    else:
        screen.blit(img, (x, y))

def main():
    current_level_index = 0
    player, walls, monsters, exits, items, keys_group, triggers = create_level(current_level_index)
    
    bg_sprites = pygame.sprite.Group()
    bg_sprites.add(walls)
    bg_sprites.add(exits)

    font_large = pygame.font.SysFont("Arial", 45, bold=True)
    font_small = pygame.font.SysFont("Arial", 30)
    font_ui = pygame.font.SysFont("Arial", 20, bold=True)
    
    game_over = False
    game_won = "" # Empty string means not won. States: "PRISON", "NEWSPAPER", "FINAL_TEXT"
    in_menu = True
    
    effect_message = ""
    effect_timer = 0
    
    boss_event_active = False
    boss_pause_timer = 0

    running = True
    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            if in_menu:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        start_button_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, 400, 200, 60)
                        if start_button_rect.collidepoint(event.pos):
                            in_menu = False
                            
            elif game_won != "":
                # Handle sequence clicks
                if event.type in [pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN]:
                    if game_won == "PRISON":
                        game_won = "NEWSPAPER"
                    elif game_won == "NEWSPAPER":
                        game_won = "FINAL_TEXT"
                    elif game_won == "FINAL_TEXT":
                        # Restart
                        in_menu = True
                        game_won = ""
                        current_level_index = 0
                        player, walls, monsters, exits, items, keys_group, triggers = create_level(current_level_index)
                        bg_sprites.empty()
                        bg_sprites.add(walls)
                        bg_sprites.add(exits)
                        game_over = False
                        effect_message = ""
                        boss_event_active = False
                        boss_pause_timer = 0
            else:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r and game_over:
                        current_level_index = 0
                        player, walls, monsters, exits, items, keys_group, triggers = create_level(current_level_index)
                        bg_sprites.empty()
                        bg_sprites.add(walls)
                        bg_sprites.add(exits)
                        game_over = False
                        effect_message = ""
                        boss_event_active = False
                        boss_pause_timer = 0

        if in_menu:
            # Draw background
            menu_bg = load_image("menu_bg.png", (SCREEN_WIDTH, SCREEN_HEIGHT), BLACK)
            screen.blit(menu_bg, (0, 0))
            
            # Dark overlay for better logo contrast
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(120)
            overlay.fill(BLACK)
            screen.blit(overlay, (0,0))
            
            logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")
            if os.path.exists(logo_path):
                logo_img = pygame.image.load(logo_path).convert()
                logo_img.set_colorkey(WHITE)
                logo_img = pygame.transform.scale(logo_img, (600, 200))
                screen.blit(logo_img, (SCREEN_WIDTH//2 - 300, 100))
            else:
                draw_text("ROLL OVER !", font_large, YELLOW, SCREEN_WIDTH//2, 200, center=True)
            
            start_button_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, 400, 200, 60)
            mouse_pos = pygame.mouse.get_pos()
            if start_button_rect.collidepoint(mouse_pos):
                pygame.draw.rect(screen, (200, 200, 200), start_button_rect, border_radius=10)
            else:
                pygame.draw.rect(screen, WHITE, start_button_rect, border_radius=10)
                
            draw_text("START", font_large, BLACK, SCREEN_WIDTH//2, 430, center=True)
            pygame.display.flip()
            continue
            
        if game_won != "":
            if game_won == "PRISON":
                screen.fill(BLACK)
                prison_img = load_image("prison_scene.png", (SCREEN_WIDTH, SCREEN_HEIGHT - 100), DARK_GRAY)
                screen.blit(prison_img, (0, 0))
                # Dialogue Box
                pygame.draw.rect(screen, (20, 20, 20), (0, SCREEN_HEIGHT - 100, SCREEN_WIDTH, 100))
                pygame.draw.rect(screen, WHITE, (0, SCREEN_HEIGHT - 100, SCREEN_WIDTH, 100), 2) # Border
                draw_text('Police: "He could not remembered what he had done in the past"', font_small, WHITE, SCREEN_WIDTH//2, SCREEN_HEIGHT - 60, center=True)
                draw_text('(Click to continue)', font_ui, YELLOW, SCREEN_WIDTH - 90, SCREEN_HEIGHT - 20, center=True)
                
            elif game_won == "NEWSPAPER":
                screen.fill(BLACK)
                news_img = load_image("newspaper_scene.png", (SCREEN_WIDTH, SCREEN_HEIGHT), DARK_GRAY)
                screen.blit(news_img, (0, 0))
                
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                overlay.set_alpha(150)
                overlay.fill(BLACK)
                screen.blit(overlay, (0,0))
                draw_text("Click to read the article...", font_large, YELLOW, SCREEN_WIDTH//2, SCREEN_HEIGHT//2, center=True)
                
            elif game_won == "FINAL_TEXT":
                screen.fill(BLACK)
                news_img = load_image("newspaper_scene.png", (SCREEN_WIDTH, SCREEN_HEIGHT), DARK_GRAY)
                screen.blit(news_img, (0, 0))
                
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                overlay.set_alpha(220)
                overlay.fill(BLACK)
                screen.blit(overlay, (0,0))
                
                text1 = "An adult ran gone mad and ran over all"
                text2 = "of his beloved cat in this maze in the garden."
                text3 = "Result in lifetime penalty..."
                
                draw_text(text1, font_small, WHITE, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 40, center=True)
                draw_text(text2, font_small, WHITE, SCREEN_WIDTH//2, SCREEN_HEIGHT//2, center=True)
                draw_text(text3, font_small, RED, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 60, center=True)
                
                draw_text("(Click to Restart Game)", font_ui, YELLOW, SCREEN_WIDTH//2, SCREEN_HEIGHT - 40, center=True)

            pygame.display.flip()
            continue

        screen.fill(DULL_GREEN)

        # Boss Pause Logic
        if boss_pause_timer > 0:
            boss_pause_timer -= 1
            if boss_pause_timer == 0:
                effect_message = ""
        else:
            if not game_over and game_won == "":
                if player: player.update(walls)
                monsters.update(walls)
                
                if effect_timer > 0: effect_timer -= 1
                else: effect_message = ""

                # Check triggers
                if player:
                    hit_trigger = pygame.sprite.spritecollideany(player, triggers)
                    if hit_trigger:
                        hit_trigger.kill()
                        # Spawn Boss Monster
                        boss_x = hit_trigger.rect.x + TILE_SIZE
                        boss_y = hit_trigger.rect.y
                        monsters.add(Monster(boss_x, boss_y, 'V', is_boss=True))
                        boss_pause_timer = 3 * FPS
                        effect_message = "You can't escape this, It's your fate."
                        boss_event_active = True

                # Check items
                if player:
                    collided_item = pygame.sprite.spritecollideany(player, items)
                    if collided_item:
                        collided_item.kill()
                        effect = random.choice(["invert", "kill"])
                        if effect == "invert":
                            player.inverted = True
                            player.inverted_timer = 7 * FPS
                            effect_message = "WARNING: CONTROLS INVERTED (7s)!"
                            effect_timer = 3 * FPS
                        elif effect == "kill":
                            if len(monsters) > 0:
                                monster_to_kill = random.choice(monsters.sprites())
                                monster_to_kill.kill()
                                effect_message = "BOOM! A MONSTER WAS DESTROYED!"
                                effect_timer = 3 * FPS
                            else:
                                effect_message = "NO MONSTERS TO DESTROY!"
                                effect_timer = 2 * FPS

                # Check keys
                if player:
                    collided_key = pygame.sprite.spritecollideany(player, keys_group)
                    if collided_key:
                        collided_key.kill()
                        player.has_key = True
                        effect_message = "KEY OBTAINED! THE DOOR IS UNLOCKED."
                        effect_timer = 3 * FPS

                # Check monster collisions
                if player and pygame.sprite.spritecollideany(player, monsters):
                    game_over = True
                
                # Check exit collisions
                if player and pygame.sprite.spritecollideany(player, exits):
                    if player.has_key:
                        current_level_index += 1
                        result = create_level(current_level_index)
                        if result[0] is None:
                            game_won = "PRISON"
                        else:
                            player, walls, monsters, exits, items, keys_group, triggers = result
                            bg_sprites.empty()
                            bg_sprites.add(walls)
                            bg_sprites.add(exits)
                            effect_message = ""
                            effect_timer = 0
                            boss_event_active = False
                    else:
                        # Don't let player proceed, bounce back slightly
                        keys_pressed = pygame.key.get_pressed()
                        player.rect.x -= player.speed if keys_pressed[pygame.K_RIGHT] else -player.speed if keys_pressed[pygame.K_LEFT] else 0
                        player.rect.y -= player.speed if keys_pressed[pygame.K_DOWN] else -player.speed if keys_pressed[pygame.K_UP] else 0
                        
                        if effect_message != "YOU NEED THE KEY TO EXIT!":
                            effect_message = "YOU NEED THE KEY TO EXIT!"
                            effect_timer = 2 * FPS

        # Draw Base Level
        bg_sprites.draw(screen)
        items.draw(screen)
        keys_group.draw(screen)
        
        # --- DRAW GLOOMY FOG ---
        if player and game_won == "":
            fog = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            fog.fill((0, 0, 0)) # Pitch black
            fog.set_colorkey((255, 0, 255)) # Magenta is transparent
            pygame.draw.circle(fog, (255, 0, 255), player.rect.center, 130)
            fog.set_alpha(210) # Gloomy atmosphere
            screen.blit(fog, (0, 0))
            
        monsters.draw(screen)
        
        if player and not game_over and game_won == "":
            # Draw the giant car centered on the normal-sized hitbox
            draw_rect = player.visual_image.get_rect(center=player.rect.center)
            screen.blit(player.visual_image, draw_rect)

        # Draw UI
        if game_won == "":
            draw_text(f"Level: {current_level_index + 1} / {len(levels)}", font_ui, WHITE, 10, 10)
            if player and player.has_key:
                draw_text("KEY: YES", font_ui, GOLD, 10, 40)
            elif player and not player.has_key:
                draw_text("KEY: NO", font_ui, RED, 10, 40)
        
        if effect_message and (effect_timer > 0 or boss_pause_timer > 0):
            if boss_pause_timer > 0:
                draw_text(effect_message, font_large, RED, SCREEN_WIDTH//2, SCREEN_HEIGHT//2, center=True)
            else:
                draw_text(effect_message, font_ui, YELLOW, SCREEN_WIDTH//2, 20, center=True)

        if game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(150)
            overlay.fill(BLACK)
            screen.blit(overlay, (0,0))
            draw_text("GAME OVER!", font_large, RED, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50, center=True)
            draw_text("Press 'R' to Restart from Level 1", font_small, WHITE, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 30, center=True)
        
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
