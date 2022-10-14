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

points = []

result = []
intpnts = []
toppnts = []
c =[]

prev_pntN_first=None

#Catenary direction
if flip == True:
    flip = -1
else:
    flip = 1


class Test:
    def __init__(self):
        print("hi")

test = Test()

class Catenary:

    def __init__(self, aPt, bPt, len, dir):
        self.aPt = aPt
        self.bPt = bPt
        self.len = len
        self.dir = dir
        self.cat = None
        self.extrdsrf = None
    
    def draw(self):
        print("Catenary.draw")
        self.cat = gh.Catenary(self.aPt, self.bPt, self.len, self.dir)
        #print(line)
    
    def extrd(self):
        print("Catenary.extrd")
        #save extruded surface as an obstacle
        path = rs.AddLine([0,0,0],[0,0,-100*flip])
        self.extrdsrf = rs.ExtrudeCurve(self.cat, path)
        


class Chain:

    def __init__(self, aPt, bPt, len, dir):
        self.aPt = aPt
        self.bPt = bPt
        self.len = len
        self.dir = dir
        self.catenaries = []
        """
        catenary = Catenary(aPt, bPt, len, dir)
        self.catenaries.append(catenary)
        """

    def tangle(self, prevChains):
        print("Chain.tangle")
        #get colliding points
        for prevChain in range(prevChains):
            for prevCat in range(prevChain):
                collision = 


        #move colliding points up
        #get divided length
        #





catenary =[]
vector = rs.coerce3dvector([0,0,-1])
for lineN, line in enumerate(lines):
    aaa = Catenary(rs.CurveStartPoint(line),rs.CurveEndPoint(line),y[lineN],vector*flip)
    aaa.draw()
    catenary.append(aaa.cat)

"""
if flip == True:
    flip = -1
else:
    flip = 1

for lineN, line in enumerate(lines):
    line = rs.coercecurve(line)
    point_a = rs.CurveStartPoint(line)
    point_b = rs.CurveEndPoint(line)
    vector = rs.coerce3dvector([0,0,-1])
    #
    cat = gh.Catenary(point_a,point_b,y[lineN],vector*flip)
    
    intpnts = []
    toppnts = []
    
    for i in range(exCatenary.BranchCount):
        prevs = exCatenary.Branch(i)
        prevsPath = exCatenary.Path(i)
        for j in range(prevs.Count):
            prev = prevs[j]
            prevcat = Catenary.Branch(i)[j]
            
            bool = rs.CurveSurfaceIntersection(cat, prev)
            if bool:
                vec = rs.coerce3dvector([0,0,1])
                projcat = gh.Project(cat,x,vec)
                projprevcat = gh.Project(prevcat,x,vec*flip)
                pnt = gh.CurveXCurve(projcat, projprevcat)[0]
                toppnts.append(pnt)
                print("hi")
                
                vec = rs.coerce3dvector([0,0,-1])
                pp= gh.ProjectPoint(pnt, vec*flip, prevcat)[0]
                rs.MoveObject(pp,[0,0,-0.4])
                intpnts.append(pp)
    
    toppnts.append(rs.CurveStartPoint(cat))
    toppnts.append(rs.CurveEndPoint(cat))
    intpnts.append(rs.CurveStartPoint(cat))
    intpnts.append(rs.CurveEndPoint(cat))
    print("waa")
    print(len(toppnts))
    print(len(intpnts))
    if toppnts:
        #print(toppnts)
        #toppnts = rs.SortPointList(toppnts)
    
        start = rs.CurveStartPoint(cat)
        distance = []
        for pnt in toppnts:
            distance.append(rs.Distance(start,pnt))
        
        toppnts = gh.SortList(distance, toppnts)[1]
        intpnts = gh.SortList(distance, intpnts)[1]
        
        
        
        dist = []
        for pntN in range(len(toppnts)-1):
            
            dist.append( round( rs.Distance( toppnts[pntN], toppnts[pntN+1] ), 2) )
            #print( rs.Distance( start , toppnts[pntN+1] ) )
        print(dist)
        print("aai")
        denom = gh.MassAddition(dist)[0]
        print(denom)
        
        for pntN in range(len(intpnts)-1):
            if prev_pntN_first==None:
                
                pntN_first = pntN
                #point_a = prev_pnt_a
                
            else:
                pntN_first = prev_pntN_first
                
                #point_a = intpnts[pntN]
            point_a = intpnts[pntN_first]
            point_b = intpnts[pntN+1]
            b = toppnts[pntN_first]
            topdist = round( rs.Distance( toppnts[pntN_first], toppnts[pntN+1] ), 2)
            
            vector = rs.coerce3dvector([0,0,-1])
            length = y[lineN]*topdist/denom
            print("topdist"+str(topdist))
            
            intdist = round( rs.Distance( intpnts[pntN_first], intpnts[pntN+1] ), 2)
            #
            print("length"+str(length))
            print("intdist"+str(intdist))
            
            if length > intdist or pntN == len(intpnts)-2:
                cat = gh.Catenary(point_a,point_b,length,vector*flip)
                print(pntN)
                print(length)
            
    
                result.append(cat)
                ##
                Catenary.Add(cat, GH_Path(lineN))
                path = rs.AddLine([0,0,0],[0,0,-100*flip])
                excat = rs.ExtrudeCurve(cat, path)
                ##
                exCatenary.Add(excat, GH_Path(lineN))
                
                prev_pntN_first = None
                
            else: 
                prev_pntN_first = pntN_first 
                print("yaaa"+str(prev_pntN_first))
"""