


import pygame

surf = pygame.display.set_mode((800,600))
run = True
posX = 50
while run :
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      run = False
  surf.fill((0,0,0))
  pygame.draw.circle(surf, (255,0,0), (posX, 300), 30, 2)
  posX = posX + 1
  pygame.display.flip()
pygame.quit()