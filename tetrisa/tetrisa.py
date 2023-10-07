import pygame
import sys
import random
import math
import copy
from pygame.locals import *

# Setup Main Game
pygame.init()
mainClock = pygame.time.Clock()

#~~~~~~~~~#
#Constants#
#~~~~~~~~~#

# Globals for setting game properties
BLOCKSIZE = 32
WINDOWWIDTH = 800
WINDOWHEIGHT = 576
FPS = 20 #Frames per second

# Semi-globals: these are modified through the menu screen settings
GAMESIZE = 8 #Number between 8 and 16
GAMESPEED = 20       

# Globals for graphics
GRIDSIZE = 32 #Size in pixels for 1 individual block (default=32)
LIGHTNINGSIZE = 3 #Size for drawing the lightning/shadow on the blocks
YSIZE = int(WINDOWHEIGHT/BLOCKSIZE)
XSIZE = int(WINDOWWIDTH/BLOCKSIZE)

# Globals for different colors used within the game
BLACK = (0,0,0)
GREYDARKER = (24,24,24)
GREYDARK = (32,32,32)
GREY = (64,64,64)
GREYLIGHT = (96,96,96)
WHITE = (255,255,255)
REDDARK = (48,0,0)
#Globals for block colors
CYAN = (0,255,255)
YELLOW = (255,255,0)
PURPLE = (128,0,255)
GREEN = (0,255,0)
BLUE = (0,0,255)
RED = (255,0,0)
ORANGE = (255,128,0)

# Tetris blocks are coded through vector format. The format for coding these is:
# [-1,0] [0,0] [1,0] [2,0] 
# [-1,1] [0,1] [1,1] [2,1]
# For example, "E" is coded as   E
#                              E E E
I = [[-1,1],[0,1],[1,1],[2,1]]
Z = [[-1,0],[0,0],[0,1],[1,1]]
S = [[-1,1],[0,1],[0,0],[1,0]]
E = [[-1,1],[0,1],[0,0],[1,1]]
O = [[0,0],[1,0],[0,1],[1,1]]
L = [[-1,1],[0,1],[1,1],[1,0]]
J = [[-1,0],[-1,1],[0,1],[1,1]]

# Lastly, constant for coding halfway point in matrix. Formula can be adjusted for different bias
# (i.e. materialize earlier or later). 
HALFWAY = round((GAMESIZE/2)-0.25)

#~~~~~#
#Setup#
#~~~~~#
#Sets up the game window
window = pygame.display.set_mode((WINDOWWIDTH,WINDOWHEIGHT),0,32)
pygame.display.set_caption('Tetrisa')

#Sets up sounds and music 
rotateFieldSound=pygame.mixer.Sound('selectFieldD.wav')
lineClearSound=pygame.mixer.Sound('lineClear.wav')
rotateBlockSound=pygame.mixer.Sound('rotateBlock.wav')
gameOverSound=pygame.mixer.Sound('gameOver.wav')
optionConfirmSound=pygame.mixer.Sound('optionConfirm.wav')
selectFieldSound=pygame.mixer.Sound('confirmFieldD.wav')
pygame.mixer.music.load('tetrisaThemeB.mp3')
pygame.mixer.music.set_volume(0.2)
pygame.mixer.music.play(-1, 0)

#Sets up text for the game. (condense into function maybe)
font=pygame.font.SysFont('couriernew',24,bold=True)
strNextBlock=font.render('NEXT BLOCK', True, WHITE, BLACK)
strScore=font.render('SCORE', True, PURPLE, BLACK)
rectNextBlock=strNextBlock.get_rect()
rectNextBlock.x=GRIDSIZE*19-8
rectNextBlock.y=GRIDSIZE*1
rectScore=strNextBlock.get_rect()
rectScore.x=GRIDSIZE*20-8
rectScore.y=GRIDSIZE*6

#Sets up text for the menu
bigFont=pygame.font.SysFont('couriernew',96,bold=False)
strTetrisa=bigFont.render('TETRISA', True, WHITE, BLACK)
rectTetrisa=strTetrisa.get_rect()
rectTetrisa.x=GRIDSIZE*6
rectTetrisa.y=GRIDSIZE*4-8


#~~~~~~~~~#
#Main Code#
#~~~~~~~~~#


#Create a new matrix with size "size". Matrix is a list with every item representing a vector
# position in the grid, for example [0,0],[1,0],[2,0] etc. for every possible [x,y] value
def createMatrix(size):
    matrix=[]
    for r in range(size):
        for c in range(size):
            matrix.append([c,r])
    return matrix

#Generates a random block and random color for the block. Takes both from the global list. Outputs
# both, which are used subsequently in the game
def generateBlock():
    block = [I,Z,S,E,O,L,J][random.randint(0,6)]
    color = [CYAN,YELLOW,PURPLE,GREEN,BLUE,RED,ORANGE][random.randint(0,6)]
    block = block.copy()
    return [block, color]

#Creates a spawn point for the new blocks to fall from based on the GAMESIZE in the global constants.
# There are four spawn points in total given there are 4 directions the block can fall.
def getSpawnPoint(direction):
    spawn = round(((GAMESIZE)/2)+0.1)-1
    matrix_size = GAMESIZE-1
    spawn_list = [[spawn,0],[matrix_size,spawn],[spawn,matrix_size],[0,spawn]]
    return spawn_list[direction]

#(No use currently but kept for posteriority)
def getHalfwayPoint(direction):
    halfway=round((GAMESIZE/2)-0.25)
    #halfway_return=[[0,halfway]
    return halfway

#This function rotates a block and is used later on for if the player wants to rotate the block it
# is currently controlling 90 degrees. There's two seperate rotating algorithms: one for the I-block
# and the other for blocks that occupy a 3x3 block (I-block has special matrix of 4x4)
def rotateBlock(block):
    r_b=block.copy() #Create a copy of the block
    #Checks if any of the vectors in the block match vectors that can only be found in the 4x4 block
    if any([item in block for item in [[2, 1], [1, 3], [2, 2], [0, 3]]]):
        for s in range(len(r_b)):
            r_b[s]=[int((-(r_b[s][1]-1.5))+0.5),int((r_b[s][0]-0.5)+1.5)]
    elif block != O:
        for s in range(len(r_b)):
            r_b[s]=[-(r_b[s][1]-1),r_b[s][0]+1]
    return r_b    

