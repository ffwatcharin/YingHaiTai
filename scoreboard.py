import pygame
class ScoreInput:
    def __init__(self,surface,text,color,x,y,scale):
        self.surface = surface 
        self.text = text[: -1]
        self.color = color
        self.x = x
        self.y =y
        self.scale =scale
        self.font = pygame.font.Font(None,16*self.scale)
        self.this_text =self.font.render(self.text,True,self.color)
    def draw(self):
        self.surface.blit(self.this_text,(self.x,self.y))