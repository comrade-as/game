import pygame
import random
import os
import sys

pygame.init()
pygame.font.init()

# Настраиваем экран
size = width, height = (1280, 720)
screen = pygame.display.set_mode(size)
pygame.display.set_caption('Arcanoid')
screen_rect = (0, 0, width, height)

# Настраиваем переменные
IsStart = 0
Lives = 5
Score = 0
Combo = 1
clock = pygame.time.Clock()
fps = 50

# Заносим звуки в переменные
BounceSNew = pygame.mixer.Sound('data/Sounds/BlockHit.ogg')
BouncePlayerS = pygame.mixer.Sound('data/Sounds/ArcPlateHit.ogg')
BrickDestroyS = pygame.mixer.Sound('data/Sounds/BlockHitBreaking.ogg')


# Создаём удобную функцию загрузки  спрайтов

def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def load_level(filename):
    filename = "data/level/" + filename
    # читаем уровень,  убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    global level
    level = list(map(lambda x: x.ljust(max_width, '.'), level_map))

    return level


def generate_level(level):
    brk_x, brk_y = 64, 100

    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] != '.':
                Brick(brk_x, brk_y, level[y][x])
                brk_x += 128
            else:
                brk_x += 128
        brk_y += 32
        brk_x -= 9 * 128


# Создаём класс платформы
class Paddle(pygame.sprite.Sprite):
    image = load_image('x.png')

    def __init__(self, x=540, y=640, razmer=200):
        super().__init__(all_sprites)
        self.add(P1)
        if razmer == 200:
            self.image = Paddle.image
        elif razmer < 200:
            self.image = load_image('05x.png')
        elif razmer > 200:
            self.image = load_image('2x.png')
        self.rect = pygame.Rect(x, y, razmer, self.image.get_rect()[3])
        self.image = pygame.transform.scale(Paddle.image, (razmer, self.image.get_rect()[3]))
        self.rect.x = x
        self.rect.y = y
        self.vx = 0
        self.vy = 0
        self.speed = 1

    def update(self):
        self.rect = self.rect.move(self.vx, self.vy)


# Создаём класс кирпичика
class Brick(pygame.sprite.Sprite):
    brick_color = ['Gray', 'Green', 'Blue', 'Red', 'Orange']
    image = load_image(f'Bricks/{brick_color[0]}.png')

    def __init__(self, x, y, color):
        super().__init__(all_sprites)
        self.add(Bricks)
        self.image = Brick.image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vx = 0
        self.vy = 0
        self.colorv = color

        for i in range(1, 5):
            if self.colorv == str(i):
                self.image = load_image(f'Bricks/{Brick.brick_color[i]}.png')

    def update(self):
        self.rect = self.rect.move(self.vx, self.vy)
        # При соприкосновении мячика с кирпичиком
        if pygame.sprite.spritecollide(self, BallG, False):
            global Combo
            global Score
            Score += 5 * Combo
            Combo += 1
            BounceSNew.play()
            self.kill()
            x = (self.rect.x - 64) // 128
            y = (self.rect.y - 100) // 32

            if self.image == Brick.image:
                particle_count = 7
                # возможные скорости
                numbers = range(-3, 4)
                for _ in range(particle_count):
                    BrickBlow(self.rect.x, self.rect.y, random.choice(numbers), random.choice(numbers))
                BrickDestroyS.play()
                if prize[y][x]:
                    Surprise(self.rect.x + 64, self.rect.y + 32, prize[y][x])
            else:
                level[y] = list(level[y])
                level[y][x] = str(int(level[y][x]) - 1)
                Brick(self.rect.x, self.rect.y, level[y][x])


class Surprise(pygame.sprite.Sprite):
    def __init__(self, x, y, vid_prize):
        super().__init__(all_sprites)
        self.vid_prize = vid_prize  # 1-уменьшение, 2- увеличение, 3 -замедление, 4 - ускорение, 5 - шарик
        self.image = load_image(f'Bonus/{self.vid_prize}.png')
        self.rect = pygame.Rect(x, y, self.image.get_rect()[2], self.image.get_rect()[3])
        self.vx = 0
        self.vy = 1

    def update(self):
        global Player
        global PBall
        self.rect = self.rect.move(self.vx, self.vy)
        if pygame.sprite.spritecollide(self, P1, False):
            x_new, y_new = Player.rect.x, Player.rect.y
            if self.vid_prize == 1:
                P1.remove(Player)
                Player.kill()
                if Player.rect.width <= 100:
                    width_new = 100
                else:
                    width_new = Player.rect.width // 2
                    x_new += width_new // 2
                Player = Paddle(x_new, y_new, width_new)
                self.kill()
            if self.vid_prize == 2:
                P1.remove(Player)
                Player.kill()
                if Player.rect.width >= 400:
                    width_new = 400
                else:
                    width_new = Player.rect.width * 2
                    x_new -= width_new // 4
                Player = Paddle(x_new, y_new, width_new)
                self.kill()
            if self.vid_prize == 3:
                if Player.speed <= 0.5:
                    Player.speed = 0.5
                else:
                    Player.speed *= 0.5
                self.kill()
            if self.vid_prize == 4:
                if Player.speed >= 2:
                    Player.speed = 2
                else:
                    Player.speed *= 2
                self.kill()
            if self.vid_prize == 5:
                PBall.rect.x
                PBall = Ball(PBall.rect.x, PBall.rect.y, -PBall.vx, -PBall.vy)
                self.kill()
            self.vy = 0
        else:
            self.vy = 1