#Function for rotating an entire given matrix 90 degrees to the right. Takes a list of vectors and calculates what
# the positions would be if the matrix were rotated and subsequently outputs these. 
def rotateMatrix(matrix):
    r_m=copy.deepcopy(matrix)
    for l in range(len(matrix)):
        r_m[l][0]=(GAMESIZE-1)-matrix[l][1]
        r_m[l][1]=matrix[l][0]
    return r_m
    
#Function below just takes the above rotateBlock function and executes it multiple times. Useful to rotate a block 180
# or 270 degrees
def blockRotation(block,times):
    m_b=block.copy() #modified_block
    for t in range(times):
        m_b=rotateBlock(m_b)
    return m_b

#Same for matrix, allows for easy multiple rotations.
def matrixRotation(matrix,times):
    m_m=copy.deepcopy(matrix) #modified_matrix
    for t in range(times):
        m_m=rotateMatrix(m_m)
    return m_m

#pasteBlock takes the block vectors and the position of the block and puts them together to calculate the actual
# position of the block on the gamefield. Used for collisions later on
def pasteBlock(block,blockposition):
    m_b=copy.deepcopy(block) #modified_block
    for v in range(len(block)):
        m_b[v][0]+=blockposition[0]
        m_b[v][1]+=blockposition[1]
    return m_b

#Return all sublists into one big list. Useful for checking blocklist later
def subList(anylist):
    return_list=[]
    for r in anylist:
        for z in r:
            return_list.append(z)
    return return_list

#Get list for clearing lines
def getQuatList():
    quat_count=round(GAMESIZE/2-0.6) #quat = 4 line clear
    quat_vectors=[]
    for c in range(quat_count):
        quat_vectors.append([]) 
    #This for creates the vector
    for q in range(quat_count):
        for s in range(q,GAMESIZE-q):
            quat_vectors[q].append([q,s])
            quat_vectors[q].append([s,q])
            quat_vectors[q].append([GAMESIZE-q-1,s])
            quat_vectors[q].append([s,GAMESIZE-q-1])
    #Following section is for removing all duplicates.
    quat_output=[]
    for c in range(quat_count):
        quat_output.append([])   
    for z in range(len(quat_vectors)):
        for n in range(len(quat_vectors[z])):
            if quat_vectors[z][n] in quat_output[z]:
                pass
            else:
                quat_output[z].append(quat_vectors[z][n])
    return quat_output
    
#~~~~~~~~~~~~~~~~~~~~~~~~#
#Player Control Functions#
#~~~~~~~~~~~~~~~~~~~~~~~~#

#Rotates the active block once. Same as rotateBlock but the player-function version (not strictly different)
def playerRotate(block):
    return rotateBlock(block)

#Factilitates block movement (left, right, up, down). It takes the current position of the block and also a
# movement vector and returns the new blockposition. E.g. blockPos of [1,4] with movement [0,1] results in [1,5]
def playerMove(blockposition,movement):
    b_p=copy.deepcopy(blockposition) #block_position    
    b_p[0]+=movement[0]
    b_p[1]+=movement[1]   
    return b_p

#Rotates the entire gamefield.
def playerFieldRotate(olddirection,newdirection,block,blockposition):
    #First, calculate how many rotations are needed by comparing the old and new direction
    rotation_amount=((newdirection-olddirection)+4)%4
    #Create copies for safety
    b=copy.deepcopy(block)
    p=copy.deepcopy(blockposition)
    #Goes as follows: use pasteBlock to get the actual position of the block on the field...
    p_b=pasteBlock(b,p) #pasted_block
    #...then rotate the block vectors an x amount.
    p_b=matrixRotation(p_b,rotation_amount)
    #Now rotate the block ITSELF. This block "b" can then be compared to "p_b" to calculate difference!
    b=blockRotation(b,rotation_amount)
    #Look at b and how far the first vector is to [0,0]
    delta_xy=[0-b[0][0],0-b[0][1]]
    #Add this difference back to the "p_b" to determine what the anchor position would be. Store this one
    new_block_position=[p_b[0][0]+delta_xy[0],p_b[0][1]+delta_xy[1]]
    #Final exception for O-block which doesn't rotate. If it's an O-block simply get the position by retrieving
    # if from the topright (which is always the anchor point)
    if block==O:
        new_block_position=min(p_b)
    new_block=b
    return [new_block,new_block_position]

#~~~~~~~~~~~~~~#
#Game functions#
#~~~~~~~~~~~~~~#

#Checks whether move any new move, be it rotation of the block or a player moving the block, is valid.
def validMove(block,blockposition,gamematrix,blocklist=None,gamedirection=0):
    #First get all the vectors of the block segments that have materialized (i.e. crossed the midline
    # of the gamefield)
    m_b=materializedBlocks(block,blockposition,gamedirection) #materialized_blocks
    invalid_count=0 #This variable will count how many of the new block positions will be invalid.
    b_l=copy.deepcopy(blocklist) #block_list. Safety copy
    t_b=copy.deepcopy(pasteBlock(block,blockposition)) #test_block
    #Check if all the block parts are valid
    for v in range(len(t_b)):
        #This first one checks if the new position fits in the gamematrix. This is used to make sure
        # the block doesn't go out of bounds. If any block parts are OOB a count gets added to invalid_count
        invalid_count+=t_b[v] not in gamematrix
        #Next, see if there's any already placed blocks occupying the space the block wants to move to.
        # If so, add another count to invalid_count.
        if(blocklist!=None)&(t_b[v] in m_b):
            invalid_count+=any(t_b[v] in i for i in blocklist)
        if(blocklist!=None)&(t_b[v] in m_b):
            invalid_count+=any(t_b[v] in i for i in blocklist)
    #print(str(invalid_count)) #Useful while testing
    return invalid_count<1

#Blocktick is activated to move the block down automatically. (Aanpassen, naar lijst formaat)
# 0=[0,1],1=[-1,0],2=[0,-1],3=[1,0]. 
def blockTick(block,blockposition,gamedirection):
    m_v=[(gamedirection%2)*(gamedirection-2),(((gamedirection+1)%2)-((gamedirection+2)*((gamedirection+1)%2)))+(((gamedirection+1)%2)*2)]
    tick=playerMove(blockposition,m_v)
    return tick

