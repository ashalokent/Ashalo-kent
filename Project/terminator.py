import turtle
import time
import random

# Screen setup
screen = turtle.Screen()
screen.title("Snake Game")
screen.bgcolor("black")
screen.setup(width=600, height=600)
screen.tracer(0)

# Initial delay (speed control)
delay = 0.15   # 🔥 Increase this to slow the game

# Snake head
head = turtle.Turtle()
head.shape("square")
head.color("green")
head.penup()
head.goto(0, 0)
head.direction = "Stop"

# Food
food = turtle.Turtle()
food.shape("circle")
food.color("red")
food.penup()
food.goto(0, 100)

# Snake body
segments = []

# Score
score = 0
high_score = 0

# Score display
pen = turtle.Turtle()
pen.speed(0)
pen.color("white")
pen.penup()
pen.hideturtle()
pen.goto(0, 260)
pen.write("Score: 0  High Score: 0", align="center", font=("Arial", 14, "normal"))

# Movement functions
def go_up():
    if head.direction != "down":
        head.direction = "up"

def go_down():
    if head.direction != "up":
        head.direction = "down"

def go_left():
    if head.direction != "right":
        head.direction = "left"

def go_right():
    if head.direction != "left":
        head.direction = "right"

def move():
    if head.direction == "up":
        head.sety(head.ycor() + 20)
    if head.direction == "down":
        head.sety(head.ycor() - 20)
    if head.direction == "left":
        head.setx(head.xcor() - 20)
    if head.direction == "right":
        head.setx(head.xcor() + 20)

# Keyboard bindings
screen.listen()
screen.onkeypress(go_up, "w")
screen.onkeypress(go_down, "s")
screen.onkeypress(go_left, "a")
screen.onkeypress(go_right, "d")

# Game loop
while True:
    screen.update()

    # Border collision
    if abs(head.xcor()) > 290 or abs(head.ycor()) > 290:
        time.sleep(1)
        head.goto(0, 0)
        head.direction = "Stop"

        for seg in segments:
            seg.goto(1000, 1000)
        segments.clear()

        score = 0
        delay = 0.15   # reset speed

        pen.clear()
        pen.write(f"Score: {score}  High Score: {high_score}",
                  align="center", font=("Arial", 14, "normal"))

    # Food collision
    if head.distance(food) < 20:
        food.goto(random.randint(-280, 280), random.randint(-280, 280))

        # Add segment
        new_seg = turtle.Turtle()
        new_seg.shape("square")
        new_seg.color("green")
        new_seg.penup()
        segments.append(new_seg)

        score += 10
        if score > high_score:
            high_score = score

        # 🔥 Increase speed gradually
        delay -= 0.005
        delay = max(0.05, delay)

        pen.clear()
        pen.write(f"Score: {score}  High Score: {high_score}",
                  align="center", font=("Arial", 14, "normal"))

    # Move body
    for i in range(len(segments)-1, 0, -1):
        segments[i].goto(segments[i-1].pos())

    if segments:
        segments[0].goto(head.pos())

    move()

    # Self collision
    for seg in segments:
        if seg.distance(head) < 20:
            time.sleep(1)
            head.goto(0, 0)
            head.direction = "Stop"

            for s in segments:
                s.goto(1000, 1000)
            segments.clear()

            score = 0
            delay = 0.15   # reset speed

            pen.clear()
            pen.write(f"Score: {score}  High Score: {high_score}",
                      align="center", font=("Arial", 14, "normal"))

    time.sleep(delay)

turtle.done()
