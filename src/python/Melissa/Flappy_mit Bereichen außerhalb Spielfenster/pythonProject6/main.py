import pygame
import random
import os
import neat
import pickle
import time
import visualize


pygame.font.init()  # init font

WIN_WIDTH = 1200 #Breite des Ausgabefensters
WIN_HEIGHT = 800 #Höhe des Ausgabefensters
FLOOR = 730 #Startposition des Bodens
TOP = 0
STAT_FONT = pygame.font.SysFont("comicsans", 50)
END_FONT = pygame.font.SysFont("comicsans", 70)
DRAW_LINES = True #Ziellinien
SCORE_MAX = 1000
FITNESS_PIPE_PASSED = 5
FITNESS_COLLIDED_PIPE = 5
FITNESS_COLLIDED_FLOOR_TOP = 3

WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Flappy Bird")

#Bilder laden und skallieren
bird_imgs = [pygame.transform.scale2x(pygame.image.load(os.path.join('bird' + str(x) + ".png"))) for x in range(1,4)]
bottom_pipe_img = pygame.transform.scale2x(pygame.image.load(os.path.join('pipe.png')).convert_alpha())
top_pipe_img = pygame.transform.flip(bottom_pipe_img, False, True)
base_img = pygame.transform.scale2x(pygame.image.load(os.path.join('base.png')).convert_alpha())
bg_img = pygame.transform.scale(pygame.image.load(os.path.join('bg.png')).convert_alpha(), (600, 800))
outsindwindow_img = pygame.image.load(os.path.join('outsidewindow.png'))

gen = 0
FPS = 60


# Vogel
rot_max_up = 25
rot_max_down = -90
rot_stop_flapping = -80
rot_vel = 20
bird_animation_time = 5
jump_vel = -10 # Geschwindigkeit des Vogels bei Erteilen eines Hüpfbefehls
bird_starting_x = 530 # Startposition Vogel x, x = konst.
bird_starting_y = 350 # Startposition Vogel y
img_count = 0
gravity = 1 #Einfluss der "Gravitation"
new_vel = 0

#Röhrenpaare
gap_y = 165 # Abstand zwischen Unterkante der oberen Röhre und Oberkante der unteren Röhre (Flugschneise)
pipe_vel = 5 #Geschwindigkeit der Röhrenpaare = Geschwindigkeit des Bodens
random_max_height = 100 #Maximale Höhe des Bezugsniveaus der Flugschneise (Unterkante obere Röhre)
random_min_height = 450 #Minimale Höhe des Bezugsniveaus der Flugschneise (Unterkante obere Röhre)
x_first_pipe = 1000 # Startposition des ersten Röhrenpaares (wird außerhalb des Windows generiert)
x_add_new_pipe = 525
x_new_pipe = 900
x_remove_pipe = 300

#Boden
base_vel = 5 #Geschwindigkeit des Bodens = Geschwindigkeit der Röhrenpaare
base_y = FLOOR #the starting y position of the floor


class Bird:
    BIRDS = bird_imgs
    ANIMATION_TIME = bird_animation_time

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0  # Neigung des Vogels zu Beginn Horizontal
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.BIRD_IMGS = self.BIRDS[0]

# Flugverlauf Vogel bei Erteilung eines Hüpfbefehls
    def jump(self):
        self.vel = jump_vel # Vogel erhält Geschwindigkeit nach oben > negative Geschwindigkeit hier -10.5
        self.height = self.y # Registrieren der Ausgangsposition

    def move(self):
        self.tick_count += 1 #Zeitintervall für einen Versatz in Y-Richtung (Displacement) = ein Frame
        dt = self.tick_count - (self.tick_count - 1)

        d = self.vel * (dt) + 0.5 * (gravity) * (dt) ** 2  # Versatz (Displacement)

        if d >= 16: # Begrenzung: maximale Geschwingigkeit von 16 Pixel pro Frame nach unten
           d = 16

        #if d < 0:
            #d -= 2

        self.y = self.y + d #neue Ausgangsposition
        new_vel = self.vel + (gravity * dt) # Geschwindigkeit bei der neuen Ausgangsposition
        self.vel = new_vel

        if self.y <= 0: # Verhindern, dass Vogel über Oberkante des Spielfensters hinausfliegt
            self.y = 0
            self.vel = 10

        if self.y + self.BIRD_IMGS.get_height() > FLOOR: # Verhindern, dass Vogel Boden üerlappt
            self.y = FLOOR
            self.vel = 0

#Rotation/Neigung des Vogels
        if d < 0 or self.y < self.height + 50:  # tilt up
            if self.tilt < rot_max_up:
                self.tilt = rot_max_up
        else:  # tilt down
            if self.tilt > rot_max_down:
                self.tilt -= rot_vel

    def draw(self, win):
        self.img_count += 1