#When blocks cross the midline of the game, they gets materialized. Below function looks at which
# parts of the block the player is currently controlling qualify for that.
def materializedBlocks(block,blockposition,gamedirection):
    #First, set the condition to check which differs based on gamedirection. 
    m_v=[[0,HALFWAY],[HALFWAY-1,GAMESIZE],[GAMESIZE,HALFWAY-1],[HALFWAY,0]][gamedirection] #midwaypoint_vector
    #Create test variabel, copy for safety
    t_b=copy.deepcopy(pasteBlock(block,blockposition)) #test_block
    return_list = []
    #Right/down gamedirection have a different check since the blocks move up/left, meaning
    # lesser than check is used.
    for v in range(len(t_b)):
        if((gamedirection==0)|(gamedirection==3))&((t_b[v][0]>=m_v[0])&(t_b[v][1]>=m_v[1])):
            return_list.append(t_b[v])
        if((gamedirection==1)|(gamedirection==2))&((t_b[v][0]<=m_v[0])&(t_b[v][1]<=m_v[1])):
            return_list.append(t_b[v])
    return return_list

def clearRow(blocklist,quatlist):
    #Create copy of blocklist, explode
    block_list=copy.deepcopy(blocklist)
    block_list=subList(block_list)
    #For checking how many lines are cleared
    quat_check=[]
    for q in quatlist:
        quat_check.append(all(item in block_list for item in q))
    #If there's no lines cleared, return original blocklist and end function
    if any(quat_check)!=True:
        return blocklist
    print('yes')
    #If there are any lines cleared...
    #First, fancy flashing line
    offset=round(((16-GAMESIZE)/2)-0.1)+1
    for c in range(len(quatList)):
        if quat_check[c]==True:
            for b in range(len(quatList[c])):
                drawBlock(WHITE,quatList[c][b][0]+offset,quatList[c][b][1]+offset)
    #Wait, play sound
    lineClearSound.play() 
    pygame.display.update()
    pygame.time.wait(500)
    
    #Create direction to where blocks will moved (random to side or vertical)
    vertical=random.choice([True,False])
    #Create a second copy of blocklist, will be modified and output
    block_output=copy.deepcopy(blocklist)
    #For every quat: check if it is cleared, if yes, remove those blocks
    # from blockList. If not then move blocks for every previous clear
    for c in range(len(quatList)):
        #If a line is cleared
        if quat_check[c]==True:
            #Remove all blocks corresponding to the quat from the general blocklist
            for b in range(len(blocklist)):
                for s in range(len(blocklist[b])):
                    if blocklist[b][s] in quatlist[c]:
                        print(blocklist[b][s])
                        block_output[b][s]=[50,50]
            print('Clear')
            #Add 1 to the total amount of lines cleared
    #Shift all the remainder blocks away from the center. Check how many True's before and more
    # same amount
    for b in range(len(block_output)):
        for v in range(len(block_output[b])):
            if block_output[b][v]!=[] and block_output[b][v]!=[50,50]:
                print('before:')
                print(block_output[b][v])
                #Check how many lines before were cleared to determine offset
                quat_no=-1
                for q in range(len(quatList)):
                    if block_output[b][v] in quatList[q]:
                        quat_no=q
                if quat_no==-1:
                    quat_no=len(quatList)+1
                shift_offset=sum(quat_check[:quat_no])
                #Get shift direction from function below. Now we have shift_amount(aka direction) and offset    
                shift_direction=blockShift(block_output[b][v])
                shift_direction[0]=shift_direction[0]*shift_offset
                shift_direction[1]=shift_direction[1]*shift_offset
                block_output[b][v]=[block_output[b][v][0]+shift_direction[0],block_output[b][v][1]+shift_direction[1]]
                print('after:')
                print(block_output[b][v])
    #Hierbovenaan toevoegen: hoeveel die beweegt afhankelijk van hoeveel clears er zijn voor
    # bijv: als 2 lines ervoor gecleared zijn: dan 2 op x/y bewegen

    return block_output


#Shifts the block 1 position towards sides (whichever closest) after line is cleared
#For determining movement of existing blocks after a line is cleared so it falls away from the center
def blockShift(vector):
    seperator=round((GAMESIZE/2)-0.1)
    if vector[0]<seperator and vector[1]<seperator:
        return [-1,-1]
    if vector[0]>=seperator and vector[1]<seperator:
        return [1,-1]
    if vector[0]<seperator and vector[1]>=seperator:
        return [-1,1]
    if vector[0]>=seperator and vector[1]>=seperator:
        return [1,1]

#~~~~~~~~~~~~~~~~~#
#Graphic Functions#
#~~~~~~~~~~~~~~~~~#

#Divides game area into grid. Each grid is GRIDSIZE wide/long. Easier
# for drawing graphics
def getGrid(gridx,gridy):
    x=0+gridx*GRIDSIZE
    y=0+gridy*GRIDSIZE
    return x,y

#Draws a block of a certain color at grid position x/y. Can save performance
# by calculating all shadow/light upfront and only drawing with drawBlock
def drawBlock(color,gridx,gridy,solid=True):
    block_outline=(solid-1)*(-1*LIGHTNINGSIZE)
    color_base=list(color[:])
    color_dark=copy.deepcopy(color_base)
    color_light=copy.deepcopy(color_base)
    #Short loop for for calculating light/shadowy sides on block
    for c in range(3):
        if color_light[c]<=200:
            color_light[c]=160
        if color_dark[c]==255:
            color_dark[c]=192
        elif color_dark[c]==128:
            color_dark[c]=64
    #Exception for grey to manually adjust/finetune
    if color==GREY:
        color_dark=[32,32,32]
        color_light=[96,96,96]
    #Same for black
    if color==BLACK:
        color_dark=[32,32,32]
        color_light=[96,96,96]        
    #Exception for non-materialized blocks to change color easily is constant        
    x,y=getGrid(gridx,gridy)
    pygame.draw.rect(window, color_base, (x,y,GRIDSIZE,GRIDSIZE),block_outline)
    pygame.draw.rect(window, color_dark, (x+GRIDSIZE-LIGHTNINGSIZE,y,LIGHTNINGSIZE,GRIDSIZE),block_outline)
    pygame.draw.rect(window, color_dark, (x,y+GRIDSIZE-LIGHTNINGSIZE,GRIDSIZE,LIGHTNINGSIZE),block_outline)
    pygame.draw.rect(window, color_light, (x,y,GRIDSIZE,LIGHTNINGSIZE),block_outline)
    pygame.draw.rect(window, color_light, (x,y,LIGHTNINGSIZE,GRIDSIZE),block_outline)
    #pygame.display.update() #DIT VERWIJDEREN LATER ALLEEN VOOR CHECK

