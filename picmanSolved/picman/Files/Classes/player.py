import pygame

class player:
    def __init__(self,x,y,image,playerWidth,playerHeight,lives,xChange,yChange):
        self.image = pygame.image.load("../Sprites/Pacman.png")
        self.playerWidth = 12
        self.playerHeight = 12
        self.lives = 3
        self.x = (displayWidth * 0.45)
        self.y = (displayHeight * 0.8)
    
    def drawPlayer(x,y):
        gameDisplay.blit(self.image,(x,y))
    

    

