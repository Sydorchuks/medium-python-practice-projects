import math
import random
import time
import json
import os
import pygame
pygame.init()

WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Aim Trainer")

WHITE_THEME = {
    "bg": "blue",
    "bar": "grey",
    "text": "black",
    "end_text": "white"
}

BLACK_THEME = {
    "bg": "black",
    "bar": "white",
    "text": "black",
    "end_text": "white"
}

themes = {"white": WHITE_THEME, "black": BLACK_THEME}
current_theme = "white"

settings = {
    "difficulty": "medium",
    "theme": "white",
    "player_name": ""
}

# --- CHANGES MADE ---
HIGHSCORE_FILE = "highscores.json"

# --- CHANGES MADE ---
def get_difficulty_multiplier():
    if settings["difficulty"] == "easy":
        return 1
    elif settings["difficulty"] == "medium":
        return 2
    elif settings["difficulty"] == "hard":
        return 3

def apply_difficulty():
    global TARGET_INCREMENT, LIVES
    if settings["difficulty"] == "easy":
        TARGET_INCREMENT = 1000
        LIVES = 5
    elif settings["difficulty"] == "medium":
        TARGET_INCREMENT = 400
        LIVES = 3
    elif settings["difficulty"] == "hard":
        TARGET_INCREMENT = 200
        LIVES = 1

apply_difficulty()

TARGET_EVENT = pygame.USEREVENT
TARGET_PADDING = 30
TOP_BAR_HEIGHT = 50

LABEL_FONT = pygame.font.SysFont("comicsans", 24)

class Target:
    MAX_SIZE = 30
    GROWTH_RATE = 0.2
    COLOR = "red"
    SECOND_COLOR = "white"

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 0
        self.grow = True

    def update(self):
        if self.size + self.GROWTH_RATE >= self.MAX_SIZE:
            self.grow = False

        if self.grow:
            self.size += self.GROWTH_RATE
        else:
            self.size -= self.GROWTH_RATE

    def draw(self, win):
        pygame.draw.circle(win, self.COLOR, (self.x, self.y), self.size)
        pygame.draw.circle(win, self.SECOND_COLOR, (self.x, self.y), self.size * 0.8)
        pygame.draw.circle(win, self.COLOR, (self.x, self.y), self.size * 0.6)
        pygame.draw.circle(win, self.SECOND_COLOR, (self.x, self.y), self.size * 0.4)

    def collide(self, x, y):
        dis = math.sqrt((self.x - x) ** 2 + (self.y - y) ** 2)
        return dis <= self.size

def draw(win, targets):
    win.fill(themes[settings["theme"]]["bg"])
    for target in targets:
        target.draw(win)