#Draw the UI blocks around the gamefield
def drawUIBlocks(color,leftside=False):
    #Drawing the background (grey blocks)
    for r in range(XSIZE):
        for c in range(YSIZE):
            drawBlock(color,r,c)
    #Drawing the gamefield. First check the coordinates to draw
    offset=round(((16-GAMESIZE)/2)-0.1)
    x,y=getGrid(1,1)
    x=x+offset*GRIDSIZE
    y=y+offset*GRIDSIZE
    #When playing the actual game itself, draw left side of gaming area
    if leftside==True:
        pygame.draw.rect(window, GREYLIGHT, (x-LIGHTNINGSIZE,y-LIGHTNINGSIZE,LIGHTNINGSIZE,LIGHTNINGSIZE+(GRIDSIZE*GAMESIZE)))
        pygame.draw.rect(window, GREYLIGHT, (x-LIGHTNINGSIZE,y-LIGHTNINGSIZE,LIGHTNINGSIZE+(GRIDSIZE*GAMESIZE),LIGHTNINGSIZE))

#Draw the background dots
def drawDots(gamedirection):
    #For compensating for border around the game
    offset=round(((16-GAMESIZE)/2)-0.1)
    x,y=getGrid(1+offset,1+offset)
    #Get a simple grid to put into the for loops so it'll draw a dot for every vector coordinate. One less
    # since you don't want dots to hug the sides of the gamefield
    dot_locations=createMatrix(GAMESIZE-1)
    #get halfwaypoint
    halfway_point=[[GAMESIZE,HALFWAY],[HALFWAY-1,0],[0,HALFWAY-1],[HALFWAY,GAMESIZE]][gamedirection]

    for h in dot_locations:
        dx,dy=h
        dx=x+(dx+1)*GRIDSIZE-LIGHTNINGSIZE
        dy=y+(dy+1)*GRIDSIZE-LIGHTNINGSIZE
        
        if((gamedirection==0)|(gamedirection==3)):
            if h[0]<halfway_point[0] and h[1]<(halfway_point[1]):
                pygame.draw.rect(window, GREYDARK, (dx,dy,LIGHTNINGSIZE,LIGHTNINGSIZE))                
            else:
                pygame.draw.rect(window, REDDARK, (dx,dy,LIGHTNINGSIZE,LIGHTNINGSIZE))

        if((gamedirection==1)|(gamedirection==2)):
            if h[0]>=halfway_point[0] and h[1]>=halfway_point[1]:
                pygame.draw.rect(window, GREYDARK, (dx,dy,LIGHTNINGSIZE,LIGHTNINGSIZE))
            else:
                pygame.draw.rect(window, REDDARK, (dx,dy,LIGHTNINGSIZE,LIGHTNINGSIZE))

def drawUINextBlock(nextBlock):
    pygame.draw.rect(window, BLACK, (18*GRIDSIZE,1*GRIDSIZE,6*GRIDSIZE,4*GRIDSIZE))
    window.blit(strNextBlock, rectNextBlock)
    if nextBlock[0]==O:
        for v in range(len(nextBlock[0])):
            gridx=20+nextBlock[0][v][0]
            gridy=2.25+nextBlock[0][v][1]
            drawBlock(RED,gridx,gridy,False)
    elif nextBlock[0]==I:
        for v in range(len(nextBlock[0])):
            gridx=20+nextBlock[0][v][0]
            gridy=1.75+nextBlock[0][v][1]
            drawBlock(RED,gridx,gridy,False)
    else:
        for v in range(len(nextBlock[0])):
            gridx=20.5+nextBlock[0][v][0]
            gridy=2.25+nextBlock[0][v][1]
            drawBlock(RED,gridx,gridy,False)

def drawUIScore(playerScore):
    pygame.draw.rect(window, BLACK, (18*GRIDSIZE,6*GRIDSIZE,6*GRIDSIZE,2*GRIDSIZE))
    #Draw score text
    window.blit(strScore, rectScore)

    #Draw score itself
    strPlayerScore=font.render(str(playerScore), True, PURPLE, BLACK)
    rectPlayerScore=strPlayerScore.get_rect()
    rectPlayerScore.centerx=GRIDSIZE*21
    rectPlayerScore.centery=GRIDSIZE*7+12
    window.blit(strPlayerScore, rectPlayerScore)

#Draw the game itself
def drawGame(block,color,blockposition,blocklist,colorlist,materializedblocks,gamedirection):
    #calculate offset first. Also, for drawing gaming field, calculate x and y
    offset=round(((16-GAMESIZE)/2)-0.1)
    x,y=getGrid(1,1)
    x=x+offset*GRIDSIZE
    y=y+offset*GRIDSIZE    
    
    offset=offset+1 #Always add 1 more offset to account for gamegrid not starting at top of gamewindow but a bit below
    #Get the actual position of block in gamegrid with pasteBlock
    active_block=pasteBlock(block,blockposition)
    
    #Redraw black backdrop
    pygame.draw.rect(window, BLACK, (x,y,GRIDSIZE*GAMESIZE,GRIDSIZE*GAMESIZE))

    #Draw dots
    drawDots(gamedirection)

    #Draw blocks already put down
    for b in range(len(blocklist)):
        for v in range(len(blocklist[b])):
            drawBlock(colorlist[b],blocklist[b][v][0]+offset,blocklist[b][v][1]+offset)
            
    #Draw active block. If it's in materialized list, draw solid, else draw outline only
    for v in range(len(active_block)):
        if active_block[v] in materializedblocks:
            drawBlock(color,active_block[v][0]+offset,active_block[v][1]+offset)
        else:
            drawBlock(RED,active_block[v][0]+offset,active_block[v][1]+offset,False)

#############
#MENU SCREEN#
#############

def drawText(string,largetext,gridx,gridy,bolded,textcolor):
    if largetext==True:
        string=bigFont.render(string, True, textcolor, BLACK)
    else:
        string=font.render(string, True, textcolor, BLACK)
    rect_string=string.get_rect()
    rect_string.x=GRIDSIZE*gridx
    rect_string.y=GRIDSIZE*gridy
    window.blit(string, rect_string)

def drawSquare(gridx,gridy,gridwidth,gridheight,color):
    pygame.draw.rect(window, color, (gridx*GRIDSIZE,gridy*GRIDSIZE,gridwidth*GRIDSIZE,gridheight*GRIDSIZE))

def drawCursor(gridx,gridy):
    x=gridx*GRIDSIZE
    y=gridy*GRIDSIZE
    pygame.draw.polygon(window, WHITE, [(x,y),(x+10,y+7),(x,y+14)],width=2)

def placeCursor(menu,position):
    x=10
    y=11.5
    if menu==0:        
        drawCursor(10,11.7+position)
    if menu==1:
        if position==0:
            drawCursor(7,2.7+position)
        else:
            drawCursor(7,2.7+position+2)

