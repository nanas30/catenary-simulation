# coding: utf-8
__author__ = "rinakinoshita"



import rhinoscriptsyntax as rs
import ghpythonlib.components as gh

from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path

## input
lines = lines
y = y
x = x
flip = flip

##output
Catenary = DataTree[object]()
exCatenary = DataTree[object]()

"""
points = []
result = []
intpnts = []
toppnts = []
c =[]

prev_pntN_first=None
"""

# Catenary direction
if flip == True:
    gravity = rs.coerce3dvector([0,0,-1]) * -1
else:
    gravity = rs.coerce3dvector([0,0,-1]) * 1


class Test:
    def __init__(self):
        print("hi")

test = Test()

#################
##### CLASS #####
#################

class Catenary:

    def __init__(self, aPt, bPt, len, dir):
        self.aPt = aPt
        self.bPt = bPt
        self.len = len
        self.dir = dir

        self.cat = self.draw()
        self.extrdSrf = self.extrd()
    
    def draw(self):
        print("Catenary.draw")
        return gh.Catenary(self.aPt, self.bPt, self.len, self.dir)

    def extrd(self):
        print("Catenary.extrd")
        # save extruded surface as an obstacle
        extrdLen = 1000 # warning # change
        path = rs.AddLine([0,0,0],gravity*extrdLen)
        return rs.ExtrudeCurve(self.cat, path)
        


class Chain:

    def __init__(self, aPt, bPt, len, dir):
        self.aPt = aPt
        self.bPt = bPt
        self.len = len
        self.dir = dir
        
        # Catenary class instance
        # before tangle
        self.initCat = Catenary(self.aPt, self.bPt, self.len, self.dir)

        # a list of Catenary class instances
        # after tangle
        self.catenaries = []


    def tangle(self, prevChainCat_list):
        print("Chain.tangle")

        #if first Chain, no obstacle
        if prevChainCat_list == []:
            
            print("first chain")

            # append first Chain as Catenary class
            self.catenaries.append(self.initCat)
            return self.catenaries

        else:

            for prevChainCats in prevChainCat_list:
                for prevCat in prevChainCats:

                    print(prevCat)
                    # check if this chain collides with obstacles ( previous chains )
                    collision = rs.CurveSurfaceIntersection(self.initCat.cat, prevCat.extrdSrf)
                    print("collision")
                    
                    if collision is None:
                        print("collision False")

                        # append undivided Chain as Catenary class
                        self.catenaries.append(self.initCat)

                    else:
                        print("collision True")
                        print(collision[0][1])

                        # append undivided Chain as Catenary class                                                                        
                        """ EDIT """
                        self.catenaries.append(self.initCat)
                        
                        #get colliding points
                        #move colliding points up
                        #get divided length
                        

#####################
##### CLASS END #####
#####################


# tangledChainCat_list -> a list of tangled Catenary class instances

# chain -> Chain class instance

tangledChainCat_list = []


for lineN, line in enumerate( lines ):
    line = rs.coercecurve( line )
    chain = Chain( rs.CurveStartPoint(line),rs.CurveEndPoint(line),y[lineN],gravity )
    chain.tangle( tangledChainCat_list )
    tangledChainCat_list.append( chain.catenaries )


print("result")

catenary =[]
for tangledChainCat in tangledChainCat_list:
    for cat in tangledChainCat:
        catenary.append(cat.cat)