#Gernerieren des Flügelschlags

        if self.img_count <= bird_animation_time:
            self.BIRD_IMGS = self.BIRDS[0]
        elif self.img_count <= bird_animation_time * 2:
            self.BIRD_IMGS = self.BIRDS[1]
        elif self.img_count <= bird_animation_time * 3:
            self.BIRD_IMGS = self.BIRDS[2]
        elif self.img_count <= bird_animation_time * 4:
            self.BIRD_IMGS = self.BIRDS[1]
        elif self.img_count == (bird_animation_time * 4) + 1:
            self.BIRD_IMGS = self.BIRDS[0]
            self.img_count = 0

        # so when bird is nose diving it isn't flapping
        if self.tilt <= rot_stop_flapping:
            self.BIRD_img = self.BIRDS[1]
            self.img_count = bird_animation_time * 2

        # Rotation des Vogels um eingenen Mittelpunkt
        blitRotateCenter(win, self.BIRD_IMGS, (self.x, self.y), self.tilt)

class Pipe():
    PIPE_WIDTH = top_pipe_img.get_width()
    PIPE_HEIGHT = top_pipe_img.get_height()

    def __init__(self, x):
        self.x = x
        self.TOP_PIPE = top_pipe_img
        self.BOTTOM_PIPE = bottom_pipe_img
        self.random_height = 0
        self.top_pipe_height = 0
        self.bottom_pipe_height = 0
        self.passed = False
        self.RANDOM_HEIGHT()


    def RANDOM_HEIGHT(self): #Randomisieren der Position der Flugschneise
        self.random_height = random.randrange(random_max_height, random_min_height) # Variable Höhe des Bezugsniveaus hier Unterkante oder oberen Röhre
        self.top_pipe_height = self.random_height - self.PIPE_HEIGHT #Position der oberen linken Ecke der oberen Röhre
        self.bottom_pipe_height = self.random_height + gap_y #Position der oberen linken Ecke der unteren Röhre

    def move(self):
        self.x -= pipe_vel #Bewegung der Röhrenpaare von rechts nach links

    def draw(self, win):
        win.blit(self.TOP_PIPE, (self.x, self.top_pipe_height)) #Zeichnen der oberen Röhre an definierter Position
        win.blit(self.BOTTOM_PIPE, (self.x, self.bottom_pipe_height)) #Zeichnen der oberen Röhre an definierter Position


#Kollision zwischen Vogel und Röhre detektieren
def collide(pipe, bird, win):
    bird_mask = pygame.mask.from_surface(bird.BIRD_IMGS)
    top_pipe_mask = pygame.mask.from_surface(pipe.TOP_PIPE)
    bottom_pipe_mask = pygame.mask.from_surface(pipe.BOTTOM_PIPE)

    top_pipe_offset = (round(pipe.x - bird.x), pipe.top_pipe_height - round(bird.y))
    bottom_pipe_offset = (round(pipe.x - bird.x), pipe.bottom_pipe_height - round(bird.y))

    collision_point_bottom_pipe = bird_mask.overlap(bottom_pipe_mask, bottom_pipe_offset)
    collision_point_top_pipe = bird_mask.overlap(top_pipe_mask, top_pipe_offset)

    if collision_point_bottom_pipe or collision_point_top_pipe:
        return True

    else:
        return False


class Base:
    VEL = base_vel
    BASE_WIDTH = base_img.get_width()
    BASE = base_img

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.BASE_WIDTH
        self.x3 = self.BASE_WIDTH * 2

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL
        self.x3 -= self.VEL

        if self.x1 + self.BASE_WIDTH < 0:
            self.x1 = self.x3 + self.BASE_WIDTH

        if self.x2 + self.BASE_WIDTH < 0:
            self.x2 = self.x1 + self.BASE_WIDTH

        if self.x3 + self.BASE_WIDTH < 0:
             self.x3 = self.x2 + self.BASE_WIDTH

    def draw(self, win):
        win.blit(self.BASE, (self.x1, self.y))
        win.blit(self.BASE, (self.x2, self.y))
        win.blit(self.BASE, (self.x3, self.y))


def blitRotateCenter(surf, image, topleft, angle):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)

    surf.blit(rotated_image, new_rect.topleft)

