# coding: utf-8
__author__ = "rinakinoshita"


import rhinoscriptsyntax as rs
import ghpythonlib.components as gh
import Rhino as rc
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path

### input
lines = lines
y = y
#x = x
flip = flip

maxLen = 1000 # warning # change
nozzleDiameter = 0.4

### output
#Catenary = DataTree[object]()
cat =[]
debugger =[]

## Catenary direction
if flip == True:
    gravity = rs.coerce3dvector([0,0,-1]) * -1
else:
    gravity = rs.coerce3dvector([0,0,-1]) * 1



#################
##### CLASS #####
#################

# A class for keeping track of each Catenaries
class Catenary:

    def __init__(self, aPt, bPt, len, dir):
        self.aPt = aPt
        self.bPt = bPt
        self.len = len
        self.dir = dir

        self.rerun()

    def rerun(self):
        self.cat = self.draw()
        self.extrdSrf = self.extrd()
    
    def draw(self):
        cat = gh.Catenary(self.aPt, self.bPt, self.len, self.dir)

        ## check cat wrong gravity direction and correct
        ## compare line and cat
        line = rs.AddLine(self.aPt, self.bPt)
        lineMidPntZ = rs.CurveMidPoint(line)[2]
        catMidPntZ = rs.CurveMidPoint(cat)[2]
        if flip is True:
            if catMidPntZ < lineMidPntZ:
                cat = gh.Catenary(self.aPt, self.bPt, self.len, self.dir*-1)
        else:
            if catMidPntZ > lineMidPntZ:
                cat = gh.Catenary(self.aPt, self.bPt, self.len, self.dir*-1)
        
        ## flip Curve Direction
        if not rs.CurveDirectionsMatch(cat, rs.AddLine(self.aPt, self.bPt)):
            cat.Reverse()
        
        ## unitize curve domain to 0-1
        cat.Domain = rc.Geometry.Interval(0,1)
        
        return cat

    def extrd(self):
        print("Catenary.extrd")
        ## save extruded surface as an obstacle
        path = rs.AddLine([0,0,0],gravity*maxLen)
        return rs.ExtrudeCurve(self.cat, path)
        

# a class for keeping track of each chain (small catenaries chained together)
# methods for generating tangled chains as Catenary class objects
class Chain:

    def __init__(self, aPt, bPt, len, dir):
        self.aPt = aPt
        self.bPt = bPt
        self.len = len
        self.dir = dir
        
        self.catBeforeTangle = Catenary(self.aPt, self.bPt, self.len, self.dir)
        self.tangledCat_list = []


    def tangle(self, prevChain_list):
        print("Chain.tangle")
        
        ## make a list of tangling points
        def tanglingPnts():
            ## append first and last point/params
            tanglingPnt_list = []
            tanglingPnt_list.append(self.aPt)
            tanglingPnt_list.append(self.bPt)

            collisionPntParam_list = []
            collisionPntParam_list.append(0)
            collisionPntParam_list.append(1)

            ## check collision if there are previous Chains
            if prevChain_list != []:
                for prevChain in prevChain_list:
                    for prevCat in prevChain.tangledCat_list:
                        # find if this chain collides with obstacles ( areas below previous chains )

                        collisionCheck = rs.CurveSurfaceIntersection(self.catBeforeTangle.cat, prevCat.extrdSrf)
                        
                        if collisionCheck:
                            if collisionCheck[0][0] == 1:
                                # find and append tangling point
                                                                                                                                
                                ## pnt and param where chain collides with obstacles 
                                collisionPnt = collisionCheck[0][1]
                                collisionPntParm = collisionCheck[0][5]
                                
                                ## find tangling points
                                movePnt = rs.CopyObject(collisionPnt, gravity * -1 * maxLen)
                                projectLine = rs.AddLine(collisionPnt, movePnt)                           
                                tangling = rs.CurveCurveIntersection(projectLine, prevCat.cat)                            
                                tanglingPnt = tangling[0][1]

                                ## move tangling points up
                                ## to express the thickness of the chain
                                rs.MoveObject(tanglingPnt, gravity * -1 * nozzleDiameter)

                                ## append tangling points and param that represents the orderr of points
                                tanglingPnt_list.append(tanglingPnt)
                                collisionPntParam_list.append(collisionPntParm)                   
                                
            ## reorder pnts
            tanglingPnt_listSorter = zip(collisionPntParam_list, tanglingPnt_list)
            tanglingPnt_listSorter.sort()
            collisionPntParam_list, tanglingPnt_list = zip(* tanglingPnt_listSorter)

            ## Cull duplicate pnts
            tanglingPnt_list = rs.CullDuplicatePoints(tanglingPnt_list)

            return tanglingPnt_list
        

        # make a list of tangled catenaries
        def tanglingChains( tanglingPnt_list ):
            for i in range( len(tanglingPnt_list) -1):
                aPt = tanglingPnt_list[i]
                bPt = tanglingPnt_list[i+1]
                dist = rs.Distance(aPt, bPt)
                catLen = dist ## change

                cat = Catenary(aPt, bPt, catLen, self.dir)

                self.tangledCat_list.append(cat)

            ### get divided length
            for i in range( len(self.tangledCat_list) ):
                cat = self.tangledCat_list[i]
                if rs.Distance(cat.aPt, cat.bPt) < nozzleDiameter*2:
                    cat.len *= 1
                else:
                    cat.len *= 1.1
                    cat.rerun()

            return self.tangledCat_list
            
        
        return tanglingChains( tanglingPnts() )

#####################
##### CLASS END #####
#####################


# tangledChain_list -> a list of tangled Chain class instances
tangledChain_list = []

for lineN, line in enumerate( lines ):
    line = rs.coercecurve( line )
    chain = Chain( rs.CurveStartPoint(line),rs.CurveEndPoint(line),y[lineN],gravity )
    chain.tangle( tangledChain_list )
    tangledChain_list.append( chain )


print("result")

catenary =[]
print(tangledChain_list)
for tangledChain in tangledChain_list:
    for tangledCat in tangledChain.tangledCat_list:
        catenary.append(tangledCat.cat)