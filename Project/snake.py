import turtle
import random
import time

# Screen
screen = turtle.Screen()
screen.title("🐑 Space Sheep Shooter PRO")
screen.bgcolor("black")
screen.setup(width=600, height=600)
screen.tracer(0)

# 🐑 Sheep Shape
sheep_shape = (
    (0,10),(6,16),(12,10),(18,16),(24,10),
    (18,4),(24,-2),(12,-8),(0,-2),(-12,-8),
    (-24,-2),(-18,4),(-24,10),(-18,16),(-12,10),(-6,16)
)
screen.register_shape("sheep", sheep_shape)

# 🌌 Stars
stars = []
for _ in range(70):
    star = turtle.Turtle()
    star.shape("circle")
    star.color(random.choice(["white", "#aaaaaa", "#dddddd"]))
    star.shapesize(0.1, 0.1)
    star.penup()
    star.goto(random.randint(-300, 300), random.randint(-300, 300))
    stars.append(star)

# 🐑 Player
player = turtle.Turtle()
player.shape("sheep")
player.color("white")
player.shapesize(1.2, 1.2)
player.penup()
player.goto(0, -250)
player.setheading(90)

# 🔫 Bullets
bullets = []
bullet_speed = 22

# 👾 Enemies
enemies = []
for _ in range(5):
    enemy = turtle.Turtle()
    enemy.shape("circle")
    enemy.color(random.choice(["#ff4d4d", "#ff944d", "#ff1a75", "#ffcc00"]))
    enemy.penup()
    enemy.goto(random.randint(-250, 250), random.randint(200, 320))
    enemies.append(enemy)

enemy_speed = 2

# 🎯 Score
score = 0
pen = turtle.Turtle()
pen.color("white")
pen.penup()
pen.hideturtle()
pen.goto(0, 260)
pen.write("Score: 0", align="center", font=("Arial", 16, "bold"))

# Controls
def move_left():
    if player.xcor() > -280:
        player.setx(player.xcor() - 30)

def move_right():
    if player.xcor() < 280:
        player.setx(player.xcor() + 30)

def fire_bullet():
    bullet = turtle.Turtle()
    bullet.shape("square")
    bullet.color("#ffff00")
    bullet.shapesize(0.3, 1.2)
    bullet.penup()
    bullet.goto(player.xcor(), player.ycor() + 15)
    bullet.setheading(90)
    bullets.append(bullet)

screen.listen()
screen.onkeypress(move_left, "Left")
screen.onkeypress(move_right, "Right")
screen.onkeypress(fire_bullet, "space")

# Collision
def is_collision(a, b):
    return a.distance(b) < 20

# Game loop
running = True

while running:
    screen.update()
    time.sleep(0.02)

    # 🌌 Stars movement
    for star in stars:
        star.sety(star.ycor() - random.uniform(0.5, 2))
        if star.ycor() < -300:
            star.goto(random.randint(-300, 300), 300)

    # 👾 Enemy movement (DOWNWARD ATTACK)
    for enemy in enemies:
        enemy.setx(enemy.xcor() + enemy_speed)

        # Continuous downward movement
        enemy.sety(enemy.ycor() - 1.5)

        # Bounce left/right
        if enemy.xcor() > 280 or enemy.xcor() < -280:
            enemy_speed *= -1

        # Collision with player
        if is_collision(player, enemy):
            running = False

        # If reaches bottom → game over
        if enemy.ycor() < -260:
            running = False

    # 🔫 Bullets
    for bullet in bullets[:]:
        bullet.sety(bullet.ycor() + bullet_speed)

        if bullet.ycor() > 300:
            bullet.hideturtle()
            bullets.remove(bullet)

        for enemy in enemies:
            if is_collision(bullet, enemy):
                bullet.hideturtle()
                if bullet in bullets:
                    bullets.remove(bullet)

                # 💥 Hit flash
                enemy.color("white")
                screen.update()
                time.sleep(0.03)

                # Respawn enemy at top
                enemy.goto(random.randint(-250, 250), random.randint(250, 320))
                enemy.color(random.choice(["#ff4d4d", "#ff944d", "#ff1a75", "#ffcc00"]))

                score += 10

                # Increase difficulty
                if score % 50 == 0:
                    enemy_speed += 0.3

                pen.clear()
                pen.write(f"Score: {score}", align="center",
                          font=("Arial", 16, "bold"))

# 💀 Game Over
pen.goto(0, 0)
pen.color("red")
pen.write("GAME OVER", align="center", font=("Arial", 28, "bold"))

turtle.done()