def drawMenuScreen():
    drawUIBlocks(GREY,False)
    #Draw main banner
    drawSquare(4,3,17,5,BLACK)
    drawText('TETRISA',True,6,4,False,WHITE)
    #Draw menu screen
    drawSquare(8,11,8,4,BLACK)
    drawText('PLAY',False,11,11.5,False,WHITE)
    drawText('SETTINGS',False,11,12.5,False,WHITE)
    drawText('TUTORIAL',False,11,13.5,False,WHITE)    
    #Draw credits
    drawSquare(17,17,8,1,BLACK)
    drawText('made by: Krirby',False,18,17,False,WHITE)

def drawSettings():
    drawSquare(4.95,1.95,15.15,14.15,GREYLIGHT)
    drawSquare(5,2,15,14,BLACK)
    #text gamesize
    drawText('Grid Size',False,8,2.5,False,WHITE)
    drawText(' 8  9 10 11',False,14.7,2.5,False,WHITE)
    drawText('12 13 14 15',False,14.7,3.5,False,WHITE)
    drawText('16',False,14.7,4.5,False,WHITE)    
    #text control scheme
    drawText('Control Scheme',False,8,5.5,False,WHITE)
    drawText('1 2 3',False,14.7,5.5,False,WHITE)
    #text difficulty
    drawText('Difficulty',False,8,6.5,False,WHITE)
    drawText('NO EZ HA',False,14.7,6.5,False,WHITE)    
    #text music
    drawText('Music',False,8,7.5,False,WHITE)
    drawText('on off',False,14.7,7.5,False,WHITE)
    #text exit
    drawText('Exit',False,8,8.5,False,WHITE)

def drawSupText(textno):
    if textno==0:
        drawText('_______________________________',False,6,9.5,False,WHITE)
        drawText('Sets the size of the game grid.',False,6,10.5,False,WHITE)
        drawText('Recommended setting is 16.     ',False,6,11.5,False,WHITE)
        drawText('                               ',False,6,12.5,False,WHITE)
        drawText('                               ',False,6,13.5,False,WHITE)
        drawText('                               ',False,6,14.5,False,WHITE)        
    if textno==1:
        drawText('_______________________________',False,6,9.5,False,WHITE)
        drawText('Sets the control scheme for fie',False,6,10.5,False,WHITE)
        drawText('ld diretion rotation. (1) is di',False,6,11.5,False,WHITE)
        drawText('rection keys only, (2) is Z-key',False,6,12.5,False,WHITE)
        drawText('for determining direction, (3) ',False,6,13.5,False,WHITE)
        drawText('is combined.',False,6,14.5,False,WHITE)
    if textno==2:
        drawText('_______________________________',False,6,9.5,False,WHITE)
        drawText('Sets the game difficulty (EASY)',False,6,10.5,False,WHITE)
        drawText('/(NORMAL)/(HARD). Setting of   ',False,6,11.5,False,WHITE)
        drawText('Normal is the default value.   ',False,6,12.5,False,WHITE)
        drawText('                               ',False,6,13.5,False,WHITE)
        drawText('                               ',False,6,14.5,False,WHITE)          
    if textno==3:
        drawText('_______________________________',False,6,9.5,False,WHITE)
        drawText('Set music to on/off. Can be    ',False,6,10.5,False,WHITE)
        drawText('toggled during the game by     ',False,6,11.5,False,WHITE)
        drawText('pressing "M"                   ',False,6,12.5,False,WHITE)
        drawText('                               ',False,6,13.5,False,WHITE)
        drawText('                               ',False,6,14.5,False,WHITE)          
        
def drawSelector(setting,select,active=False):
    #set passive/active color
    if active==False:
        color_select=BLUE
    else:
        color_select=PURPLE

    #Grid size
    if setting==0:
        gridwidth=1.3
        gridheight=1.1        
        if select==8:
            gridx=14.5
            gridy=2.3
        if select==9:
            gridx=15.8#
            gridy=2.3
        if select==10:
            gridx=17.1#
            gridy=2.3
        if select==11:
            gridx=18.4#
            gridy=2.3            
        if select==12:
            gridx=14.5#
            gridy=3.3
        if select==13:
            gridx=15.8#
            gridy=3.3
        if select==14:
            gridx=17.1#
            gridy=3.3
        if select==15:
            gridx=18.4#
            gridy=3.3
        if select==16:
            gridx=14.5#
            gridy=4.3

    #Control Scheme
    if setting==1:
        gridwidth=0.8
        gridheight=1.1        
        if select==1:
            gridx=14.5
            gridy=5.3
        if select==2:
            gridx=15.4
            gridy=5.3
        if select==3:
            gridx=16.3
            gridy=5.3

    #Difficulty
    if setting==2:
        gridwidth=1.4
        gridheight=1.1        
        if select==1:
            gridx=14.5
            gridy=6.3
        if select==2:
            gridx=15.8
            gridy=6.3
        if select==3:
            gridx=17.1
            gridy=6.3

    #Music
    if setting==3:
        gridwidth=1.6
        gridheight=1.1        
        if select==1:
            gridx=14.5
            gridy=7.3
        if select==2:
            gridx=15.9
            gridy=7.3

    #Draw the cursor
    pygame.draw.rect(window,color_select, (gridx*GRIDSIZE,gridy*GRIDSIZE,gridwidth*GRIDSIZE,gridheight*GRIDSIZE),width=4)    


def moveCursor(playercursor,direction):
    active=playercursor.get('active')
    menu=playercursor.get('menu')
    position=playercursor.get('position')
    if direction==2:
        if active==0:
            if menu==0 and position<2:
                position+=1
                rotateBlockSound.play() 
            if menu==1 and position<4:
                position+=1
                rotateBlockSound.play() 
    if direction==0:
        if active==0:
            if menu==0 and position>0:
                position-=1
                rotateBlockSound.play() 
            if menu==1 and position>0:
                position-=1
                rotateBlockSound.play() 
    return {'active':active,'menu':menu,'position':position}
            


def placeMenu(menu,position):
    drawMenuScreen()    
    if menu==1:
        drawSettings()
        drawSupText(position)
        
    
def placeSelector(menu,selector):
    if menu==1:
        drawSelector(0,selector['grid'])
        drawSelector(1,selector['control'])
        drawSelector(2,selector['diff'])
        drawSelector(3,selector['music'])
        