# Создаём класс мячика
class Ball(pygame.sprite.Sprite):
    image = load_image('Ball.png')

    def __init__(self, x=628, y=605, vx=0, vy=0):
        super().__init__(all_sprites)
        self.add(BallG)  # Добавляем мяч в специальную группу для взаимодействий
        self.image = Ball.image
        pygame.transform.scale(Ball.image, (30, 30))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vx = vx
        self.vy = vy
        self.rdirb = 0
        self.rdirp = 0

    def update(self):
        self.rect = self.rect.move(self.vx * Player.speed, self.vy * Player.speed)  # Двигаем мячик
        # При соприкосновении с кирпичиком меняем направление и проигрываем звук
        if pygame.sprite.spritecollide(self, Bricks, False):

            BounceSNew.play()

            self.rdirb = random.randint(1, 3)
            if self.rdirb == 1:
                self.vx = self.vx
                self.vy = -self.vy
            elif self.rdirb == 2:
                self.vx = -self.vx
                self.vy = -self.vy
            elif self.rdirb == 3:
                self.vx = -self.vx
                self.vy = self.vy

        # Отскакиваем от платформы
        if pygame.sprite.spritecollide(self, P1, False):
            global Combo
            BouncePlayerS.play()
            Combo = 1
            self.rdirp = random.randint(0, 1)

            if self.rdirp:
                if vpravo and abs(self.vy) < 9:
                    self.vy += 1
                self.vx = self.vx
                self.vy = -self.vy
            else:
                if not vpravo and abs(self.vy) > 1:
                    self.vy -= 1
                self.vx = -self.vx
                self.vy = -self.vy

                # Отскакиваем от границ экрана
        if pygame.sprite.spritecollideany(self, horizontal_borders):
            self.vy = -self.vy
        if pygame.sprite.spritecollideany(self, vertical_borders):
            self.vx = -self.vx

        # Мячик не поймали, теряем одну жизнь
        if self.rect.y >= height - 50:
            self.foul()

    # Функция старта мячика
    def go(self):
        self.vx = -4
        self.vy = -4

    # Функция для потери жизни
    def foul(self):
        global IsStart
        global Lives
        global Combo
        global PBall
        global Player
        self.vx = 0
        self.vy = 0
        Combo = 1
        BallG.remove(self)
        self.kill()
        if Lives and not BallG:
            PBall = Ball(628, 605)
            P1.remove(Player)
            Player.kill()
            Player = Paddle()
            IsStart = 0
            Lives -= 1


# Создаём класс под задний фон
class Background(pygame.sprite.Sprite):
    def __init__(self, x, y, image='level1.jpg'):
        super().__init__(all_sprites)
        filename = "level/" + image
        self.image = load_image(filename)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


# Создаём класс под анимацию уничтожения кирпичика
class BrickBlow(pygame.sprite.Sprite):
    fire = [load_image("piece.png")]
    for scale in (5, 10, 20):
        fire.append(pygame.transform.scale(fire[0], (scale, scale)))

    def __init__(self, x, y, dx, dy):
        super().__init__(all_sprites)
        self.image = random.choice(self.fire)
        self.rect = self.image.get_rect()

        # у каждой частицы своя скорость — это вектор
        self.velocity = [dx, dy]
        # и свои координаты
        self.rect.x, self.rect.y = x, y

        # гравитация будет одинаковой
        self.gravity = 2

        self.last_update = pygame.time.get_ticks()
        self.rot = 0
        self.rot_speed = 3

    def rotate(self):
        now = pygame.time.get_ticks()

        if now - self.last_update > 50:
            self.last_update = now
            self.rot = (self.rot + self.rot_speed) % 360
            new_image_rot = pygame.transform.rotate(self.image, self.rot)
            old_center = self.rect.center
            self.image = new_image_rot
            self.rect = self.image.get_rect()
            self.rect.center = old_center

    def update(self):
        # применяем гравитационный эффект:
        # движение с ускорением под действием гравитации
        self.velocity[1] += self.gravity
        self.rotate()

        # перемещаем частицу
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]

        # убиваем, если частица ушла за экран
        if not self.rect.colliderect(screen_rect):
            self.kill()