def draw_window(win, birds, pipes, base, score, gen, pipe_ind):
    if gen == 0:
        gen = 1
    win.blit(outsindwindow_img, (0, 0))
    win.blit(bg_img, (300,0))
    win.blit(outsindwindow_img, (900,0))

    for pipe in pipes:
        pipe.draw(win)

    base.draw(win)
    for bird in birds:
        # Kontrollinien
        if DRAW_LINES:
            try:
                #Zentrum Vogel zu Unterkante obere Röhre
                #pygame.draw.line(win, (255, 0, 0), (bird.x + bird.BIRD_IMGS.get_width() / 2, bird.y + bird.BIRD_IMGS.get_height() / 2),(pipes[pipe_ind].x + pipes[pipe_ind].TOP_PIPE.get_width() / 2, pipes[pipe_ind].random_height),5)
                #Zentrum Vogel zu Oberkante untere Röhre
                #pygame.draw.line(win, (255, 0, 0), (bird.x + bird.BIRD_IMGS.get_width() / 2, bird.y + bird.BIRD_IMGS.get_height() / 2), (pipes[pipe_ind].x + pipes[pipe_ind].BOTTOM_PIPE.get_width() / 2,pipes[pipe_ind].bottom_pipe_height), 5)
                #Zentrum Vogel zu Mittelebene Flugschneise
                pygame.draw.line(win, (255, 0, 0), (bird.x + bird.BIRD_IMGS.get_width() / 2, bird.y + bird.BIRD_IMGS.get_height() / 2), (pipes[pipe_ind].x + pipes[pipe_ind].BOTTOM_PIPE.get_width() / 2, (pipes[pipe_ind].bottom_pipe_height - (gap_y/2))), 5)
            except:
                pass
        # draw bird
        bird.draw(win)

    # Spiel-Score
    score_label = STAT_FONT.render("Score: " + str(score),1,(255, 255, 255))
    win.blit(score_label, (WIN_WIDTH - score_label.get_width() - 315, 10))

    #Generation
    score_label = STAT_FONT.render("Generation: " + str(gen-1),1,(255,255,255))
    win.blit(score_label, (310, 10))

    # Anzahl Lebender Genome/Vögel anzeigen
    score_label = STAT_FONT.render("Alive: " + str(len(birds)),1,(255,255,255))
    win.blit(score_label, (310, 50))

    # Röhren-Index anzeigen
    score_label = STAT_FONT.render("Pipe-Index: " + str(pipe_ind), 1, (255, 255, 255))
    win.blit(score_label, (310, 90))

    pygame.display.update()


def eval_genomes(genomes, config):
    global WIN, gen
    win = WIN
    gen += 1 #erzeugen einer neuen Generation

    # Erstellen der Listen
    nets = []
    birds = []
    ge = []
    for genome_id, genome in genomes:
        genome.fitness = 0 #Initialer Fitness-Score = 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        birds.append(Bird(bird_starting_x,bird_starting_y))
        ge.append(genome)

    base = Base(FLOOR)
    pipes = [Pipe(x_first_pipe)]
    score = 0

    clock = pygame.time.Clock()

    run = True
    while run and len(birds) > 0:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
                break

        if score == SCORE_MAX:
            break


        pipe_ind = 0 #Röhren-Index bestimmen
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].TOP_PIPE.get_width():
                pipe_ind = 1

        for x, bird in enumerate(birds):  # give each bird a fitness of 0.1 for each frame it stays alive
            ge[x].fitness += 0.1
            bird.move()

            # ein Input: vertikaler Abstand Mittelpunkt Vogel und Mittelebene der Flugschneise
            output = nets[birds.index(bird)].activate(([((bird.y) +(bird.BIRD_IMGS.get_height() / 2)) - (pipes[pipe_ind].random_height + gap_y/2)]))
            #2 Inputs: vertikaler Abstand Mittelpunkt Vogel zu Oberkante/ Unterkante der unteren/oberen Röhre
            #output = nets[birds.index(bird)].activate((((pipes[pipe_ind].random_height)-(bird.y + (bird.BIRD_IMGS.get_height() / 2))),((pipes[pipe_ind].bottom_pipe_height) - (bird.y + (bird.BIRD_IMGS.get_height() / 2)))))


            if output[0] > 0.5:  # we use a tanh activation function so result will be between -1 and 1. if over 0.5 jump
                bird.jump()

        base.move()

        rem = []
        for pipe in pipes:
            pipe.move()

            if pipe.x + pipe.TOP_PIPE.get_width() < x_remove_pipe: #Durchlaufenes Röhrenpaar entfernen
                rem.append(pipe)

        for pipe in pipes: #Generieren einer neuen Pipe wenn vorherige definierte x-Position erreicht
            if pipe.x == x_add_new_pipe:
                pipes.append(Pipe(x_new_pipe))


            # Kolliion mit Röhre prüfen
            for bird in birds:
                if collide(pipe, bird, win):
                    ge[birds.index(bird)].fitness -= FITNESS_COLLIDED_PIPE
                    nets.pop(birds.index(bird))
                    ge.pop(birds.index(bird))
                    birds.pop(birds.index(bird))


            if not pipe.passed and pipe.x + top_pipe_img.get_width() < bird_starting_x: #Röhrenpaar vollständig passiert
                pipe.passed = True
                score += 1 # Spiel-Score + 1
                for genome in ge:
                    genome.fitness += FITNESS_PIPE_PASSED


        for r in rem:
            pipes.remove(r)


        for bird in birds: #Kollision mit Boden oder Oberem Bildschirmrand Prüfen
            if bird.y + bird.BIRD_IMGS.get_height() >= FLOOR or bird.y <= TOP:
                ge[birds.index(bird)].fitness -= FITNESS_COLLIDED_FLOOR_TOP
                nets.pop(birds.index(bird))
                ge.pop(birds.index(bird))
                birds.pop(birds.index(bird))


        draw_window(WIN, birds, pipes, base, score, gen, pipe_ind)

def run(config_file):

    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(5))

    # Run for up to 50 generations.
    p.run(eval_genomes, 50) #Anzahl der Generationen hier = 50
    winner = stats.best_genome()

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))

if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config')
    run(config_path)




