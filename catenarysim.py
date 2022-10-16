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
nozzleDiameter = 5

### output
#Catenary = DataTree[object]()
catenary =[]
debugger =[]

## Catenary direction
if flip == True:
    gravity = rs.coerce3dvector([0,0,-1]) * -1
else:
    gravity = rs.coerce3dvector([0,0,-1]) * 1



#################
##### CLASS #####
#################

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
        print("Catenary.draw")
        cat = gh.Catenary(self.aPt, self.bPt, self.len, self.dir)

        ## check catenary wrong gravity and 
        ## compare line and cat
        line = rs.AddLine(self.aPt, self.bPt)
        lineMidPntZ = rs.CurveMidPoint(line)[2]
        catMidPntZ = rs.CurveMidPoint(cat)[2]
        if catMidPntZ > lineMidPntZ:
            cat = gh.Catenary(self.aPt, self.bPt, self.len, self.dir*-1)

        
        ## flip Curve Direction
        if not rs.CurveDirectionsMatch(cat, rs.AddLine(self.aPt, self.bPt)):
            print("reverse")
            cat.Reverse()
        
        ## unitize curve domain
        cat.Domain = rc.Geometry.Interval(0,1)
        
        return cat

    def extrd(self):
        print("Catenary.extrd")
        ## save extruded surface as an obstacle
        path = rs.AddLine([0,0,0],gravity*maxLen)
        return rs.ExtrudeCurve(self.cat, path)
        


class Chain:

    def __init__(self, aPt, bPt, len, dir):
        self.aPt = aPt
        self.bPt = bPt
        self.len = len
        self.dir = dir
        
        ## Catenary class instance
        ## before tangle
        self.initCat = Catenary(self.aPt, self.bPt, self.len, self.dir)

        ## a list of Catenary class instances
        ## after tangle
        self.catenaries = []


    def tangle(self, prevChainCat_list):
        print("Chain.tangle")

        ## if first Chain, no obstacle
        if prevChainCat_list == []:
            
            print("first chain")

            ## append first Chain as Catenary class
            self.catenaries.append(self.initCat)
            return self.catenaries

        ## after first Chain, check collision
        else:
            bendingPnt_list = []
            bendingPnt_list.append(self.aPt)
            bendingPnt_list.append(self.bPt)

            collisionPntParam_list = []
            collisionPntParam_list.append(0)
            collisionPntParam_list.append(1)

            for prevChainCats in prevChainCat_list:
                for prevCat in prevChainCats:

                    print(prevCat)
                    ## check if this chain collides with obstacles ( previous chains )
                    print(self.initCat.cat, prevCat.extrdSrf)
                    if not prevCat.extrdSrf:
                        break
                    collisionCheck = rs.CurveSurfaceIntersection(self.initCat.cat, prevCat.extrdSrf)
                    print("collisionCheck")
                    
                    if collisionCheck:
                        if collisionCheck[0][0] == 1:
                            print("collisionCheck True")
                            #print(collisionCheck[0][1])

                            ## append undivided Chain as Catenary class                                                                        
                            """ EDIT """
                            #self.catenaries.append(self.initCat)
                            ## pnt and param where chain collides with obstacles 
                            collisionPnt = collisionCheck[0][1]
                            collisionPntParm = collisionCheck[0][5]

                            movePnt = rs.CopyObject(collisionPnt, gravity * -1 * maxLen)
                            projectLine = rs.AddLine(collisionPnt, movePnt)

                            ## get colliding points
                            projectLine = rs.coercecurve(projectLine)                            
                            bending = rs.CurveCurveIntersection(projectLine, prevCat.cat)                            
                            bendingPnt = bending[0][1]

                            print("bendingPnt")
                            print(bendingPnt)

                            ## move colliding points up
                            rs.MoveObject(bendingPnt, gravity * -1 * nozzleDiameter)

                            bendingPnt_list.append(bendingPnt)
                            collisionPntParam_list.append(collisionPntParm)                   
                            
                    else:
                        print("collisionCheck False")

                        ## append undivided Chain as Catenary class
                        #self.catenaries.append(self.initCat)
            
            ## reorder pnts
            print(collisionPntParam_list)
            bendingPnt_listSorter = zip(collisionPntParam_list, bendingPnt_list)
            bendingPnt_listSorter.sort()
            collisionPntParam_list, bendingPnt_list = zip(* bendingPnt_listSorter)
            print(collisionPntParam_list)

            ## Cull duplicate pnts
            bendingPnt_list = rs.CullDuplicatePoints(bendingPnt_list)


            for i in range( len(bendingPnt_list) -1):
                aPt = bendingPnt_list[i]
                bPt = bendingPnt_list[i+1]
                dist = rs.Distance(aPt, bPt)
                catLen = dist ## change


                catenary = Catenary(aPt, bPt, catLen, self.dir)
                self.catenaries.append(catenary)

            ### get divided length
            for i in range( len(self.catenaries) ):
                cat = self.catenaries[i]
                if rs.Distance(cat.aPt, cat.bPt) < nozzleDiameter*2:
                    cat.len *= 1
                else:
                    cat.len *= 2
                    cat.rerun()





            



                        

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
print(tangledChainCat_list)
for tangledChainCat in tangledChainCat_list:
    for cat in tangledChainCat:
        catenary.append(cat.cat)