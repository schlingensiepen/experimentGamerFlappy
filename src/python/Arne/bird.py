
class Bird:
    playerMidPos = 0
    playerHeight = 0
    visibleRot = 0
    playerSurface = None
    score = 0

    def __init__(self, movementInfo, SCREENWIDTH):
        self.playerIndexGen = movementInfo['playerIndexGen']
        self.playerx, self.playery = int(SCREENWIDTH * 0.2), movementInfo['playery']
        self.playerVelY = -9  # player's velocity along Y, default same as playerFlapped
        self.playerMaxVelY = 10  # max vel along Y, max descend speed
        self.playerMinVelY = -8  # min vel along Y, max ascend speed
        self.playerAccY = 1  # players downward accleration
        self.playerRot = 45  # player's rotation
        self.playerVelRot = 3  # angular speed
        self.playerRotThr = 20  # rotation threshold
        self.playerFlapAcc = -9  # players speed on flapping
        self.playerFlapped = False  # True when player flaps
        self.playerIndex = 0