import pygame
import random
import cv2   # ✅ for video playback

# Initialize pygame
pygame.init()
pygame.mixer.init()  # ✅ audio system

# Constants
WIDTH = 600
HEIGHT = 400
BLOCK_SIZE = 20
FPS = 8
MAX_CRASHES = 5
BOUNDARY_PADDING = 15

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GREY = (169, 169, 169)

# Display setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Snake but Reversed(Ragebait Edition)')

clock = pygame.time.Clock()
font = pygame.font.SysFont('arial', 20)
big_font = pygame.font.SysFont('arial', 30)

# Valid movement area
MIN_X = BOUNDARY_PADDING
MAX_X = WIDTH - BOUNDARY_PADDING - BLOCK_SIZE
MIN_Y = BOUNDARY_PADDING
MAX_Y = HEIGHT - BOUNDARY_PADDING - BLOCK_SIZE

# ✅ Load sounds
crash_sound = pygame.mixer.Sound("crash.wav")  # plays on each crash (except final)
# jumpscare.wav will be loaded when playing the video


# -------------------------------
# ✅ Jumpscare video + audio
# -------------------------------
def play_jumpscare_video(video_path, audio_path=None):
    cap = cv2.VideoCapture(video_path)

    # Play audio if available
    if audio_path:
        scream = pygame.mixer.Sound(audio_path)
        scream.play()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break  # video finished

        # Convert frame to Pygame surface
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
        frame_surface = pygame.transform.scale(frame_surface, (WIDTH, HEIGHT))

        screen.blit(frame_surface, (0, 0))
        pygame.display.update()

        # Allow quitting during playback
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cap.release()
                return

        # Delay for ~30 fps
        pygame.time.delay(33)

    cap.release()


# -------------------------------
# Snake class
# -------------------------------
class Snake:
    def __init__(self):
        self.body = [(MIN_X + BLOCK_SIZE * 2, MIN_Y + BLOCK_SIZE * 2),
                     (MIN_X + BLOCK_SIZE, MIN_Y + BLOCK_SIZE * 2),
                     (MIN_X, MIN_Y + BLOCK_SIZE * 2)]
        self.direction = 'RIGHT'
        self.crashes = 0
        self.speed = FPS

    def get_next_head(self, direction=None):
        if direction is None:
            direction = self.direction
        head_x, head_y = self.body[0]
        if direction == 'UP':
            return (head_x, head_y - BLOCK_SIZE)
        elif direction == 'DOWN':
            return (head_x, head_y + BLOCK_SIZE)
        elif direction == 'LEFT':
            return (head_x - BLOCK_SIZE, head_y)
        elif direction == 'RIGHT':
            return (head_x + BLOCK_SIZE, head_y)

    def move(self):
        new_head = self.get_next_head()
        self.body = [new_head] + self.body[:-1]

    def grow(self):
        self.body.append(self.body[-1])

    def crash(self):
        self.crashes += 1

    def draw(self):
        for segment in self.body:
            pygame.draw.rect(screen, GREEN, (*segment, BLOCK_SIZE, BLOCK_SIZE))

    def out_of_bounds(self, pos=None):
        if pos is None:
            pos = self.body[0]
        x, y = pos
        return x < MIN_X or x > MAX_X or y < MIN_Y or y > MAX_Y

    def auto_turn(self):
        directions = ['UP', 'DOWN', 'LEFT', 'RIGHT']
        random.shuffle(directions)
        for d in directions:
            if d == self.opposite_direction(self.direction):
                continue
            new_pos = self.get_next_head(direction=d)
            if not self.out_of_bounds(new_pos):
                self.direction = d
                return

    @staticmethod
    def opposite_direction(dir):
        return {
            'UP': 'DOWN',
            'DOWN': 'UP',
            'LEFT': 'RIGHT',
            'RIGHT': 'LEFT'
        }[dir]


# -------------------------------
# Fruit class
# -------------------------------
class Fruit:
    def __init__(self):
        self.position = self.spawn_inside_boundary()

    def spawn_inside_boundary(self):
        x = random.randrange(MIN_X, MAX_X + 1, BLOCK_SIZE)
        y = random.randrange(MIN_Y, MAX_Y + 1, BLOCK_SIZE)
        return (x, y)

    def spawn(self):
        self.position = self.spawn_inside_boundary()

    def draw(self):
        pygame.draw.rect(screen, RED, (*self.position, BLOCK_SIZE, BLOCK_SIZE))


def draw_boundary():
    pygame.draw.rect(
        screen, GREY,
        (BOUNDARY_PADDING, BOUNDARY_PADDING,
         WIDTH - 2 * BOUNDARY_PADDING, HEIGHT - 2 * BOUNDARY_PADDING),
        5
    )


def display_text(text, font, color, x, y):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))


# -------------------------------
# Main game loop
# -------------------------------
def game_loop():
    snake = Snake()
    fruit = Fruit()
    running = True
    game_over = False

    while running:
        screen.fill(BLACK)
        draw_boundary()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                # Reversed Controls
                if event.key == pygame.K_UP and snake.direction != 'UP':
                    snake.direction = 'DOWN'
                elif event.key == pygame.K_DOWN and snake.direction != 'DOWN':
                    snake.direction = 'UP'
                elif event.key == pygame.K_LEFT and snake.direction != 'LEFT':
                    snake.direction = 'RIGHT'
                elif event.key == pygame.K_RIGHT and snake.direction != 'RIGHT':
                    snake.direction = 'LEFT'

        if not game_over:
            next_head = snake.get_next_head()

            if snake.out_of_bounds(next_head):
                snake.crash()
                if snake.crashes >= MAX_CRASHES:
                    # ✅ Final crash → jumpscare video + scream
                    play_jumpscare_video("jumpscare.mp4", "jumpscare.wav")
                    game_over = True
                else:
                    # ✅ Normal crash sound
                    crash_sound.play()
                    snake.auto_turn()
            else:
                snake.move()

                if snake.body[0] == fruit.position:
                    snake.grow()
                    fruit.spawn()
                    snake.speed /= 0.75  # Increase speed on fruit eat (faster!)
                    clock.tick(max(1, snake.speed))

            snake.draw()
            fruit.draw()
            display_text(f'Speed: {int(snake.speed)}', font, WHITE, 10, 10)

        else:
            display_text('Game Over! Press Q to quit or R to restart.', big_font, RED, WIDTH // 6, HEIGHT // 2)

        pygame.display.update()

        if game_over:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_q]:
                running = False
            elif keys[pygame.K_r]:
                game_loop()

        clock.tick(snake.speed)

    pygame.quit()


# Start the game
game_loop()
