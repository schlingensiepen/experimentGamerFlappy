import pygame
import random
import os
import neat

pygame.font.init()  # init font

WIN_WIDTH = 600
WIN_HEIGHT = 800
FLOOR = 730
STAT_FONT = pygame.font.SysFont("comicsans", 50)
END_FONT = pygame.font.SysFont("comicsans", 70)
DRAW_LINES = False

WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Flappy Bird")

bird_imgs = [pygame.transform.scale2x(pygame.image.load(os.path.join('bird' + str(x) + ".png"))) for x in range(1,4)]
bottom_pipe_img = pygame.transform.scale2x(pygame.image.load(os.path.join('pipe.png')).convert_alpha())
top_pipe_img = pygame.transform.flip(bottom_pipe_img, False, True)
base_img = pygame.transform.scale2x(pygame.image.load(os.path.join('base.png')).convert_alpha())
bg_img = pygame.transform.scale(pygame.image.load(os.path.join('bg.png')).convert_alpha(), (600, 800))
outsindwindow_img = pygame.image.load(os.path.join('outsidewindow.png'))

gen = 0
FPS = 30


# Vogel
rot_max_up = 25
rot_max_down = -90
rot_vel = 20
bird_animation_time = 5
jump_vel = -10
acceleration = 3
bird_starting_x = 230
bird_starting_y = 350
img_count = 0
gravity = 1
new_vel = 0

#Rohrpaare
gap_y = 190 # Abstand zwischen Unterkante des oberen Rohres und Oberkante des unteren Rohtes (Flugschneise)
pipe_vel = 5 # horizontale Geschwindigkeit der Rohrpaare = Geschwindigkeit des Bodens
random_min_height = 50 # the minimum height of the top pipe (carefully set this number)
random_max_height = 450 # the maximum height of the top pipe (carefully set this number)
pipe_starting_x = 700 # Startposition des ersten Rohrpaares ( wird außerhalb des Windows generiert)

#Boden
base_vel = 5 #the horizontal moving velocity of the floor, this should equal to pipe_velocity
base_y = 730 #the starting y position of the floor


class Bird:
    BIRDS = bird_imgs
    ANIMATION_TIME = bird_animation_time

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0  # degrees to tilt
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.BIRD_IMGS = self.BIRDS[0]

    def jump(self):
        self.vel = jump_vel # Vogel erhält Geschwindigkeit nach oben > negative Geschwindigkeit hier -10.5
        self.height = self.y # Registrieren der Ausgangsposition

    def move(self):
        self.tick_count += 1 #Zeitintervall für einen Versatz
        dt = self.tick_count - (self.tick_count - 1)

        d = self.vel * (dt) + 0.5 * (gravity) * (dt) ** 2  # Versatz (Displacement)

        if d >= 16:
           d = 16

        #if d < 0:
            #d -= 2

        self.y = self.y + d
        self.y = self.y + d
        new_vel = self.vel + (gravity * dt)
        self.vel = new_vel

        if self.y < 0:
            self.y = 0
            self.vel = 0

        if self.y + self.BIRD_IMGS.get_height() > 730:
            self.y = 730
            self.vel = 0

        if d < 0 or self.y < self.height + 50:  # tilt up
            if self.tilt < rot_max_up:
                self.tilt = rot_max_up
        else:  # tilt down
            if self.tilt > rot_max_down:
                self.tilt -= rot_vel

    def draw(self, win):
        self.img_count += 1

        # For animation of bird, loop through three images
        if self.img_count <= 5:
            self.BIRD_IMGS = self.BIRDS[0]
        elif self.img_count <= 10:
            self.BIRD_IMGS = self.BIRDS[1]
        elif self.img_count <= 15:
            self.BIRD_IMGS = self.BIRDS[2]
        elif self.img_count <= 20:
            self.BIRD_IMGS = self.BIRDS[1]
        elif self.img_count == 21:
            self.BIRD_IMGS = self.BIRDS[0]
            self.img_count = 0

        # so when bird is nose diving it isn't flapping
        if self.tilt <= -80:
            self.BIRD_img = self.BIRDS[1]
            self.img_count = 5*2


        # tilt the bird
        blitRotateCenter(win, self.BIRD_IMGS, (self.x, self.y), self.tilt)



class Pipe():
    PIPE_WIDTH = top_pipe_img.get_width()
    PIPE_HEIGHT= top_pipe_img.get_height()

    def __init__(self, x):
        self.x = x
        self.TOP_PIPE = top_pipe_img
        self.BOTTOM_PIPE = bottom_pipe_img
        self.random_height = 0
        self.top_pipe_height = 0
        self.bottom_pipe_height = 0
        self.passed = False
        self.RANDOM_HEIGHT()

    def RANDOM_HEIGHT(self):
        self.random_height = random.randrange(random_min_height, random_max_height) # Variable Höhe des Bezugsniveaus Unterkante oberes Rohr
        self.top_pipe_height = self.random_height - self.PIPE_HEIGHT #Position der oberen linken Ecke der oberen Rohres
        self.bottom_pipe_height = self.random_height + gap_y #Position der oberen linken Ecke des unteren Rohres

    def move(self):
        self.x -= pipe_vel # Bewegung des Rohrpaares von rechts nach links

    def draw(self, win):
        win.blit(self.TOP_PIPE, (self.x, self.top_pipe_height)) # Zeichnen des oberen Rohres
        win.blit(self.BOTTOM_PIPE, (self.x, self.bottom_pipe_height))



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


        if self.x1 + self.BASE_WIDTH < 0:
            self.x1 = self.x2 + self.BASE_WIDTH

        if self.x2 + self.BASE_WIDTH < 0:
            self.x2 = self.x1 + self.BASE_WIDTH



    def draw(self, win):
        win.blit(self.BASE, (self.x1, self.y))
        win.blit(self.BASE, (self.x2, self.y))



