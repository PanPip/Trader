import numpy as np
import sys
import random
import pygame
#import flappy_bird_utils
import pygame.surfarray as surfarray
import os, os.path # To count images in directory Too complicatd?
from pygame.locals import *


#Trading on second graph
FPS = 30 # Or, may be faster?
SCREENWIDTH  = 600
SCREENHEIGHT = 1000

pygame.init()
FPSCLOCK = pygame.time.Clock()
SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
pygame.display.set_caption('Trader')


#This is a lite version of a program. Only one open order is allowed at a time, fixed size.
class GameState:
    def __init__(self):
	self.money = 1000 # actual money
	self.money_i = 0 # how much order is worth (for kicking a trader)
	self.multiplyer = 1000 # 1:100 (Not used in lite version)
	self.orderprice = 0.1 #fixed price for order
	self.order = 0 # -1 :currently sell order 0 : currently no orders 1: currently buy order
	self.order_price = 0 #price at which order was opened
	self.spread = 0.0001 #obviously, spread value
        self.score =  0 #Not shure if needed yet
	self.kick_price = 900 # At this balance your game ends
	self.frame = 0 #Not shure if needed
	path, dirs, files = os.walk("/home/illya/Trader/src/images/specgrams").next()
	self.max_frames = len(files)
	with open("/home/illya/Trader/src/newvector.txt") as f:
    	    self.prices = map(float, f)

    def frame_step(self, input_actions):
        pygame.event.pump()

        reward = 0
        terminal = False

        if sum(input_actions) != 1:
            raise ValueError('Multiple input actions!')

        # input_actions[0] == 1: sell
        # input_actions[1] == 1: do nothing
	# input_actions[2] == 1: buy
        if input_actions[0] == 1:
            if self.order == 0:
		self.money -= self.orderprice 
		self.order = -1
		self.order_price = self.prices[self.frame]
		reward = 0 #On opening an order you get nothing
	    if self.order == 1:
		buf = self.order_price * ( self.prices[self.frame] - self.orderprice - self.spread) # Income/ Loss
		self.money += buf  
		self.order = 0
		self.order_price = 0
		if buf > 0:
			reward = 1 # Got money
		if buf < 0:
			reward = -1# Lost money
	    #No other cases - Can't have two sell orders

        if input_actions[1] == 1:
            if self.order == 0:
		self.money -= self.orderprice 
		self.order = 1
		self.order_price = self.prices[self.frame]
		reward = 0 #On opening an order you get nothing
	    if self.order == -1:
		buf = self.order_price * ( self.orderprice - self.prices[self.frame] - self.spread) # Income/ Loss
		self.money += buf  
		# self.money_i not here
		self.order = 0
		self.order_price = 0
		if buf > 0:
			reward = 1 # Got money
		if buf < 0:
			reward = -1# Lost money
	    #No other cases - Can't have two sell orders


        # check if game ended  - out of money ! or pictures ended
	buf = 0 # In case no order is held
	if self.order == 1:
	    buf = self.order_price * ( self.prices[self.frame] - self.orderprice - self.spread)
	if self.order == -1:
	    buf = self.order_price * ( self.orderprice - self.prices[self.frame] - self.spread)

	#Need an exception when have not enough values!!!(self.prices)
	#Leaving game if no money or no more frames
        isCrash= (((self.money - buf) < self.kick_price) or (self.frame + 2 > self.max_frames))

        if isCrash:
            terminal = True
            self.__init__()
            reward = -1 

        # draw images
	IMAGE_PATH = '/home/illya/Trader/src/images/specgrams/img' + str(1024 + self.frame) + '.png'
	current_screen = pygame.image.load(IMAGE_PATH).convert()
        SCREEN.blit(current_screen, (0,0)) # draws one image over another

        showScore(self)

        image_data = pygame.surfarray.array3d(pygame.display.get_surface())
	#Updating
        pygame.display.update()
        #print ("FPS" , FPSCLOCK.get_fps())
	FPSCLOCK.tick(FPS)
	self.frame += 1
        return image_data, reward, terminal


#Need to be calibrated - so doesn't overlay needed information
def showScore(self):

    myfont = pygame.font.SysFont("monospace", 15)
    if self.order == -1:
	buf = 'Sell'
    if self.order == 0:
	buf = 'None'
    if self.order == 1:
	buf = 'Buy'
	
    score = 'Frame: ' +str(self.frame)+  ' Money: ' + str(self.money) + ' Current order: ' + buf
    label = myfont.render(score, 1, (0,0,0))
    SCREEN.blit(label, (10, 10))




