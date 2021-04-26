from itertools import cycle
import random
import sys
import numpy as np
import os
import neat

from bird import Bird

import pygame
from pygame.locals import *
from setuptools.command.setopt import config_file

FPS = 100
SCREENWIDTH  = 288
SCREENHEIGHT = 400
# amount by which base can maximum shift to left
PIPEGAPSIZE  = 100 # gap between upper and lower part of pipe
BASEY        = SCREENHEIGHT * 0.79
# image, sound and hitmask  dicts
IMAGES, SOUNDS, HITMASKS = {}, {}, {}

SCALING = 0.5

# list of all possible players (tuple of 3 positions of flap)
PLAYERS_LIST = [

    # red bird
    (
        'assets/sprites/redbird-upflap.png',
        'assets/sprites/redbird-midflap.png',
        'assets/sprites/redbird-downflap.png',
    ),
    
    # blue bird
    (
        # amount by which base can maximum shift to left
        'assets/sprites/bluebird-upflap.png',
        'assets/sprites/bluebird-midflap.png',
        'assets/sprites/bluebird-downflap.png',
    ),
    # yellow bird

    (
        'assets/sprites/yellowbird-upflap.png',
        'assets/sprites/yellowbird-midflap.png',
        'assets/sprites/yellowbird-downflap.png',
    ),

]

# list of backgrounds
BACKGROUNDS_LIST = (
    'assets/sprites/background-day.png',
    'assets/sprites/background-night.png',
)

# list of pipes
PIPES_LIST = (
    'assets/sprites/pipe-green.png',
    'assets/sprites/pipe-red.png',
)


try:
    xrange
except NameError:
    xrange = range