def blitRotateCenter(surf, image, topleft, angle):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)

    surf.blit(rotated_image, new_rect.topleft)

def draw_window(win, birds, pipes, base, score, gen, pipe_ind):
    if gen == 0:
        gen = 1

    win.blit(bg_img, (0,0))


    for pipe in pipes:
        pipe.draw(win)

    base.draw(win)
    for bird in birds:
        # draw lines from bird to pipe
        if DRAW_LINES:
            try:
                pygame.draw.line(win, (255, 0, 0), (bird.x + bird.BIRD_IMGS.get_width() / 2, bird.y + bird.BIRD_IMGS.get_height() / 2),(pipes[pipe_ind].x + pipes[pipe_ind].TOP_PIPE.get_width() / 2, pipes[pipe_ind].random_height),5)
                pygame.draw.line(win, (255, 0, 0), (bird.x + bird.BIRD_IMGS.get_width() / 2, bird.y + bird.BIRD_IMGS.get_height() / 2), (pipes[pipe_ind].x + pipes[pipe_ind].BOTTOM_PIPE.get_width() / 2,pipes[pipe_ind].bottom_pipe_height), 5)
                #pygame.draw.line(win, (255, 0, 0), (bird.x + bird.BIRD_IMGS.get_width() / 2, bird.y + bird.BIRD_IMGS.get_height() / 2), (pipes[pipe_ind].x + pipes[pipe_ind].BOTTOM_PIPE.get_width() / 2, (pipes[pipe_ind].bottom_pipe_height - (gap_y/2))), 5)
            except:
                pass
        # draw bird
        bird.draw(win)

    # score
    score_label = STAT_FONT.render("Score: " + str(score),1,(255, 255, 255))
    win.blit(score_label, (WIN_WIDTH - score_label.get_width() - 315, 10))

    #generations
    score_label = STAT_FONT.render("Gens: " + str(gen-1),1,(255,255,255))
    win.blit(score_label, (310, 10))

    # alive
    score_label = STAT_FONT.render("Alive: " + str(len(birds)),1,(255,255,255))
    win.blit(score_label, (310, 50))

    pygame.display.update()


def eval_genomes(genomes, config):
    global WIN, gen
    win = WIN
    gen += 1

    # start by creating lists holding the genome itself, the
    # neural network associated with the genome and the
    # bird object that uses that network to play
    nets = []
    birds = []
    ge = []
    for genome_id, genome in genomes:
        genome.fitness = 0  # start with fitness level of 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        birds.append(Bird(230,350))
        ge.append(genome)

    base = Base(FLOOR)
    pipes = [Pipe(700)]
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

        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].TOP_PIPE.get_width():  # determine whether to use the first or second
                pipe_ind = 1                                                                 # pipe on the screen for neural network input

        for x, bird in enumerate(birds):  # give each bird a fitness of 0.1 for each frame it stays alive
            ge[x].fitness += 0.1
            bird.move()



            # send bird location, top pipe location and bottom pipe location and determine from network whether to jump or not
            output = nets[birds.index(bird)].activate(([(bird.y + (bird.BIRD_IMGS.get_height()/2)) - (pipes[pipe_ind].random_height + (gap_y/2))]))
            #output = nets[birds.index(bird)].activate((((bird.y + (bird.BIRD_IMGS.get_height() / 2)) - (pipes[pipe_ind].random_height)),((bird.y + (bird.BIRD_IMGS.get_height() / 2)) - (pipes[pipe_ind].bottom_pipe_height))))


            if output[0] > 0.5:  # we use a tanh activation function so result will be between -1 and 1. if over 0.5 jump
                bird.jump()

        base.move()

        rem = []
        for pipe in pipes:
            pipe.move()

            if pipe.x + pipe.TOP_PIPE.get_width() < 0:
                rem.append(pipe)

        for pipe in pipes:
            if pipe.x == 225:
                pipes.append(Pipe(600))


            # check for collision
            for bird in birds:
                if collide(pipe, bird, win):
                    ge[birds.index(bird)].fitness -= 5
                    nets.pop(birds.index(bird))
                    ge.pop(birds.index(bird))
                    birds.pop(birds.index(bird))


            if not pipe.passed and pipe.x + top_pipe_img.get_width() < 530:
                pipe.passed = True
                score += 1
                for genome in ge:
                    genome.fitness += 5


        for r in rem:
            pipes.remove(r)

        for bird in birds:
            if bird.y + bird.BIRD_IMGS.get_height() >= 730 or bird.y <= 0:
                ge[birds.index(bird)].fitness -= 5
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
    #p.add_reporter(neat.Checkpointer(5))

    # Run for up to 50 generations.
    winner = p.run(eval_genomes, 50)

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))


if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config')
    run(config_path)