class Border(pygame.sprite.Sprite):
    # строго вертикальный или строго горизонтальный отрезок
    def __init__(self, x1, y1, x2, y2):
        super().__init__(all_sprites)
        if x1 == x2:  # вертикальная стенка
            self.add(vertical_borders)
            self.image = pygame.Surface([1, y2 - y1])
            self.rect = pygame.Rect(x1, y1, 1, y2 - y1)
        else:  # горизонтальная стенка
            self.add(horizontal_borders)
            self.image = pygame.Surface([x2 - x1, 1])
            self.rect = pygame.Rect(x1, y1, x2 - x1, 1)


def start_screen():
    intro_text = ["Игра Arcanoid",
                  "Цель - разбить все кирпичики",
                  "Кирпичики разного цвета",
                  "поэтому для разбивания требуется разное",
                  "количество касаний кирпичика",
                  "Самые крепкие - оранжевые,",
                  "их требуется ударить 4 раза,",
                  "ну а серые разбиваются сразу",
                  "Из разбитых кирпичиков иногда выпадают Сюрпризики",
                  "бывают приятные, а бывают не очень"]

    fon = pygame.transform.scale(load_image('fon.jpg'), (width, height))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(fps)


# Задаём шрифт игры и так-же создаём тексты
GameFont = pygame.font.SysFont('calibri', 30)
ScoreText = GameFont.render('Score: ' + str(Score), 1, (255, 255, 255))
ComboText = GameFont.render('Combo: ' + str(Combo), 1, (255, 255, 255))
LivesText = GameFont.render('Lives: ' + str(Lives), 1, (255, 255, 255))

# Создаём группы взаимодействий
all_sprites = pygame.sprite.Group()
P1 = pygame.sprite.Group()
BallG = pygame.sprite.Group()
Bricks = pygame.sprite.Group()

horizontal_borders = pygame.sprite.Group()
vertical_borders = pygame.sprite.Group()

Border(5, 5, width - 5, 5)
Border(5, 5, 5, height - 5)
Border(width - 5, 5, width - 5, height - 5)

k = 1
# Создаём объекты
BackGroundObj = Background(0, 0, f"level{k}.jpg")
Player = Paddle(540, 640)
PBall = Ball(628, 605)

start_screen()

prize = [[0] * 9 for _ in range(7)]
nabor_prize = random.choices(range(1, 6), k=8)
for i in range(8):
    x = random.randint(0, 6)
    y = random.randint(0, 8)
    if nabor_prize:
        prize[x][y] = nabor_prize.pop(-1)

generate_level(load_level(f"level{k}.txt"))

# Главный цикл игры
vpravo = False
running = True
while running:

    # Управление персонажем
    keys = pygame.key.get_pressed()

    if keys[pygame.K_RIGHT] and Player.rect.x < width - Player.rect.width:
        Player.rect.x += 6
        vpravo = not vpravo
        if not IsStart:
            PBall.rect.x += 6
    if keys[pygame.K_LEFT] and Player.rect.x > 0:
        Player.rect.x -= 6
        vpravo = not vpravo
        if not IsStart:
            PBall.rect.x -= 6

    # Проверка на уничтожение всех кирпичиков
    if not Bricks:
        k += 1

        BackGroundObj = Background(0, 0, f"level{k}.jpg")
        generate_level(load_level(f"level{k}.txt"))
        Player.kill()
        PBall.kill()
        Player = Paddle(540, 640)
        PBall = Ball(628, 605)
        IsStart = 0

    # При нажатии Space вызываем функцию старта у мячика
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and not IsStart and Lives:
            IsStart = 1
            PBall.go()

        if event.type == pygame.QUIT:
            running = False

    # Рендерим (рисуем) все объекты на экран
    screen.fill((0, 0, 0))

    ScoreText = GameFont.render('Score: ' + str(Score), 1, (255, 255, 255))
    ComboText = GameFont.render('Combo: ' + str(Combo), 1, (255, 255, 255))

    if Lives:
        LivesText = GameFont.render('Lives: ' + str(Lives), 1, (255, 255, 255))
    else:
        Player.kill()
        PBall.kill()
        BackGroundObj.kill()
        BackGroundObj = Background(0, 0, "gameover.jpg")

    for sprite in all_sprites:
        sprite.update()
    all_sprites.draw(screen)
    screen.blit(ScoreText, (20, 20))
    screen.blit(ComboText, (20, 660))
    screen.blit(LivesText, (20, 630))
    pygame.display.flip()
    pygame.time.delay(20)
    clock.tick(fps)