def main(genomes, config):
#def main():


    global SCREEN, FPSCLOCK
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    SCREEN = pygame.display.set_mode((int(SCREENWIDTH * SCALING), int(SCREENHEIGHT * SCALING)))
    pygame.display.set_caption('Flappy Bird')

    # numbers sprites for score display
    IMAGES['numbers'] = (
        pygame.image.load('assets/sprites-custom/0.png').convert_alpha(),
        pygame.image.load('assets/sprites-custom/1.png').convert_alpha(),
        pygame.image.load('assets/sprites-custom/2.png').convert_alpha(),
        pygame.image.load('assets/sprites-custom/3.png').convert_alpha(),
        pygame.image.load('assets/sprites-custom/4.png').convert_alpha(),
        pygame.image.load('assets/sprites-custom/5.png').convert_alpha(),
        pygame.image.load('assets/sprites-custom/6.png').convert_alpha(),
        pygame.image.load('assets/sprites-custom/7.png').convert_alpha(),
        pygame.image.load('assets/sprites-custom/8.png').convert_alpha(),
        pygame.image.load('assets/sprites-custom/9.png').convert_alpha()
    )

    # game over sprite
    IMAGES['gameover'] = pygame.image.load('assets/sprites-custom/gameover.png').convert_alpha()
    # message sprite for welcome screen
    IMAGES['message'] = pygame.image.load('assets/sprites-custom/message.png').convert_alpha()
    # base (ground) sprite
    IMAGES['base'] = pygame.image.load('assets/sprites-custom/base.png').convert_alpha()

    # sounds
    if 'win' in sys.platform:
        soundExt = '.wav'
    else:
        soundExt = '.ogg'

    SOUNDS['die']    = pygame.mixer.Sound('assets/audio/die' + soundExt)
    SOUNDS['hit']    = pygame.mixer.Sound('assets/audio/hit' + soundExt)
    SOUNDS['point']  = pygame.mixer.Sound('assets/audio/point' + soundExt)
    SOUNDS['swoosh'] = pygame.mixer.Sound('assets/audio/swoosh' + soundExt)
    SOUNDS['wing']   = pygame.mixer.Sound('assets/audio/wing' + soundExt)

    # select random background sprites
    randBg = random.randint(0, len(BACKGROUNDS_LIST) - 1)
    IMAGES['background'] = pygame.image.load(BACKGROUNDS_LIST[randBg]).convert()

    # select random player sprites
    randPlayer = random.randint(0, len(PLAYERS_LIST) - 1)
    IMAGES['player'] = (
        pygame.image.load(PLAYERS_LIST[randPlayer][0]).convert_alpha(),
        pygame.image.load(PLAYERS_LIST[randPlayer][1]).convert_alpha(),
        pygame.image.load(PLAYERS_LIST[randPlayer][2]).convert_alpha(),
    )

    # select random pipe sprites
    pipeindex = random.randint(0, len(PIPES_LIST) - 1)
    IMAGES['pipe'] = (
        pygame.transform.rotate(
            pygame.image.load(PIPES_LIST[pipeindex]).convert_alpha(), 180),
        pygame.image.load(PIPES_LIST[pipeindex]).convert_alpha(),
    )

    # hismask for pipes
    HITMASKS['pipe'] = (
        getHitmask(IMAGES['pipe'][0]),
        getHitmask(IMAGES['pipe'][1]),
    )

    # hitmask for player
    HITMASKS['player'] = (
        getHitmask(IMAGES['player'][0]),
        getHitmask(IMAGES['player'][1]),
        getHitmask(IMAGES['player'][2]),
    )

    score = loopIter = 0

    # bird = Bird(movementInfo, SCREENWIDTH)

    basex = -16
    baseShift = IMAGES['base'].get_width() - IMAGES['background'].get_width()

    # get 2 new pipes to add to upperPipes lowerPipes list
    newPipe1 = getRandomPipe()
    newPipe2 = getRandomPipe()

    # list of upper pipes
    upperPipes = [
        {'x': SCREENWIDTH + 200, 'y': newPipe1[0]['y']},
        {'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2), 'y': newPipe2[0]['y']},
    ]

    # list of lowerpipe
    lowerPipes = [
        {'x': SCREENWIDTH + 200, 'y': newPipe1[1]['y']},
        {'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2), 'y': newPipe2[1]['y']},
    ]

    pipeVelX = -4

    surface = pygame.Surface((SCREENWIDTH, SCREENHEIGHT))

    Birds = []
    nets = []
    ge = []

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        g.fitness = 0
        playery = int((SCREENHEIGHT - IMAGES['player'][0].get_height()) / 2)
        movementInfo = {
            'playery': np.random.randint(playery - 8, playery + 8),
            'basex': -16,
            'playerIndexGen': cycle([0, 1, 2, 1])
        }
        Birds.append(Bird(movementInfo, SCREENWIDTH))
        ge.append(g)

    run = True
    while run and len(Birds) > 0:
        # move pipes to left
        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            uPipe['x'] += pipeVelX
            lPipe['x'] += pipeVelX

        # add new pipe when first pipe is about to touch left of screen
        if 0 < upperPipes[0]['x'] < 5:
            newPipe = getRandomPipe()
            upperPipes.append(newPipe[0])
            lowerPipes.append(newPipe[1])

        # remove first pipe if its out of the screen
        if upperPipes[0]['x'] < -IMAGES['pipe'][0].get_width():
            upperPipes.pop(0)
            lowerPipes.pop(0)

        # draw sprites

        surface.blit(IMAGES['background'], (0, 0))

        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            surface.blit(IMAGES['pipe'][0], (uPipe['x'], uPipe['y']))
            surface.blit(IMAGES['pipe'][1], (lPipe['x'], lPipe['y']))

        surface.blit(IMAGES['base'], (basex, BASEY))
        # print score so player overlaps the score
        showScore(Birds[0].score, surface)

        for x, bird in enumerate(Birds):
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    pygame.quit()
                    run = False
                    sys.exit()
                '''if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                    if bird.playery > -2 * IMAGES['player'][0].get_height():
                        bird.playerVelY = bird.playerFlapAcc
                        bird.playerFlapped = True
                        SOUNDS['wing'].play()'''



            # check for crash here
            crashTest = checkCrash({'x': bird.playerx, 'y': bird.playery, 'index': bird.playerIndex},
                                   upperPipes, lowerPipes)

            # check for score
            bird.playerMidPos = bird.playerx + IMAGES['player'][0].get_width() / 2
            for pipe in upperPipes:
                pipeMidPos = pipe['x'] + IMAGES['pipe'][0].get_width() / 2
                if pipeMidPos <= bird.playerMidPos < pipeMidPos + 4:
                    bird.score += 1
                    ge[x].fitness += 5
                    SOUNDS['point'].play()

            # playerIndex basex change
            if (loopIter + 1) % 3 == 0:
                bird.playerIndex = next(bird.playerIndexGen)
            loopIter = (loopIter + 1) % 30
            basex = -((-basex + 100) % baseShift)

            # rotate the player
            if bird.playerRot > -90:
                bird.playerRot -= bird.playerVelRot

            # player's movement
            if bird.playerVelY < bird.playerMaxVelY and not bird.playerFlapped:
                bird.playerVelY += bird.playerAccY
            if bird.playerFlapped:
                bird.playerFlapped = False

                # more rotation to cover the threshold (calculated in visible rotation)
                bird.playerRot = 45

            bird.playerHeight = IMAGES['player'][bird.playerIndex].get_height()
            bird.playery += min(bird.playerVelY, BASEY - bird.playery - bird.playerHeight)

            # Player rotation has a threshold
            bird.visibleRot = bird.playerRotThr
            if bird.playerRot <= bird.playerRotThr:
                bird.visibleRot = bird.playerRot

            bird.playerSurface = pygame.transform.rotate(IMAGES['player'][bird.playerIndex], bird.visibleRot)
            surface.blit(bird.playerSurface, (bird.playerx, bird.playery))

            ge[x].fitness += 0.1

            pipe_ind = 0
            if len(Birds) < 1:
                break
            else:
                if upperPipes[0]['x'] > Birds[0].playerx:
                    pipe_ind = 0
                else:
                    pipe_ind = 1

            pipeH = IMAGES['pipe'][0].get_height()
            print(upperPipes[pipe_ind]['y']+pipeH)

            print(lowerPipes[pipe_ind]['y'])

            #pipeH = IMAGES['pipe'][0].get_height()

            output = nets[x].activate(
                (bird.playery, abs(upperPipes[pipe_ind]['y']+pipeH - bird.playery), abs(lowerPipes[pipe_ind]['y'] - bird.playery), upperPipes[pipe_ind]['x'] - bird.playerx))

            if output[0] > 0.5:
                if bird.playery > -2 * IMAGES['player'][0].get_height():
                    bird.playerVelY = bird.playerFlapAcc
                    bird.playerFlapped = True
                    SOUNDS['wing'].play()

            if crashTest[0]:
                if crashTest[1]:
                    ge[x].fitness -= 1
                ge[x].fitness -= 1
                Birds.pop(x)
                nets.pop(x)
                ge.pop(x)

                '''
                return {
                    'y': bird.playery,
                    'groundCrash': crashTest[1],
                    'basex': basex,
                    'upperPipes': upperPipes,
                    'lowerPipes': lowerPipes,
                    'score': score,
                    'playerVelY': bird.playerVelY,
                    'playerRot': bird.playerRot
                }
                '''

        surfaceScaled = pygame.transform.scale(surface, (int(SCREENWIDTH * SCALING), int(SCREENHEIGHT * SCALING)))
        SCREEN.blit(surfaceScaled, (0, 0))

        pygame.display.update()
        FPSCLOCK.tick(FPS)
        # hier pipes location übergeben
        # hier zeit vergangen hinzufügen



def showWelcomeAnimation():
    """Shows welcome screen animation of flappy bird"""
    # index of player to blit on screen
    playerIndex = 0
    playerIndexGen = cycle([0, 1, 2, 1])
    # iterator used to change playerIndex after every 5th iteration
    loopIter = 0

    playerx = int(SCREENWIDTH * 0.2)
    playery = int((SCREENHEIGHT - IMAGES['player'][0].get_height()) / 2)

    messagex = int((SCREENWIDTH - IMAGES['message'].get_width()) / 2)
    messagey = int(SCREENHEIGHT * 0.12)

    basex = 0
    # amount by which base can maximum shift to left
    baseShift = IMAGES['base'].get_width() - IMAGES['background'].get_width()

    # player shm for up-down motion on welcome screen
    playerShmVals = {'val': 0, 'dir': 1}
    surface = pygame.Surface((SCREENWIDTH, SCREENHEIGHT))

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                # make first flap sound and return values for mainGame
                SOUNDS['wing'].play()
                return {
                    'playery': playery + playerShmVals['val'],
                    'basex': basex,
                    'playerIndexGen': playerIndexGen,
                }

        # adjust playery, playerIndex, basex
        if (loopIter + 1) % 5 == 0:
            playerIndex = next(playerIndexGen)
        loopIter = (loopIter + 1) % 30
        basex = -((-basex + 4) % baseShift)
        playerShm(playerShmVals)

        # draw sprites
        surface.blit(IMAGES['background'], (0,0))
        surface.blit(IMAGES['player'][playerIndex],
                    (playerx, playery + playerShmVals['val']))
        surface.blit(IMAGES['message'], (messagex, messagey))
        surface.blit(IMAGES['base'], (basex, BASEY))

        surfaceScaled = pygame.transform.scale(surface, (int(SCREENWIDTH * SCALING), int(SCREENHEIGHT * SCALING)))
        SCREEN.blit(surfaceScaled, (0, 0))

        pygame.display.update()

        FPSCLOCK.tick(FPS)





def showGameOverScreen(crashInfo):
    """crashes the player down ans shows gameover image"""
    score = crashInfo['score']
    playerx = SCREENWIDTH * 0.2
    playery = crashInfo['y']
    playerHeight = IMAGES['player'][0].get_height()
    playerVelY = crashInfo['playerVelY']
    playerAccY = 2
    playerRot = crashInfo['playerRot']
    playerVelRot = 7

    basex = crashInfo['basex']

    upperPipes, lowerPipes = crashInfo['upperPipes'], crashInfo['lowerPipes']

    # play hit and die sounds
    SOUNDS['hit'].play()
    if not crashInfo['groundCrash']:
        SOUNDS['die'].play()

    surface = pygame.Surface((SCREENWIDTH, SCREENHEIGHT))

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if playery + playerHeight >= BASEY - 1:
                    return

        # player y shift
        if playery + playerHeight < BASEY - 1:
            playery += min(playerVelY, BASEY - playery - playerHeight)

        # player velocity change
        if playerVelY < 15:
            playerVelY += playerAccY

        # rotate only when it's a pipe crash
        if not crashInfo['groundCrash']:
            if playerRot > -90:
                playerRot -= playerVelRot

        # draw sprites
        surface.blit(IMAGES['background'], (0,0))

        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            surface.blit(IMAGES['pipe'][0], (uPipe['x'], uPipe['y']))
            surface.blit(IMAGES['pipe'][1], (lPipe['x'], lPipe['y']))

        surface.blit(IMAGES['base'], (basex, BASEY))
        showScore(score, surface)

        playerSurface = pygame.transform.rotate(IMAGES['player'][1], playerRot)
        surface.blit(playerSurface, (playerx,playery))

        surfaceScaled = pygame.transform.scale(surface, (int(SCREENWIDTH * SCALING), int(SCREENHEIGHT * SCALING)))
        SCREEN.blit(surfaceScaled, (0, 0))

        FPSCLOCK.tick(FPS)
        pygame.display.update()


def playerShm(playerShm):
    """oscillates the value of playerShm['val'] between 8 and -8"""
    if abs(playerShm['val']) == 8:
        playerShm['dir'] *= -1

    if playerShm['dir'] == 1:
         playerShm['val'] += 1
    else:
        playerShm['val'] -= 1


def getRandomPipe():
    """returns a randomly generated pipe"""
    # y of gap between upper and lower pipe
    gapY = random.randrange(0, int(BASEY * 0.6 - PIPEGAPSIZE))
    gapY += int(BASEY * 0.2)
    pipeHeight = IMAGES['pipe'][0].get_height()
    pipeX = SCREENWIDTH + 10


    return [
        {'x': pipeX, 'y': gapY - pipeHeight},  # upper pipe
        {'x': pipeX, 'y': gapY + PIPEGAPSIZE}, # lower pipe
    ]


def showScore(score, surface):
    """displays score in center of screen"""
    scoreDigits = [int(x) for x in list(str(score))]
    totalWidth = 0 # total width of all numbers to be printed

    for digit in scoreDigits:
        totalWidth += IMAGES['numbers'][digit].get_width()

    Xoffset = (SCREENWIDTH - totalWidth) / 2

    for digit in scoreDigits:
        surface.blit(IMAGES['numbers'][digit], (Xoffset, SCREENHEIGHT * 0.1))
        Xoffset += IMAGES['numbers'][digit].get_width()


def checkCrash(player, upperPipes, lowerPipes):
    """returns True if player collders with base or pipes."""
    pi = player['index']
    player['w'] = IMAGES['player'][0].get_width()
    player['h'] = IMAGES['player'][0].get_height()

    # if player crashes into ground
    if player['y'] + player['h'] >= BASEY - 1:
        return [True, True]
    elif player['y'] <= 0:
        return [True, True]

    #return ground crash
    else:

        playerRect = pygame.Rect(player['x'], player['y'],
                      player['w'], player['h'])
        pipeW = IMAGES['pipe'][0].get_width()
        pipeH = IMAGES['pipe'][0].get_height()

        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            # upper and lower pipe rects
            uPipeRect = pygame.Rect(uPipe['x'], uPipe['y'], pipeW, pipeH)
            lPipeRect = pygame.Rect(lPipe['x'], lPipe['y'], pipeW, pipeH)

            print(lPipeRect)
            print((uPipeRect))

            # player and upper/lower pipe hitmasks
            pHitMask = HITMASKS['player'][pi]
            uHitmask = HITMASKS['pipe'][0]
            lHitmask = HITMASKS['pipe'][1]

            # if bird collided with upipe or lpipe
            uCollide = pixelCollision(playerRect, uPipeRect, pHitMask, uHitmask)
            lCollide = pixelCollision(playerRect, lPipeRect, pHitMask, lHitmask)

            if uCollide or lCollide:
                return [True, False]
            #return pipe crash

    return [False, False]

def pixelCollision(rect1, rect2, hitmask1, hitmask2):
    """Checks if two objects collide and not just their rects"""
    rect = rect1.clip(rect2)

    if rect.width == 0 or rect.height == 0:
        return False

    x1, y1 = rect.x - rect1.x, rect.y - rect1.y
    x2, y2 = rect.x - rect2.x, rect.y - rect2.y

    for x in xrange(rect.width):
        for y in xrange(rect.height):
            if hitmask1[x1+x][y1+y] and hitmask2[x2+x][y2+y]:
                return True
    return False

def getHitmask(image):
    """returns a hitmask using an image's alpha."""
    mask = []
    for x in xrange(image.get_width()):
        mask.append([])
        for y in xrange(image.get_height()):
            mask[x].append(bool(image.get_at((x,y))[3]))
    return mask


def run(config_file):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_file)

    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(main, 50)


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    #config_path = 'C:/work/experimentGamerFlappy/src/python/Arne/config-feedforward.txt'
    run(config_path)