def drawTutorial():
    drawSquare(0.95,0.95,23.15,16.15,GREYLIGHT)
    drawSquare(1,1,23,16,BLACK)
    drawText('Thank you for playing Tetrisa!',False,1,1,False,WHITE)
    drawText('Instructions: ',False,1,2,False,WHITE)
    drawText('Tetrisa is a Tetris-like game and controls as such, ',False,1,3,False,WHITE)
    drawText('with the added feature that blocks can be placed in ',False,1,4,False,WHITE)
    drawText('four different directions instead of 1. When a new  ',False,1,5,False,WHITE)
    drawText('block is spawned, use the direction keys to decide  ',False,1,6,False,WHITE)
    drawText('which direction you want the block to fall. To      ',False,1,7,False,WHITE)
    drawText('confirm, press (z) (default control scheme). Once   ',False,1,8,False,WHITE)
    drawText('confirmed, you can use the arrow keys to move the   ',False,1,9,False,WHITE)
    drawText('block like you would in a regular tetris game. Use  ',False,1,10,False,WHITE)
    drawText('(x) to rotate the block 90 degrees.                 ',False,1,11,False,WHITE)
    drawText('Note that that each new block is totally free to    ',False,1,12,False,WHITE)
    drawText('to move until it passes the midway line! (signified ',False,1,13,False,WHITE)
    drawText('by the red dots on the game grid center). Once it   ',False,1,14,False,WHITE)
    drawText('passes the midway line you can actually place it    ',False,1,15,False,WHITE)
    drawText('among other blocks on the field.                    ',False,1,16,False,WHITE) 
    


def drawGameOver(playerscore,playerselector):
    pygame.mixer.music.unload()
    
    pygame.time.wait(1500)
    drawSquare(4.95,4.95,8.15,8.15,GREYLIGHT)
    drawSquare(5,5,8,8,BLACK)
    pygame.display.update()
    pygame.time.wait(400)
    
    drawText('GAME OVER!',False,7,6,False,PURPLE)
    pygame.display.update()
    pygame.time.wait(1200)

    drawText('Final Score:',False,6.6,7.4,False,WHITE)
    pygame.display.update()
    pygame.time.wait(1200)
    
    drawText(str(playerscore),False,8,9.2,False,YELLOW)
    pygame.display.update()
    pygame.time.wait(800)

    if playerselector['music']==1:
        pygame.mixer.music.load('endingTheme.mp3')
        pygame.mixer.music.play(-1, 0)
        pygame.mixer.music.set_volume(0.8)
        
    pygame.time.wait(2000)

####
#Menu/game loop
####

#Menu screen variables
playerCursor={'active':0,'menu':0,'position':0}
playerSelector={'grid':16,'control':1,'diff':1,'music':1}
writeGameSettings=False #If set to true, write game settings to game globals upon starting game
gameState='start_menu'
playerMenu=True #While true, playermenu loop runs
tutorialActive=False    # Toggle if tutorial is currently viewed on screen

