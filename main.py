import sys
import pygame
import random
from constants import *
from pygame.locals import *


class MineField:
    def __init__(self):
        self.field = self.blankField()

    def game(self):
        icon = pygame.image.load("icon.png")
        pygame.init()
        pygame.display.set_icon(icon)
        pygame.display.set_caption("Сапёр")
        self.FPSCLOCK = pygame.time.Clock()
        self.DISPLAYSURFACE = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
        self.BASICFONT = pygame.font.SysFont(FONTTYPE, FONTSIZE)

        # obtain reset & show objects and rects
        self.RESET_SURF, self.RESET_RECT = self.drawButton("Заново", TEXTCOLOR_3, RESETBGCOLOR, WINDOWWIDTH / 2, WINDOWHEIGHT - 120)

        # stores XY of mouse events
        mouse_x = 0
        mouse_y = 0

        # set up data structures and lists
        zeroListXY, revealedBoxes, markedMines = self.gameSetup()

        # set background color
        self.DISPLAYSURFACE.fill(BGCOLOR)

        # main game loop
        while True:

            # check for quit function
            self.checkForKeyPress()

            # initialize input booleans
            mouseClicked = False
            spacePressed = False

            # draw field
            self.DISPLAYSURFACE.fill(BGCOLOR)
            pygame.draw.rect(self.DISPLAYSURFACE, FIELDCOLOR, (
                XMARGIN - 5, YMARGIN - 5, (BOXSIZE + GAPSIZE) * FIELDWIDTH + 5, (BOXSIZE + GAPSIZE) * FIELDHEIGHT + 5))
            self.drawField()
            self.drawMinesNumbers()

            # event handling loop
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                    self.terminate()
                elif event.type == MOUSEMOTION:
                    mouse_x, mouse_y = event.pos
                elif event.type == MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = event.pos
                    mouseClicked = True
                elif event.type == KEYDOWN:
                    if event.key == K_SPACE:
                        spacePressed = True
                elif event.type == KEYUP:
                    if event.key == K_SPACE:
                        spacePressed = False

            # draw covers
            self.drawCovers(revealedBoxes, markedMines)

            # mine marker tip
            tipFont = pygame.font.SysFont(FONTTYPE, 16)
            self.drawText("Совет: выделите поле и нажмите пробел (вместо щелчка мышью)", tipFont, TEXTCOLOR_3,
                          self.DISPLAYSURFACE, WINDOWWIDTH / 2, WINDOWHEIGHT - 60)
            self.drawText("чтобы отметить области, которые, как вы думаете, содержат мины.", tipFont, TEXTCOLOR_3, self.DISPLAYSURFACE,
                          WINDOWWIDTH / 2,
                          WINDOWHEIGHT - 40)

            # determine boxes at clicked areas
            box_x, box_y = self.getBoxAtPixel(mouse_x, mouse_y)

            # mouse not over a box in field
            if (box_x, box_y) == (None, None):

                # check if reset box is clicked
                if self.RESET_RECT.collidepoint(mouse_x, mouse_y):
                    self.highlightButton(self.RESET_RECT)
                    if mouseClicked:
                        zeroListXY, revealedBoxes, markedMines = self.gameSetup()

            # mouse currently over box in field
            else:

                # highlight unrevealed box
                if not revealedBoxes[box_x][box_y]:
                    self.highlightBox(box_x, box_y)

                    # mark mines
                    if spacePressed:
                        try:
                            markedMines.remove([box_x, box_y])
                        except ValueError:
                            markedMines.append([box_x, box_y])

                    # reveal clicked boxes
                    if mouseClicked:
                        revealedBoxes[box_x][box_y] = True

                        # when 0 is revealed, show relevant boxes
                        if self.field[box_x][box_y] == "[0]":
                            self.showNumbers(revealedBoxes, box_x, box_y, zeroListXY)

                        # when mine is revealed, show mines
                        if self.field[box_x][box_y] == "[X]":
                            self.gameOverAnimation(revealedBoxes, markedMines, "LOSS")
                            zeroListXY, revealedBoxes, markedMines = self.gameSetup()

            # check if player has won
            if self.gameWon(revealedBoxes):
                self.gameOverAnimation(revealedBoxes, markedMines, "WIN")
                zeroListXY, revealedBoxes, markedMines = self.gameSetup()

            # redraw screen, wait clock tick
            pygame.display.update()
            self.FPSCLOCK.tick(FPS)

    def blankField(self):
        field = []
        for x in range(FIELDWIDTH):
            field.append([])
            for y in range(FIELDHEIGHT):
                field[x].append("[ ]")
        return field

    def placeMines(self):
        # places mines in FIELDWIDTH x FIELDHEIGHT data structure
        # requires blank field as input

        mineCount = 0
        xy = []
        while mineCount < MINESTOTAL:
            x = random.randint(0, FIELDWIDTH - 1)
            y = random.randint(0, FIELDHEIGHT - 1)
            xy.append([x, y])
            if xy.count([x, y]) > 1:
                xy.remove([x, y])
            else:
                self.field[x][y] = "[X]"
                mineCount += 1

    def isThereMine(self, x, y):
        return self.field[x][y] == "[X]"

    def placeNumbers(self):
        # places numbers in FIELDWIDTH x FIELDHEIGHT data structure
        # requires field with mines as input

        for x in range(FIELDWIDTH):
            for y in range(FIELDHEIGHT):
                if not self.isThereMine(x, y):
                    count = 0
                    if x != 0:
                        if self.isThereMine(x - 1, y):
                            count += 1
                        if y != 0:
                            if self.isThereMine(x - 1, y - 1):
                                count += 1
                        if y != FIELDHEIGHT - 1:
                            if self.isThereMine(x - 1, y + 1):
                                count += 1
                    if x != FIELDWIDTH - 1:
                        if self.isThereMine(x + 1, y):
                            count += 1
                        if y != 0:
                            if self.isThereMine(x + 1, y - 1):
                                count += 1
                        if y != FIELDHEIGHT - 1:
                            if self.isThereMine(x + 1, y + 1):
                                count += 1
                    if y != 0:
                        if self.isThereMine(x, y - 1):
                            count += 1
                    if y != FIELDHEIGHT - 1:
                        if self.isThereMine(x, y + 1):
                            count += 1
                    self.field[x][y] = '[%s]' % count

    def blankRevealedBoxData(self, val):
        # returns FIELDWIDTH x FIELDHEIGHT data structure different from the field data structure
        # each item in data structure is boolean (val) to show whether box at those fieldwidth & fieldheight coordinates should be revealed

        revealedBoxes = []
        for i in range(FIELDWIDTH):
            revealedBoxes.append([val] * FIELDHEIGHT)
        return revealedBoxes

    def gameSetup(self):
        # set up mine field data structure, list of all zeros for recursion, and revealed box boolean data structure

        # mineField = self.blankField()
        self.placeMines()
        self.placeNumbers()
        zeroListXY = []
        markedMines = []
        revealedBoxes = self.blankRevealedBoxData(False)

        return zeroListXY, revealedBoxes, markedMines

    def drawField(self):
        # draws field GUI and reset button

        for box_x in range(FIELDWIDTH):
            for box_y in range(FIELDHEIGHT):
                left, top = self.getLeftTopXY(box_x, box_y)
                pygame.draw.rect(self.DISPLAYSURFACE, BOXCOLOR_REV, (left, top, BOXSIZE, BOXSIZE))

        self.DISPLAYSURFACE.blit(self.RESET_SURF, self.RESET_RECT)

    def drawMinesNumbers(self):
        # draws mines and numbers onto GUI
        # field should have mines and numbers

        half = int(BOXSIZE * 0.5)
        quarter = int(BOXSIZE * 0.25)
        eighth = int(BOXSIZE * 0.125)

        for box_x in range(FIELDWIDTH):
            for box_y in range(FIELDHEIGHT):
                left, top = self.getLeftTopXY(box_x, box_y)
                center_x, center_y = self.getCenterXY(box_x, box_y)
                if self.field[box_x][box_y] == "[X]":
                    pygame.draw.circle(self.DISPLAYSURFACE, MINECOLOR, (left + half, top + half), quarter)
                    pygame.draw.circle(self.DISPLAYSURFACE, WHITE, (left + half, top + half), eighth)
                    pygame.draw.line(self.DISPLAYSURFACE, MINECOLOR, (left + eighth, top + half),
                                     (left + half + quarter + eighth, top + half))
                    pygame.draw.line(self.DISPLAYSURFACE, MINECOLOR, (left + half, top + eighth),
                                     (left + half, top + half + quarter + eighth))
                    pygame.draw.line(self.DISPLAYSURFACE, MINECOLOR, (left + quarter, top + quarter),
                                     (left + half + quarter, top + half + quarter))
                    pygame.draw.line(self.DISPLAYSURFACE, MINECOLOR, (left + quarter, top + half + quarter),
                                     (left + half + quarter, top + quarter))
                else:
                    for i in range(1, 9):
                        if self.field[box_x][box_y] == "[" + str(i) + "]":
                            if i in range(1, 3):
                                textColor = TEXTCOLOR_1
                            else:
                                textColor = TEXTCOLOR_2
                            self.drawText(str(i), self.BASICFONT, textColor, self.DISPLAYSURFACE, center_x, center_y)

    def showNumbers(self, revealedBoxes, box_x, box_y, zeroListXY):
        # modifies revealedBox data strucure if chosen box_x & box_y is [0]
        # show all boxes using recursion

        revealedBoxes[box_x][box_y] = True
        self.revealAdjacentBoxes(revealedBoxes, box_x, box_y)
        for i, j in self.getAdjacentBoxesXY(box_x, box_y):
            if self.field[i][j] == "[0]" and [i, j] not in zeroListXY:
                zeroListXY.append([i, j])
                self.showNumbers(revealedBoxes, i, j, zeroListXY)

    def revealAdjacentBoxes(self, revealedBoxes, box_x, box_y):
        # modifies revealedBoxes data structure so that all adjacent boxes to (box_x, box_y) are set to True

        if box_x != 0:
            revealedBoxes[box_x - 1][box_y] = True
            if box_y != 0:
                revealedBoxes[box_x - 1][box_y - 1] = True
            if box_y != FIELDHEIGHT - 1:
                revealedBoxes[box_x - 1][box_y + 1] = True
        if box_x != FIELDWIDTH - 1:
            revealedBoxes[box_x + 1][box_y] = True
            if box_y != 0:
                revealedBoxes[box_x + 1][box_y - 1] = True
            if box_y != FIELDHEIGHT - 1:
                revealedBoxes[box_x + 1][box_y + 1] = True
        if box_y != 0:
            revealedBoxes[box_x][box_y - 1] = True
        if box_y != FIELDHEIGHT - 1:
            revealedBoxes[box_x][box_y + 1] = True

    def getAdjacentBoxesXY(self, box_x, box_y):
        # get box XY coordinates for all adjacent boxes to (box_x, box_y)

        adjacentBoxesXY = []

        if box_x != 0:
            adjacentBoxesXY.append([box_x - 1, box_y])
            if box_y != 0:
                adjacentBoxesXY.append([box_x - 1, box_y - 1])
            if box_y != FIELDHEIGHT - 1:
                adjacentBoxesXY.append([box_x - 1, box_y + 1])
        if box_x != FIELDWIDTH - 1:
            adjacentBoxesXY.append([box_x + 1, box_y])
            if box_y != 0:
                adjacentBoxesXY.append([box_x + 1, box_y - 1])
            if box_y != FIELDHEIGHT - 1:
                adjacentBoxesXY.append([box_x + 1, box_y + 1])
        if box_y != 0:
            adjacentBoxesXY.append([box_x, box_y - 1])
        if box_y != FIELDHEIGHT - 1:
            adjacentBoxesXY.append([box_x, box_y + 1])

        return adjacentBoxesXY

    def drawCovers(self, revealedBoxes, markedMines):
        # uses revealedBox FIELDWIDTH x FIELDHEIGHT data structure to determine whether to draw box covering mine/number
        # draw red cover instead of gray cover over marked mines

        for box_x in range(FIELDWIDTH):
            for box_y in range(FIELDHEIGHT):
                if not revealedBoxes[box_x][box_y]:
                    left, top = self.getLeftTopXY(box_x, box_y)
                    if [box_x, box_y] in markedMines:
                        pygame.draw.rect(self.DISPLAYSURFACE, MINEMARK_COV, (left, top, BOXSIZE, BOXSIZE))
                    else:
                        pygame.draw.rect(self.DISPLAYSURFACE, BOXCOLOR_COV, (left, top, BOXSIZE, BOXSIZE))

    def drawText(self, text, font, color, surface, x, y):
        # function to easily draw text and also return object & rect pair

        textobj = font.render(text, True, color)
        textrect = textobj.get_rect()
        textrect.centerx = x
        textrect.centery = y
        surface.blit(textobj, textrect)

    def drawButton(self, text, color, bgcolor, center_x, center_y):
        # similar to drawText but text has bg color and returns obj & rect

        butSurf = self.BASICFONT.render(text, True, color, bgcolor)
        butRect = butSurf.get_rect()
        butRect.centerx = center_x
        butRect.centery = center_y

        return butSurf, butRect

    def getLeftTopXY(self, box_x, box_y):
        # get left & top coordinates for drawing mine boxes

        left = XMARGIN + box_x * (BOXSIZE + GAPSIZE)
        top = YMARGIN + box_y * (BOXSIZE + GAPSIZE)
        return left, top

    def getCenterXY(self, box_x, box_y):
        # get center coordinates for drawing mine boxes

        center_x = XMARGIN + BOXSIZE / 2 + box_x * (BOXSIZE + GAPSIZE)
        center_y = YMARGIN + BOXSIZE / 2 + box_y * (BOXSIZE + GAPSIZE)
        return center_x, center_y

    def getBoxAtPixel(self, x, y):
        # gets coordinates of box at mouse coordinates

        for box_x in range(FIELDWIDTH):
            for box_y in range(FIELDHEIGHT):
                left, top = self.getLeftTopXY(box_x, box_y)
                boxRect = pygame.Rect(left, top, BOXSIZE, BOXSIZE)
                if boxRect.collidepoint(x, y):
                    return box_x, box_y
        return None, None

    def highlightBox(self, box_x, box_y):
        # highlight box when mouse hovers over it

        left, top = self.getLeftTopXY(box_x, box_y)
        pygame.draw.rect(self.DISPLAYSURFACE, HILITECOLOR, (left, top, BOXSIZE, BOXSIZE), 4)

    def highlightButton(self, butRect):
        # highlight button when mouse hovers over it

        linewidth = 4
        pygame.draw.rect(self.DISPLAYSURFACE, HILITECOLOR, (
            butRect.left - linewidth, butRect.top - linewidth, butRect.width + 2 * linewidth,
            butRect.height + 2 * linewidth),
                         linewidth)

    def gameWon(self, revealedBoxes):
        # check if player has revealed all boxes

        notMineCount = 0

        for box_x in range(FIELDWIDTH):
            for box_y in range(FIELDHEIGHT):
                if revealedBoxes[box_x][box_y]:
                    if self.field[box_x][box_y] != "[X]":
                        notMineCount += 1

        if notMineCount >= (FIELDWIDTH * FIELDHEIGHT) - MINESTOTAL:
            return True
        else:
            return False

    def gameOverAnimation(self, revealedBoxes, markedMines, result):
        # makes background flash red (loss) or blue (win)

        origSurf = self.DISPLAYSURFACE.copy()
        flashSurf = pygame.Surface(self.DISPLAYSURFACE.get_size())
        flashSurf = flashSurf.convert_alpha()
        animationSpeed = 20

        if result == "WIN":
            r, g, b = BLUE
        else:
            r, g, b = RED

        for i in range(5):
            for start, end, step in ((0, 255, 1), (255, 0, -1)):
                for alpha in range(start, end, animationSpeed * step):  # animation loop
                    self.checkForKeyPress()
                    flashSurf.fill((r, g, b, alpha))
                    self.DISPLAYSURFACE.blit(origSurf, (0, 0))
                    self.DISPLAYSURFACE.blit(flashSurf, (0, 0))
                    pygame.draw.rect(self.DISPLAYSURFACE, FIELDCOLOR, (
                        XMARGIN - 5, YMARGIN - 5, (BOXSIZE + GAPSIZE) * FIELDWIDTH + 5,
                        (BOXSIZE + GAPSIZE) * FIELDHEIGHT + 5))
                    self.drawField()
                    self.drawMinesNumbers()
                    tipFont = pygame.font.SysFont(FONTTYPE, 16)
                    self.drawText("Совет: выделите поле и нажмите пробел (вместо щелчка мышью)", tipFont, TEXTCOLOR_3,
                                  self.DISPLAYSURFACE, WINDOWWIDTH / 2, WINDOWHEIGHT - 60)
                    self.drawText("чтобы отметить области, которые, как вы думаете, содержат мины.", tipFont, TEXTCOLOR_3, self.DISPLAYSURFACE,
                                  WINDOWWIDTH / 2, WINDOWHEIGHT - 40)
                    self.RESET_SURF, self.RESET_RECT = self.drawButton("Заново", TEXTCOLOR_3, RESETBGCOLOR, WINDOWWIDTH / 2, WINDOWHEIGHT - 120)
                    self.drawCovers(revealedBoxes, markedMines)
                    pygame.display.update()
                    self.FPSCLOCK.tick(FPS)

    def terminate(self):
        pygame.quit()
        sys.exit()

    def checkForKeyPress(self):
        # check if quit or any other key is pressed

        if len(pygame.event.get(QUIT)) > 0:
            self.terminate()

        keyUpEvents = pygame.event.get(KEYUP)
        if len(keyUpEvents) == 0:
            return None
        if keyUpEvents[0].key == K_ESCAPE:
            self.terminate()
        return keyUpEvents[0].key


if __name__ == "__main__":
    field = MineField()
    field.game()