def format_time(secs):
    milli = math.floor(int(secs * 1000 % 1000) / 100)
    seconds = int(round(secs % 60, 1))
    minutes = int(secs // 60)
    return f"{minutes:02d}:{seconds:02d}.{milli}"

def draw_top_bar(win, elapsed_time, targets_pressed, misses):
    pygame.draw.rect(win, themes[settings["theme"]]["bar"], (0, 0, WIDTH, TOP_BAR_HEIGHT))
    text_color = themes[settings["theme"]]["text"]
    time_label = LABEL_FONT.render(f"Time: {format_time(elapsed_time)}", 1, text_color)
    speed = round(targets_pressed / elapsed_time, 1)
    speed_label = LABEL_FONT.render(f"Speed: {speed} t/s", 1, text_color)
    hits_label = LABEL_FONT.render(f"Hits: {targets_pressed}", 1, text_color)
    lives_label = LABEL_FONT.render(f"Lives: {LIVES - misses}", 1, text_color)

    win.blit(time_label, (5, 5))
    win.blit(speed_label, (200, 5))
    win.blit(hits_label, (450, 5))
    win.blit(lives_label, (650, 5))

# --- CHANGES MADE ---
def load_highscores():
    if os.path.exists(HIGHSCORE_FILE):
        with open(HIGHSCORE_FILE, 'r') as f:
            return json.load(f)
    return []

def save_highscores(scores):
    with open(HIGHSCORE_FILE, 'w') as f:
        json.dump(scores, f, indent=2)

def update_highscores(player, score):
    highscores = load_highscores()
    updated = False
    for entry in highscores:
        if entry['name'] == player:
            if entry['score'] < score:
                entry['score'] = score
            updated = True
            break
    if not updated:
        highscores.append({"name": player, "score": score})
    highscores.sort(key=lambda x: x['score'], reverse=True)
    save_highscores(highscores[:5])

def draw_highscores(win):
    highscores = load_highscores()
    y = 450
    for i, entry in enumerate(highscores):
        label = LABEL_FONT.render(f"{i+1}. {entry['name']} - {entry['score']}", 1, themes[settings["theme"]]["end_text"])
        win.blit(label, (get_middle(label), y))
        y += 30

def end_screen(win, elapsed_time, targets_pressed, clicks):
    win.fill(themes[settings["theme"]]["bg"])
    color = themes[settings["theme"]]["end_text"]
    time_label = LABEL_FONT.render(f"Time: {format_time(elapsed_time)}", 1, color)
    speed = round(targets_pressed / elapsed_time, 1)
    speed_label = LABEL_FONT.render(f"Speed: {speed} t/s", 1, color)
    hits_label = LABEL_FONT.render(f"Hits: {targets_pressed}", 1, color)
    accuracy = round(targets_pressed / clicks * 100, 1)
    accuracy_label = LABEL_FONT.render(f"Accuracy: {accuracy}", 1, color)

    score = round(targets_pressed * get_difficulty_multiplier())
    update_highscores(settings["player_name"], score)

    win.blit(time_label, (get_middle(time_label), 100))
    win.blit(speed_label, (get_middle(speed_label), 150))
    win.blit(hits_label, (get_middle(hits_label), 200))
    win.blit(accuracy_label, (get_middle(accuracy_label), 250))

    draw_highscores(win)

    button_width, button_height = 200, 50
    button_x = WIDTH // 2 - button_width // 2
    button_y = 350
    pygame.draw.rect(win, "green", (button_x, button_y, button_width, button_height))
    button_label = LABEL_FONT.render("Play Again", 1, "white")
    win.blit(button_label, (get_middle(button_label), button_y + 10))

    pygame.display.update()

    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                run = False
                main()  # Start new game
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if button_x <= mx <= button_x + button_width and button_y <= my <= button_y + button_height:
                    run = False
                    main()  # Start new game

def get_middle(surface):
    return WIDTH / 2 - surface.get_width() / 2

# --- CHANGES MADE ---
def settings_screen():
    selecting = True
    input_active = True
    player_name = ""
    while selecting:
        WIN.fill("blue")
        title = LABEL_FONT.render("START", 1, "white")
        theme_color = "black" if settings["theme"] == "black" else "white"
        theme_label = LABEL_FONT.render(f"Theme (T): {settings['theme']}", 1, theme_color)

        difficulty_color = "yellow" if settings['difficulty'] == 'medium' else ("red" if settings['difficulty'] == 'hard' else "green")
        diff_label = LABEL_FONT.render(f"Difficulty (1-Easy, 2-Medium, 3-Hard): {settings['difficulty']}", 1, difficulty_color)
        name_label = LABEL_FONT.render(f"Enter Name: {player_name}|", 1, "white")
        start_label = LABEL_FONT.render("Press Enter to Start", 1, "white")

        WIN.blit(title, (get_middle(title), 50))
        WIN.blit(theme_label, (get_middle(theme_label), 150))
        WIN.blit(diff_label, (get_middle(diff_label), 200))
        WIN.blit(name_label, (get_middle(name_label), 300))
        WIN.blit(start_label, (get_middle(start_label), 400))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.KEYDOWN:
                if input_active:
                    if event.key == pygame.K_RETURN:
                        if player_name.strip() != "":
                            settings["player_name"] = player_name.strip()
                            selecting = False
                    elif event.key == pygame.K_BACKSPACE:
                        player_name = player_name[:-1]
                    elif event.unicode.isprintable() and len(player_name) < 15:
                        player_name += event.unicode
                if event.key == pygame.K_t:
                    settings["theme"] = "black" if settings["theme"] == "white" else "white"
                if event.key == pygame.K_1:
                    settings["difficulty"] = "easy"
                    apply_difficulty()
                if event.key == pygame.K_2:
                    settings["difficulty"] = "medium"
                    apply_difficulty()
                if event.key == pygame.K_3:
                    settings["difficulty"] = "hard"
                    apply_difficulty()

def main():
    settings_screen()
    run = True
    targets = []
    clock = pygame.time.Clock()
    targets_pressed = 0
    clicks = 0
    misses = 0
    start_time = time.time()

    pygame.time.set_timer(TARGET_EVENT, TARGET_INCREMENT)

    while run:
        clock.tick(60)
        click = False
        mouse_pos = pygame.mouse.get_pos()
        elapsed_time = time.time() - start_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            if event.type == TARGET_EVENT:
                x = random.randint(TARGET_PADDING, WIDTH - TARGET_PADDING)
                y = random.randint(TARGET_PADDING + TOP_BAR_HEIGHT, HEIGHT - TARGET_PADDING)
                targets.append(Target(x, y))
            if event.type == pygame.MOUSEBUTTONDOWN:
                click = True
                clicks += 1

        for target in targets[:]:
            target.update()
            if target.size <= 0:
                targets.remove(target)
                misses += 1
            if click and target.collide(mouse_pos[0], mouse_pos[1]):
                targets.remove(target)
                targets_pressed += 1

        if misses >= LIVES:
            end_screen(WIN, elapsed_time, targets_pressed, clicks)
            return

        draw(WIN, targets)
        draw_top_bar(WIN, elapsed_time, targets_pressed, misses)
        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()