# Main game While loop
while True:
    
    # PART 1 OF WHILE LOOP: if the game is current in the menu screen
    if gameState=='start_menu':
        drawMenuScreen()

        # Cursor movement
        for event in pygame.event.get():
            if event.type == KEYDOWN:

                # These two ifs are for moving cursor up and down
                if event.key == K_DOWN and tutorialActive==False:
                    playerCursor=moveCursor(playerCursor,2)
                if event.key == K_UP and tutorialActive==False:
                    playerCursor=moveCursor(playerCursor,0)

                # For pressing enter
                if event.key == K_RETURN or event.key == K_SPACE or event.key == K_x:
                    
                    #Option 0: start the game
                    if playerCursor['menu']==0 and playerCursor['position']==0:
                        gameState='game'
                        optionConfirmSound.play()
                        writeGameSettings=True
                    #Option 1: Bring up settings
                    elif playerCursor['menu']==0 and playerCursor['position']==1:
                        playerCursor['menu']=1
                        playerCursor['position']=0
                        optionConfirmSound.play()
                    #Option 2: Display tutorial
                    elif playerCursor['menu']==0 and playerCursor['position']==2:
                        if tutorialActive==False:
                            tutorialActive=True
                            optionConfirmSound.play()
                        else:
                            tutorialActive=False
                            optionConfirmSound.play()
                            
                    #Controls settings menu
                    elif playerCursor['menu']==1:
                        
                        #Change grid size, make it +1 or back to 8 if 16
                        if playerCursor['position']==0:
                            if playerSelector['grid']==16:
                                playerSelector['grid']=8
                            else:
                                playerSelector['grid']+=1
                        #Change control scheme
                        if playerCursor['position']==1:
                            if playerSelector['control']==3:
                                playerSelector['control']=1
                            else:
                                playerSelector['control']+=1
                        #Change difficulty setting
                        if playerCursor['position']==2:
                            if playerSelector['diff']==3:
                                playerSelector['diff']=1
                            else:
                                playerSelector['diff']+=1
                        #Turn music on/off
                        if playerCursor['position']==3:
                            if playerSelector['music']==1:
                                playerSelector['music']=2
                                pygame.mixer.music.set_volume(0)
                            else:
                                playerSelector['music']-=1
                                pygame.mixer.music.set_volume(0.2)
                        #Exit settings menu
                        if playerCursor['position']==4:
                            playerCursor['menu']=0
                            playerCursor['position']=1
                        optionConfirmSound.play()

                #Quit game if escape is pressed during menu                 
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        # Write the graphics based on above settings, update display afterwads
        placeMenu(playerCursor.get('menu'),playerCursor.get('position'))
        placeSelector(playerCursor.get('menu'),playerSelector)    
        placeCursor(playerCursor.get('menu'),playerCursor.get('position'))
        if tutorialActive==True:
            drawTutorial()
        pygame.display.update()

        # Advance frame
        mainClock.tick(FPS)

    # PART 1.5 OF  WHILE LOOP:
    # This gets executed ONCE when player starts the game initially. Gamesettings get transferred to global variables, vars for game get defined
    if writeGameSettings==True:
        GAMESIZE = playerSelector['grid']
        controlScheme=playerSelector['control']-1
        HALFWAY = round((GAMESIZE/2)-0.25)

        # Set the difficulty
        if playerSelector['diff']==1:
            GAMESPEED = 20
        elif playerSelector['diff']==2:
            GAMESPEED = 24
        elif playerSelector['diff']==3:
            GAMESPEED = 10

        # Create the gameMatrix
        gameMatrix=createMatrix(GAMESIZE) #Create gamematrix
        quatList=getQuatList() #Create a list for checking clears
        oldBlock = None     #Set blocks to none
        oldBlockPos = None

        playerScore=0

        
        gameOver=False


        # Draw the game background
        drawUIBlocks(GREY)
        print('hey')
        writeGameSettings=False
        gameDirection=0 #Set game (field) direction spawnpoint, up=0, right=1, down=2, left=3

        #halfWayPoint=GAMESIZE
        newBlock=True #Set to true to create new block at the start of the game
        timer=0 #Ticks every frame, for calculating speed at which blocks drop (game difficulty)
        blockList=[] #Contains list of every past block thats already been set onto the game field.
        colorList=[] #The corresponding colors. The color of each seperate block is a seperate sublist
        #dirConfirmed=False #For checking whether direction is chosen by the player
                            # to definitively drop the block. Cannot change for current block once set.
                            # Put this in newBlock code block so it can trigger when creating new block
        nextBlock=[] #Stores the block after the current one
        #These variables are used to check if anything has changed so the game area doesn't need to be
        # redrawn every frame if not necessary
        drawGameOverScreen=False #for drawing game over screen once

    #PART 2 OF WHILE LOOP:           
    if gameState=='game' and gameOver==False:
        #Generate new block 
        if newBlock==True:
            if nextBlock==[]:
                block,color=generateBlock() #Create new block, add its colors to list
            else:
                block,color=nextBlock
            nextBlock=generateBlock()
            #block=random.choice([O])
            blockPos=getSpawnPoint(0)
            block, blockPos = playerFieldRotate(0,gameDirection,block,blockPos)
            newBlock=False
            dirConfirmed=False
            materialized=False #flag, if set to false means block is not yet materialized meaning it doesn't
                               # interact with the game matrix (used for new block creation)
        #Check if any blocks have materialized! If so (meaning list returned from function isn't empty), toggle materialized
        if validMove(block,blockPos,gameMatrix,blockList,gameDirection)==False:
            gameOver=True
            drawGameOverScreen=True
            
        mattedBlocks=materializedBlocks(block,blockPos,gameDirection) #Store materialized blocks ins this var
        materialized=(materializedBlocks(block,blockPos,gameDirection)!=[]) #This looks at whether anything is stored in mattedBlocks, if so flag True
        #print(mattedBlocks) For test
        #print('begin')
        #Player input
        for event in pygame.event.get():
            if event.type == KEYDOWN:

                #If down is pressed, only trigger 
                if event.key == K_DOWN:
                    #If dirConfirmed = True, prepare to move block. Cannot move to gameDirection,
                    # so make an exception for that!
                    if (dirConfirmed == True) & (gameDirection!=2):
                        #Store new position of the blockposition first, check if valid, if so make new position
                        newPos=playerMove(blockPos,[0,1])
                        #Two checks (short-circuited) are performed: for a materialized block first (does interact
                        # with the gamefield) and a non-materialized block after (does not interact with gamefield)
                        if(materialized==True)&(validMove(block,newPos,gameMatrix,blockList,gameDirection)):
                            blockPos=newPos
                            if(gameDirection==0):
                                timer=0 #If a block moves, reset the tick timer so tick doesn't happen right after
                        elif(materialized==False)&(validMove(block,newPos,gameMatrix)):
                            blockPos=newPos
                            if(gameDirection==0):
                                timer=0
                        #If it's not a valid move and it needs to be stacked on ground/other blocks based on direction
                        elif gameDirection==0:
                            newBlock=True
                            blockList.append(pasteBlock(block,blockPos))
                            colorList.append(color)
                            playerScore+=100
                    #If the direction isn't confirmed, either rotate matrix or set direction
                    if dirConfirmed == False:
                        #If the gamedirection is the same as input, set direction (dirConfirmed=True)
                        if gameDirection==0:
                            if controlScheme!=1:
                                dirConfirmed=True
                                selectFieldSound.play() #Selefct field sound
                        #Else: change the gamedirection to chosen direction
                        else:
                            block, blockPos = playerFieldRotate(gameDirection,0,block,blockPos)
                            gameDirection=0
                            rotateFieldSound.play() #Rotate field sound

                #Same for other directions            
                if event.key == K_RIGHT:
                    if (dirConfirmed == True) & (gameDirection!=1):
                        newPos=playerMove(blockPos,[1,0])
                        if(materialized==True)&(validMove(block,newPos,gameMatrix,blockList,gameDirection)):
                            blockPos=newPos
                            if(gameDirection==3):
                                timer=0
                        elif(materialized==False)&(validMove(block,newPos,gameMatrix)):
                            blockPos=newPos
                            if(gameDirection==3):
                                timer=0
                        elif gameDirection==3:
                            newBlock=True
                            blockList.append(pasteBlock(block,blockPos))
                            colorList.append(color)
                            playerScore+=100
                    if dirConfirmed == False:
                        if gameDirection==3:
                            if controlScheme!=1:
                                dirConfirmed=True
                                selectFieldSound.play()
                        else:
                            block, blockPos = playerFieldRotate(gameDirection,3,block,blockPos)
                            gameDirection=3
                            rotateFieldSound.play() 
                        
                if event.key == K_LEFT:
                    if (dirConfirmed == True) & (gameDirection!=3):
                        newPos=playerMove(blockPos,[-1,0])
                        if(materialized==True)&(validMove(block,newPos,gameMatrix,blockList,gameDirection)):
                            blockPos=newPos
                            if(gameDirection==1):
                                timer=0
                        elif(materialized==False)&(validMove(block,newPos,gameMatrix)):
                            blockPos=newPos
                            if(gameDirection==1):
                                timer=0
                        elif gameDirection==1:
                            newBlock=True
                            blockList.append(pasteBlock(block,blockPos))
                            colorList.append(color)
                            playerScore+=100
                    if dirConfirmed == False:
                        if gameDirection==1:
                            if controlScheme!=1:
                                dirConfirmed=True
                                selectFieldSound.play()
                        else:
                            block, blockPos = playerFieldRotate(gameDirection,1,block,blockPos)
                            gameDirection=1
                            rotateFieldSound.play() 
                        
                if event.key == K_UP:
                    if (dirConfirmed == True) & (gameDirection!=0):
                        newPos=playerMove(blockPos,[0,-1])
                        if(materialized==True)&(validMove(block,newPos,gameMatrix,blockList,gameDirection)):
                            blockPos=newPos
                            if(gameDirection==2):
                                timer=0
                        elif(materialized==False)&(validMove(block,newPos,gameMatrix)):
                            blockPos=newPos                       
                            if(gameDirection==2):
                                timer=0
                        elif gameDirection==2:
                            newBlock=True
                            blockList.append(pasteBlock(block,blockPos))
                            colorList.append(color)
                            playerScore+=100
                    if dirConfirmed == False:
                        if gameDirection==2:
                            if controlScheme!=1:
                                dirConfirmed=True
                                selectFieldSound.play()
                        else:
                            block, blockPos = playerFieldRotate(gameDirection,2,block,blockPos)
                            gameDirection=2
                            rotateFieldSound.play() 
                
                if event.key == K_x:
                    #Rotate block once, store
                    newBlock=playerRotate(block)               
                    #Perform check: is the new rotation valid on the gamefield? If so replace current
                    # block with it, if not do nothing
                    if(validMove(newBlock,blockPos,gameMatrix,blockList,gameDirection)):
                        block=newBlock
                        rotateBlockSound.play() 
                if event.key == K_z:
                    if dirConfirmed==False and controlScheme !=0:
                        dirConfirmed=True #1 x om direction vast te zetten handmatig
                        #blockList=rotateMatrix(blockList)
                        selectFieldSound.play()
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                if event.key == K_m:
                    if playerSelector['music']==1:
                        playerSelector['music']=2
                        pygame.mixer.music.set_volume(0.0)
                    elif playerSelector['music']==2:
                        playerSelector['music']=1
                        pygame.mixer.music.set_volume(0.2)

        if timer==0:
            print('trigger')
            playerScore+=10
        timer+=1
        if timer==GAMESPEED:
            #Calculate position if the block ticks 1
            newPos=blockTick(block,blockPos,gameDirection)
            #Check whether this new position is valid. If not, it must be stacked onto gamefield
            # given that tick always stacks if movement if impossible.
            if(materialized==True)&(validMove(block,newPos,gameMatrix,blockList,gameDirection)):
                blockPos=newPos            
            elif(materialized==False)&(validMove(block,newPos,gameMatrix)):
                #Block translucent, however check to see if the new move makes it materialized/
                #If there's any materialized blocks in the next step...
                if(materializedBlocks(block,newPos,gameDirection)!=[]):
                    #If there's any blocks already inhabiting position the block wants to go to...
                    if(validMove(block,newPos,gameMatrix,blockList,gameDirection)==False):
                        #Try two times in either direction if a position left/up or right/down is viable, if not, game ends
                        if gameDirection==0 or gameDirection==2:
                            try1=[validMove(block,[newPos[0]+1,newPos[1]],gameMatrix,blockList,gameDirection),[newPos[0]+1,newPos[1]]]
                            try2=[validMove(block,[newPos[0]-1,newPos[1]],gameMatrix,blockList,gameDirection),[newPos[0]-1,newPos[1]]]
                            try3=[validMove(block,[newPos[0]+2,newPos[1]],gameMatrix,blockList,gameDirection),[newPos[0]+2,newPos[1]]]
                            try4=[validMove(block,[newPos[0]-2,newPos[1]],gameMatrix,blockList,gameDirection),[newPos[0]-2,newPos[1]]]
                        if gameDirection==1 or gameDirection==3:
                            try1=[validMove(block,[newPos[0],newPos[1]+1],gameMatrix,blockList,gameDirection),[newPos[0],newPos[1]+1]]
                            try2=[validMove(block,[newPos[0],newPos[1]-1],gameMatrix,blockList,gameDirection),[newPos[0],newPos[1]-1]]
                            try3=[validMove(block,[newPos[0],newPos[1]+2],gameMatrix,blockList,gameDirection),[newPos[0],newPos[1]+2]]
                            try4=[validMove(block,[newPos[0],newPos[1]-2],gameMatrix,blockList,gameDirection),[newPos[0],newPos[1]-2]]
                        tryloop=[try1,try2,try3,try4]
                        print(tryloop)
                        killCount=0
                        done=False
                        for t in range(4):
                            if tryloop[t][0]==True and done==False:
                                blockPos=tryloop[t][1]
                                done=True
                                print('success')
                            else:
                                killCount+=1
                        if killCount==4:
                            print('Game over')
                            sys.exit()                       
                    else:
                        blockPos=newPos
                else:
                    blockPos=newPos
                
            else:
                newBlock=True
                blockList.append(pasteBlock(block,blockPos))
                colorList.append(color)
            timer=0
            print('DROP')
            #pygame.time.wait(2000) voor test

        #Then look if any of these materialized blocks inhabit same space as already set blocks. Happens ONLY if new
        # blocks don't have anywhere else to go.

        #Check to see if any rows are cleared. if so update blocklist, if not blocklist remains the same
        blockList=clearRow(blockList,quatList)
            
        #Drawing graphics of the game. First, always perform a check to see if any value has changed.
        # If not, don't need to redraw the game area. Perform this check every frame. 1st time it will always
        # draw since oldBlock and oldBlockPos don't have stored values
        if oldBlock!=block or oldBlockPos!=blockPos:
            oldBlock=block
            oldBlockPos=blockPos
            #drawBlock(RED,blockPos[0],blockPos[1]) #for testing drawing
            #pygame.draw.rect(window, (0, 100, 255), (50, 50, 162, 100), 3) #test voor alleen outline drawen
            #print(mattedBlocks) for Test
            #print('later')
            
            mattedBlocks=materializedBlocks(block,blockPos,gameDirection) 
            drawGame(block,color,blockPos,blockList,colorList,mattedBlocks,gameDirection)

        #UI:Draw the next block window
        drawUINextBlock(nextBlock)
        #UI:Draw score
        drawUIScore(playerScore)
        #drawUINextBlock(nextBlock)

        
        #pygame.draw.rect(window, RED, (0,0,32,32))
        
        #Refresh graphics. ZET ZODAT niet elke frame doet maar alleen als nodig
        pygame.display.update()
            
        #printGame(gamematrix,blockPos,block,blockList,colorList)
        

    if gameState=='game' and gameOver==True:
        if drawGameOverScreen==True:
            pygame.mixer.music.set_volume(0.0)
            gameOverSound.play()
            drawGameOver(playerScore,playerSelector)
            drawGameOverScreen=False
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_RETURN or event.key == K_SPACE or event.key == K_x:
                    playerCursor={'active':0,'menu':0,'position':0}
                    writeGameSettings=False #If set to true, write game settings to game globals upon starting game
                    playerMenu=True #While true, playermenu loop runs
                    tutorialActive=False    # Toggle if tutorial is currently viewed on screen
                    gameState='start_menu'
                    
                    pygame.mixer.music.load('tetrisaThemeB.mp3')
                    pygame.mixer.music.play(-1, 0)
                    if playerSelector['music']==1:
                        pygame.mixer.music.set_volume(0.2)
                        
                        
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
        

    #Regardless of game over or not, in game always advance clock every frame
    mainClock.tick(FPS)



