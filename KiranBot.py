#!/usr/bin/env python
from ants import *
from scipy.spatial.distance import euclidean,cosine 
import numpy as np
# define a class with a do_turn method
# the Ants.run method will parse and update bot input
# it will also run the do_turn method for us
class KiranBot:
    def __init__(self):
        # define class level variables, will be remembered between turns
        self.hill_loc=-1
        self.fdir={}
        self.rdir={}
        for i,j in zip(['n','e','w','s'],range(4)):
            self.fdir[i]=j
            self.rdir[j]=i
        sys.stdout.write(' init ') 

    # do_setup is run once at the start of the game
    # after the bot has received the game settings
    # the ants class is created and setup by the Ants.run method
    def do_setup(self, ants):
        #f = open('/tmp/comp.txt', 'w+')
        #self.hill_loc=my_hills[0]
        sys.stdout.write(' do_setup ') 
   
    def caldist(x,y):
        return euclidean(np.array(self.hill_loc),np.array([x,y]))
       
    def caldir(p1,p2):
        ''' point, home loc'''
        ##f = open('/tmp/comp.txt', 'w+')
        #f.write("abcd")
        #f.flush()
        x1,y1=p1
        x2,y2=p2
        ydf,xdf=y2-y1,x2-x1
        if xdf== 0 and ydf ==0:
            return (x1,y1)
        #print "p1 ",p1," p2 ",p2," xdf ", xdf," ydf ",ydf
        if math.fabs(ydf) > math.fabs(xdf):        
            if y2>y1:
                #return (x1,y1+1),'e'
                return 'e'
            else:
                #return (x1,y1-1),'w'
                return 'w'
        else:
            if x2>x1:
                #return (x1+1,y1),'s'
                return 's'
            else:
                #return (x1-1,y1),'n'
                return 'n'

    def smallmove(ant_loc,direction,new_loc):
        if (ants.passable(new_loc)):
            # an order is the location of a current ant and a direction
            ants.issue_order((ant_loc, direction))
            return True
        else:
            return False

    def calcpos(oldir):
        nd=0 if self.fdir[oldir]+1 > 3 else self.fdir[oldir]+1
        return self.rdir[nd]

    def makemove(ant_loc,direction,new_loc):
        valmove=smallmove(ant_loc,direction,new_loc)
        for i in range(3):
            if valmove==False:
                ndirection=calcpos(direction)
                valmove=smallmove(ant_loc,ndirection,new_loc)
            else:
                break

    # do turn is run once per turn
    # the ants class has the game state and is updated by the Ants.run method
    # it also has several helper methods to use
    def do_turn(self, ants):
        # loop through all my ants and try to give them orders
        # the ant_loc is an ant location tuple in (row, col) form
        #find distance to hill
        dists=[(caldist(x,y),x,y) for x,y in ants.food()]
        num_ants=len(ants.my_ants())
        nfood=heapq.nsmallest(num_ants,dists,key=lambda x:x[0]) 

        for ant_loc,food_loc in zip(ants.my_ants(),nfood):
            x,y=ant_loc
            direction=caldir(ant_loc,food_loc)
                  
            new_loc = ants.destination(ant_loc, direction)
            makemove(ant_loc,direction,new_loc)
                 
            # check if we still have time left to calculate more orders
            if ants.time_remaining() < 10:
                break
            
if __name__ == '__main__':
    # psyco will speed up python a little, but is not needed
    try:
        import psyco
        psyco.full()
    except ImportError:
        pass
    
    try:
        # if run is passed a class with a do_turn method, it will do the work
        # this is not needed, in which case you will need to write your own
        # parsing function and your own game state class
        Ants.run(KiranBot())
    except KeyboardInterrupt:
        print('ctrl-c, leaving ...')
