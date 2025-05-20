import pgzrun
from random import randint
from math import sin, pi
from pygame import Rect

# Set character properties
alien = Actor("alien")
alien.topright = 0 , 10

# Set the screen size and title
WIDTH = 500
HEIGHT = alien.height + 20
TITLE = "Super Popo"

def draw():
    screen.clear()
    alien.draw()

def update():
    alien.left += 2
    if alien.left > WIDTH:
        alien.right = 0

def on_mouse_down(pos):
    if alien.collidepoint(pos):
        set_alien_hurt()


def set_alien_hurt():
    alien.image = 'alien_hurt'
    sounds.eep.play()
    clock.schedule_unique(set_alien_normal, 1.0)

def set_alien_normal():
    alien.image = 'alien'

pgzrun.go()
