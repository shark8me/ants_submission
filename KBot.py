#!/usr/bin/env python
from ants import *
from scipy.spatial.distance import euclidean,cosine 
import numpy as np

class KBot:
    def __init__(self):
        # define class level variables, will be remembered between turns
        self.directions = ['n','e','s','w']

    # do_setup is run once at the start of the game
    # after the bot has received the game settings
    # the ants class is created and setup by the Ants.run method
    def do_setup(self, ants):
        #array with x,y, and 2 dimensions
        self.grid=np.ones((ants.rows,ants.cols,2))
        self.grid[:,:,0]=0.25
#        hill=ants.my_hills()
#        print "hill ",hill
#set the hill as -1 so ants dont go there
#        self.grid[hill[0],hill[1],1]=-1        
        self.ants=ants
        self.teamloc={}
        self.f=open('/tmp/probmat','w+')
        self.turnnum=1

    def no_friendly_ants(self,ndest):
        return ndest not in self.teamloc
 
    def getp(self,x,y):
        #return probability (stored at 0 index, if 1 index is not==-1
        #return self.grid[x-1,y-1,0] if self.grid[x-1,y-1,1]!=-1 else 0.001 
        try:
            if self.ants.passable((x,y)) and self.ants.unoccupied((x,y)) and self.no_friendly_ants((x,y)):
                p=self.grid[x,y,0] 
            else:
                p=0
        except (IndexError):
            p=0.001
        return p

    def setp(self,x,y,val):
        try:
            self.grid[x,y,0]=val 
        except (IndexError):
            pass
         
    def getneighbours(self,ant_loc):
        x,y=ant_loc
        #   N                   E                S                   W
        k=[self.getp(x-1,y),self.getp(x,y+1),self.getp(x+1,y),self.getp(x,y-1)] 
        pstr=' '.join([str(i) for i in k])
        self.f.write('unnormed xy loc %i %i probmat %s \n' % (x,y,pstr))
        self.f.flush()
        return k

    def makemove(self,ant_loc):
        x,y=ant_loc
        k=self.getneighbours(ant_loc)
        if sum(k)==0:
            return
        probmat=[i/sum(k) for i in k]
        pstr=' '.join([str(i) for i in probmat])
        self.f.write('xy loc %i %i probmat %s \n' % (x,y,pstr))
        self.f.flush()
        #ndir=np.random.choice(self.directions,1,replace=False,p=probmat)
        nd=sorted(zip(self.directions,probmat),key=lambda x:x[1],reverse=True)
        ndir=[i for i,j in nd]

        self.ants.issue_order((ant_loc,ndir[0]))
        newdest=self.ants.destination(ant_loc,ndir[0])
        self.teamloc[newdest]=1
        self.setp(x,y,0.01)
        '''
        for i in ndir:
            newdest=self.ants.destination(ant_loc,i)
            if self.ants.passable(newdest):
                if self.no_friendly_ants(newdest) and self.ants.unoccupied(newdest):
                    self.ants.issue_order((ant_loc,i))
                    self.teamloc[newdest]=1
                    self.setp(x,y,0.01)
                    break
                else:
                    continue
            else:
                self.grid[x,y,1]=-1
                '''
            
    def nbrlist(self,x,y):
        return [(x-1,y),(x,y+1),(x+1,y),(x,y-1)] 

    def secnbrlist(self,x,y):
        return [(x,y+2),(x,y-2),
                (x+2,y),(x-2,y),
                (x-1,y-1),(x-1,y+1),
                (x+1,y-1),(x+1,y+1)] 
        
    def do_turn(self, ants):
        #initialize empty friendly location 
        self.teamloc={}
        self.f.write('start of turn %i \n' % (self.turnnum))
        self.turnnum+=1

        #increment locations previously visited
        kfn=np.vectorize(lambda x:x+0.01)
        self.grid[:,:,0]=kfn(self.grid[:,:,0])

        #increment locations having food
        #and their immediate neighbours too
#        [self.setp(x3,y3,0.9) for x,y in ants.food() for x1,y1 in self.nbrlist(x,y) for x2,y2 in self.nbrlist(x1,y1) for x3,y3 in self.nbrlist(x2,y2)]

        for x,y in ants.food():
            self.setp(x,y,0.9) 
            for x,y in self.nbrlist(x,y):
                self.setp(x,y,0.8) 
            for x,y in self.secnbrlist(x,y):
                self.setp(x,y,0.7) 
        
        #[self.setp(x1,y1,0.001) for (x,y),z in ants.enemy_ants() for x1,y1 in self.nbrlist(x,y)]
        for (x,y),z in ants.enemy_ants():
             for x1,y1 in self.nbrlist(x,y):
                 self.setp(x1,y1,0.001) 
             self.setp(x,y,0.001) 

        for ant_loc in ants.my_ants():
            self.makemove(ant_loc)
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
        Ants.run(KBot())
    except KeyboardInterrupt:
        print('ctrl-c, leaving ...')
