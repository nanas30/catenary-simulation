# coding: utf-8
__author__ = "rinakinoshita"


import rhinoscriptsyntax as rs
import ghpythonlib.components as gh
import Rhino as rc
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path

import scriptcontext


### input
lines = lines
y = y
#x = x
flip = flip

maxLen = 1000 # warning # change
nozzleDiameter = 0.4

### output
catenaryTree = DataTree[object]()
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

    def __init__(self, aPt, bPt, mult, dir):
        self.aPt = aPt
        self.bPt = bPt
        self.mult = mult
        self.dir = dir

        self.len = 0
        self.color= [0,0,0]
        self.rerun()

    def rerun(self):
        self.dist = self.distance()
        self.cat = self.draw()
        self.extrdSrf = self.extrd()
    
    def distance(self):
        return rs.Distance(self.aPt, self.bPt)

    def draw(self):
        self.len = self.dist * self.mult

        #print(self.aPt, self.bPt, self.len, self.dir)
        #print(self.mult)
        if self.len <= self.dist:
            print("")
            #print("warning: catenary length is shorter than AB distance")
        cat = gh.Catenary(self.aPt, self.bPt, self.len, self.dir)

        ## check cat wrong gravity direction and correct
        ## compare line and cat
        line = rs.AddLine(self.aPt, self.bPt)
        lineMidPntZ = rs.CurveMidPoint(line)[2]
        catMidPntZ = rs.CurveMidPoint(cat)[2]
        if flip is True:
            if catMidPntZ < lineMidPntZ:
                cat = gh.Catenary(self.aPt, self.bPt, self.len, self.dir*-1)
                catMidPntZ = rs.CurveMidPoint(cat)[2]
                if catMidPntZ < lineMidPntZ:
                    cat = gh.Catenary(self.aPt, self.bPt, self.dist, self.dir)
        else:
            if catMidPntZ > lineMidPntZ:
                cat = gh.Catenary(self.aPt, self.bPt, self.len, self.dir*-1)
                catMidPntZ = rs.CurveMidPoint(cat)[2]
                if catMidPntZ > lineMidPntZ:
                    cat = gh.Catenary(self.aPt, self.bPt, self.dist, self.dir)
        
        ## flip Curve Direction
        if not rs.CurveDirectionsMatch(cat, rs.AddLine(self.aPt, self.bPt)):
            cat.Reverse()
        
        ## unitize curve domain to 0-1
        cat.Domain = rc.Geometry.Interval(0,1)
        
        return cat

    def extrd(self):
        ## save extruded surface as an obstacle
        path = rs.AddLine([0,0,0],gravity*maxLen)
        return rs.ExtrudeCurve(self.cat, path)
        

# a class for keeping track of each chain (small catenaries chained together)
# methods for generating tangled chains as Catenary class objects
class Chain:

    def __init__(self, aPt, bPt, mult, dir):
        self.aPt = aPt
        self.bPt = bPt
        self.mult = mult
        self.dir = dir
        
        self.catBeforeTangle = Catenary(self.aPt, self.bPt, self.mult, self.dir)
        self.tangledCat_list = []


    def tangle(self, prevChain_list, lineNforDebug):
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
                for i, prevChain in enumerate(prevChain_list):
                    for j, prevCat in enumerate(prevChain.tangledCat_list):
                        # find if this chain collides with obstacles ( areas below previous chains )

                        print(i,j)

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
                                
            ## sort pnts order
            tanglingPnt_listSorter = zip(collisionPntParam_list, tanglingPnt_list)
            tanglingPnt_listSorter.sort()
            collisionPntParam_list, tanglingPnt_list = zip(* tanglingPnt_listSorter)

            ## Cull duplicate pnts refer XYZ
            tanglingPnt_list = rs.CullDuplicatePoints(tanglingPnt_list)
            
            ## Cull duplicate pnts refer XY 
            tanglingPntXY_list =  rs.CopyObjects( tanglingPnt_list )
            for n in range(len(tanglingPntXY_list)):
                tanglingPntXY_list[n] = rs.coerce3dpoint( tanglingPntXY_list[n] )

            for tanglingPntXY in tanglingPntXY_list:
                tanglingPntXY[2] = 0

            for thisn, tanglingPntXY in enumerate( tanglingPntXY_list ):
                for n in range(thisn):
                    if rs.PointCompare(tanglingPntXY_list[thisn], tanglingPntXY_list[n]):
                        ## TODO: does not deal with flip
                        if tanglingPnt_list[thisn][2] > tanglingPnt_list[n][2]:
                            tanglingPnt_list[n] = []
                        else:
                            tanglingPnt_list[thisn] = []

            tanglingPnt_list = filter(None, tanglingPnt_list)

            return tanglingPnt_list
        

        # make a list of tangled catenaries
        def tanglingChains( tanglingPnt_list ):
            for i in range( len(tanglingPnt_list) -1):
                aPt = tanglingPnt_list[i]
                bPt = tanglingPnt_list[i+1]
                mult = self.mult ## change

                cat = Catenary(aPt, bPt, mult, self.dir)

                self.tangledCat_list.append(cat)

            totalDist = 0
            for i in range( len(self.tangledCat_list) ):
                cat = self.tangledCat_list[i]
                totalDist += cat.dist


            ### get divided length
            for i in range( len(self.tangledCat_list) ):
                cat = self.tangledCat_list[i]
                if cat.dist < nozzleDiameter*2:
                    cat.mult = 1
                    cat.rerun()
                else:
                    cat.mult *= self.catBeforeTangle.dist / totalDist
                    cat.rerun()

            #return self.tangledCat_list

        tanglingPnt_list = tanglingPnts()
        
        ## !!!!
        if lineNforDebug < len(lines)-1:
            tanglingChains( tanglingPnt_list )
        else:
            for item in tanglingPnt_list:
                debugger.append(item)

        return self.tangledCat_list

#####################
##### CLASS END #####
#####################


# tangledChain_list -> a list of tangled Chain class instances
tangledChain_list = []

for lineN, line in enumerate( lines ):
    line = rs.coercecurve( line )
    chain = Chain( rs.CurveStartPoint(line),rs.CurveEndPoint(line),y[lineN],gravity )
    chain.tangle( tangledChain_list , lineN)

    ## !!!!
    if lineN < len(lines)-1:
        
        tangledChain_list.append( chain )
        print(lineN)


print("result")

catenary = []
check = []
for i,tangledChain in enumerate(tangledChain_list):
    chain =[]
    
    for j, tangledCat in enumerate(tangledChain.tangledCat_list):
        chain.append(tangledCat.cat)
        catenaryTree.Add(tangledCat.cat, GH_Path(i))

        check.append(tangledCat.extrdSrf)

    
    if len(chain)>1:
        catenary.append(rs.JoinCurves(chain)[0])
    else:
        catenary.append(tangledCat.cat)