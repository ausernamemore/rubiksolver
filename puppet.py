import math
from eng import *
from gexplorer import *
from cached import *

"""
    Code by u/Adventurous_Fill7251
    Make sure to check out my Puppet Cube guide, available on my Reddit profile ;)

    Notes on how cube is represented:
    * MMM is the main block
    * CCC is the binding corner
    * __L are L shaped blocks
    * __B are Big Blocks
        (if you're not familiar with this notation, please refer to the guide)

    The order of the elements in the serialsied string as well as the orientation labels
    (rl, fb, ud) are set by convention.
    If you're a programmer: every code tagged with OCD is order-convention-dependant, so
    make sure you modify it if you change the convention.

    You can also add a number after each piece (MMM_1, rlL_2, udB_3, fbL_4, etc.) to make
    the solver consider two cubes with the same shape but different colors distinct cases.
    This expands the search space considerably (by a factor of 36), but I don't think
    it's interesting because there are well known algorithms to exchange colors once
    the puzzle is restored to its cube shape.
"""

def serialiseState(cube):
    # Get unique string representation of a cube state
    if cube is None: raise Exception("State to serialise is None!")
    return '-'.join(cube)

def deserialise(seq):
    return [
        seq[0:3],
        seq[4:7],
        seq[8:11],
        seq[12:15],
        seq[16:19],
        seq[20:23],
        seq[24:27],
        seq[28:31]]

#-------------------------------------------------#
    # Below is geometry logic to implement the move restrictions of the Puppet Cube v1

def changeAxis(piece): # x -> y -> z
    if piece[:2] == "fb": return "rl" + piece[2:]
    if piece[:2] == "rl": return "ud" + piece[2:]
    if piece[:2] == "ud": return "fb" + piece[2:]
    return piece
def rotateX90(piece):
    if piece[:2] == "rl": return "ud" + piece[2:]
    if piece[:2] == "ud": return "rl" + piece[2:]
    return piece
def rotateY90(piece):
    if piece[:2] == "ud": return "fb" + piece[2:]
    if piece[:2] == "fb": return "ud" + piece[2:]
    return piece
def rotateZ90(piece):
    if piece[:2] == "fb": return "rl" + piece[2:]
    if piece[:2] == "rl": return "fb" + piece[2:]
    return piece
def doU(cube):  # rotate around Z axis
    if cube is None: return None
    return [  # OCD
        rotateZ90(cube[3]),
        rotateZ90(cube[0]),
        rotateZ90(cube[1]),
        rotateZ90(cube[2]),
        cube[4],
        cube[5],
        cube[6],
        cube[7]]
def doF(cube):  # rotate around X axis
    if cube is None: return None    
    return [  # OCD
        rotateX90(cube[1]),
        rotateX90(cube[5]),
        cube[2],
        cube[3],
        rotateX90(cube[0]),
        rotateX90(cube[4]),
        cube[6],
        cube[7]]
def doR(cube):  # rotate around Y axis
    if cube is None: return None    
    return [  # OCD
        rotateY90(cube[4]),
        cube[1],
        cube[2],
        rotateY90(cube[0]),
        rotateY90(cube[7]),
        cube[5],
        cube[6],
        rotateY90(cube[3])]

def do120(cube):  # Rotate cube 120 degrees around cube[0,6] diagonal (keeping MMM in place) in x->y->z direction
    return [  # OCD
        changeAxis(cube[0]),
        changeAxis(cube[3]),
        changeAxis(cube[7]),
        changeAxis(cube[4]),
        changeAxis(cube[1]),
        changeAxis(cube[2]),
        changeAxis(cube[6]),
        changeAxis(cube[5])]
def doY90(cube):  # rotate around Y axis
    return [  # OCD
        rotateY90(cube[4]),
        rotateY90(cube[5]),
        rotateY90(cube[1]),
        rotateY90(cube[0]),
        rotateY90(cube[7]),
        rotateY90(cube[6]),
        rotateY90(cube[2]),
        rotateY90(cube[3])]
# Note: these two are enough to generate all other rotations and I'm lazy af so these are all I'll write.

class Point:
    @staticmethod
    def PlacePiece(piece, o):
        if piece == "": return []
        if piece[:3] == "MMM":
            return [o.scale(1, 1, 1),
                o.scale(1, 1, 0), o.scale(1, 0, 1), o.scale(0, 1, 1),
                o.scale(0, 0, 1), o.scale(0, 1, 0), o.scale(1, 0, 0)]
        if piece[:3] == "CCC":
            return [o.scale(1, 1, 1),
                o.scale(1, 1, 2), o.scale(1, 2, 1), o.scale(2, 1, 1),
                o.scale(2, 2, 1), o.scale(2, 1, 2), o.scale(1, 2, 2),
                o.scale(2, 2, 2)]
        # L pattern: [o, fix active axis in 2 and combine others with (0,1)]
        if piece[:3] == "fbL":
            return [o.scale(1, 1, 1), o.scale(2, 1, 1), o.scale(2, 1, 0), o.scale(2, 0, 1), o.scale(2, 0, 0)]
        if piece[:3] == "rlL":
            return [o.scale(1, 1, 1), o.scale(1, 2, 1), o.scale(1, 2, 0), o.scale(0, 2, 1), o.scale(0, 2, 0)]
        if piece[:3] == "udL":
            return [o.scale(1, 1, 1), o.scale(1, 1, 2), o.scale(0, 1, 2), o.scale(1, 0, 2), o.scale(0, 0, 2)]
        # B pattern: [o, fix active axis in 1 and combine others with (1,2), fix active axis in 0 and combine others with (1,2)]
        if piece[:3] == "fbB":
            return [o.scale(1, 1, 1),
                o.scale(1, 2, 2), o.scale(1, 1, 2), o.scale(1, 2, 1),
                o.scale(0, 2, 2), o.scale(0, 1, 2), o.scale(0, 2, 1)]
        if piece[:3] == "rlB":
            return [o.scale(1, 1, 1),
                o.scale(2, 1, 2), o.scale(2, 1, 1), o.scale(1, 1, 2),
                o.scale(2, 0, 2), o.scale(2, 0, 1), o.scale(1, 0, 2)]
        if piece[:3] == "udB":
            return [o.scale(1, 1, 1),
                o.scale(2, 2, 1), o.scale(2, 1, 1), o.scale(1, 2, 1),
                o.scale(2, 2, 0), o.scale(2, 1, 0), o.scale(1, 2, 0)]
        raise Exception(f"Unknown piece label {piece}!")
    @staticmethod
    def Validate(cube):
        if cube is None: return None
        occupied = []
        print(f"Validating {cube}...")
        for piece, loc in zip(cube, VisualSolver.Locations): occupied.extend(Point.PlacePiece(piece, loc))
        points = set()
        for p in occupied:
            p = f"{p[0]}.{p[1]}.{p[2]}"
            if p in points: return None
            points.add(p)
        return cube

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
    def scale(self, px, py, pz): return (self.x*px, self.y*py, self.z*pz)

def reverse(seq):
    if seq is None: return None
    result = ""
    for char in seq:
        result = (
            "u" if char == "U" else
            "r" if char == "R" else
            "f" if char == "F" else
            "U" if char == "u" else
            "R" if char == "r" else
            "F" if char == "f" else
            "*" if char == "*" else
            "?") + result
    return result

allMoves = {
    "o": do120,  # no need to validate because reorienting is always legal
    "U": lambda c: Point.Validate(doU(c)),
    "R": lambda c: Point.Validate(doR(c)),
    "F": lambda c: Point.Validate(doF(c)),
    "u": lambda c: Point.Validate(doU(doU(doU(c)))),  # U'
    "r": lambda c: Point.Validate(doR(doR(doR(c)))),  # R'
    "f": lambda c: Point.Validate(doF(doF(doF(c)))),  # F'
}
"""
    Note: because there is no 90° reorientation move included (only 120° and the three basic axis and inverses),
        the element at index 6 (OCD) of the generator can never move to a different position.
    -> For convention, I chose to keep the MMM there, because it contains the centers so it makes sense it doesn't move
"""

#-------------------------------------------------#
    # 3d processing code

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 128, 0)
GREEN = (0, 255, 0)
DGREEN = (0, 128, 0)
CYAN = (0, 128, 128)
MAGENTA = (255, 0, 255)
GRAY = (128, 128, 128)
DGRAY = (64, 64, 64)

class CubePiece(Tag):
    Options = ["", "rlL", "udL", "fbL", "rlB", "udB", "fbB", "CCC"]
    Solved = [7, 4, 2, 6, 5, 3, None, 1]

    class Inner(Tag):
        def __init__(self, parent): self.parent = parent
        def ondraw(self): return BLACK, None

    def __init__(self, solver, location):
        self.solver = solver
        self.inner = CubePiece.Inner(self)
        self.location = location  # where this piece should be
        self.n = 0  # which type of piece this should be
        self.fixed = None
    def ondraw(self): return self.color, (GREEN if self.solver.cursor.value is self and self.fixed is None else DGRAY)
    def getType(self): return self.fixed if self.fixed else CubePiece.Options[self.n]
    def cycle(self):
        if self.fixed: return
        self.n = (self.n + 1) % len(CubePiece.Options)

    def getPolygons(self):
        o = self.location
        ptype = self.getType()
        inner = None if self.solver.optimised else self.inner

        if ptype == "":
            self.color = GRAY
            return o.scale(2, 2, 2), (
                Bases.paralog(self, o.scale(3, 3, 3), o.scale(1, 3, 3), o.scale(3, 1, 3)) +
                Bases.paralog(self, o.scale(3, 3, 3), o.scale(3, 1, 3), o.scale(3, 3, 1)) +
                Bases.paralog(self, o.scale(3, 3, 3), o.scale(3, 3, 1), o.scale(1, 3, 3)))
        if ptype == "MMM":
            self.color = CYAN
            return o.scale(1, 1, 1), (
                Bases.paralog(self, o.scale(3, -1, -1), o.scale(3, 1, -1), o.scale(3, -1, -3)) +  # X cubicle
                Bases.paralog(self, o.scale(3, -1, -1), o.scale(3, -1, 1), o.scale(3, -3, -1)) +
                #Bases.paralog(inner, o.scale(3, -3, -1), o.scale(3, -3, 1), o.scale(1, -3, -1)) +
                #Bases.paralog(inner, o.scale(3, -1, -3), o.scale(3, 1, -3), o.scale(1, -1, -3)) +
                Bases.paralog(self, o.scale(-1, 3, -1), o.scale(1, 3, -1), o.scale(-1, 3, -3)) +  # Y cubicle
                Bases.paralog(self, o.scale(-1, 3, -1), o.scale(-1, 3, 1), o.scale(-3, 3, -1)) +
                #Bases.paralog(inner, o.scale(-3, 3, -1), o.scale(-3, 3, 1), o.scale(-3, 1, -1)) +
                #Bases.paralog(inner, o.scale(-1, 3, -3), o.scale(1, 3, -3), o.scale(-1, 1, -3)) +
                Bases.paralog(self, o.scale(-1, -1, 3), o.scale(1, -1, 3), o.scale(-1, -3, 3)) +  # Z cubicle
                Bases.paralog(self, o.scale(-1, -1, 3), o.scale(-1, 1, 3), o.scale(-3, -1, 3)) +
                #Bases.paralog(inner, o.scale(-3, -1, 3), o.scale(-3, 1, 3), o.scale(-3, -1, 1)) +
                #Bases.paralog(inner, o.scale(-1, -3, 3), o.scale(1, -3, 3), o.scale(-1, -3, 1)) +
                Bases.paralog(self, o.scale(3, 3, 3), o.scale(3, 3, -1), o.scale(3, -1, 3)) +  # main block
                Bases.paralog(self, o.scale(3, 3, 3), o.scale(-1, 3, 3), o.scale(3, 3, -1)) +
                Bases.paralog(self, o.scale(3, 3, 3), o.scale(3, -1, 3), o.scale(-1, 3, 3)) +

                Bases.paralog(self, o.scale(1, -3, 3), o.scale(-1, -3, 3), o.scale(1, -3, -3)) + # X strip
                Bases.paralog(self, o.scale(1, 3, -3), o.scale(-1, 3, -3), o.scale(1, -3, -3)) +
                Bases.paralog(self, o.scale(-3, 1, 3), o.scale(-3, -1, 3), o.scale(-3, 1, -3)) + # Y strip
                Bases.paralog(self, o.scale(3, 1, -3), o.scale(3, -1, -3), o.scale(-3, 1, -3)) +
                Bases.paralog(self, o.scale(-3, 3, 1), o.scale(-3, 3, -1), o.scale(-3, -3, 1)) + # Z strip
                Bases.paralog(self, o.scale(3, -3, 1), o.scale(3, -3, -1), o.scale(-3, -3, 1)))
        if ptype == "CCC":
            self.color = ORANGE
            return o.scale(3, 3, 3), (
                Bases.paralog(inner, o.scale(1, 1, 1), o.scale(5, 1, 1), o.scale(1, 5, 1)) +
                Bases.paralog(inner, o.scale(1, 1, 1), o.scale(1, 1, 5), o.scale(5, 1, 1)) +
                Bases.paralog(inner, o.scale(1, 1, 1), o.scale(1, 5, 1), o.scale(1, 1, 5)) +
                Bases.paralog(self, o.scale(5, 5, 5), o.scale(5, 1, 5), o.scale(5, 5, 1)) +
                Bases.paralog(self, o.scale(5, 5, 5), o.scale(5, 5, 1), o.scale(1, 5, 5)) +
                Bases.paralog(self, o.scale(5, 5, 5), o.scale(1, 5, 5), o.scale(5, 1, 5)))
        if ptype == "fbL":
            self.color = RED
            return o.scale(4, 1, 1), (
                Bases.paralog(inner, o.scale(5, -1, -1), o.scale(3, -1, -1), o.scale(5, 3, -1)) +
                Bases.paralog(inner, o.scale(5, -1, -1), o.scale(3, -1, -1), o.scale(5, -1, 3)) +
                Bases.paralog(self, o.scale(3, 3, 3), o.scale(1, 3, 3), o.scale(3, 1, 3)) +
                Bases.paralog(self, o.scale(3, 3, 3), o.scale(1, 3, 3), o.scale(3, 3, 1)) +
                Bases.paralog(self, o.scale(5, 3, 3), o.scale(3, 3, 3), o.scale(5, 3, -1)) +
                Bases.paralog(self, o.scale(5, 3, 3), o.scale(3, 3, 3), o.scale(5, -1, 3)) +
                Bases.paralog(self, o.scale(5, 3, 3), o.scale(5, 3, -1), o.scale(5, -1, 3)))
        if ptype == "rlL":
            self.color = RED
            return o.scale(1, 4, 1), (
                Bases.paralog(inner, o.scale(-1, 5, -1), o.scale(-1, 3, -1), o.scale(3, 5, -1)) +
                Bases.paralog(inner, o.scale(-1, 5, -1), o.scale(-1, 3, -1), o.scale(-1, 5, 3)) +
                Bases.paralog(self, o.scale(3, 3, 3), o.scale(3, 1, 3), o.scale(1, 3, 3)) +
                Bases.paralog(self, o.scale(3, 3, 3), o.scale(3, 1, 3), o.scale(3, 3, 1)) +
                Bases.paralog(self, o.scale(3, 5, 3), o.scale(3, 3, 3), o.scale(3, 5, -1)) +
                Bases.paralog(self, o.scale(3, 5, 3), o.scale(3, 3, 3), o.scale(-1, 5, 3)) +
                Bases.paralog(self, o.scale(3, 5, 3), o.scale(3, 5, -1), o.scale(-1, 5, 3)))
        if ptype == "udL":
            self.color = RED
            return o.scale(1, 1, 4), (
                Bases.paralog(inner, o.scale(-1, -1, 5), o.scale(-1, -1, 3), o.scale(3, -1, 5)) +
                Bases.paralog(inner, o.scale(-1, -1, 5), o.scale(-1, -1, 3), o.scale(-1, 3, 5)) +
                Bases.paralog(self, o.scale(3, 3, 3), o.scale(3, 3, 1), o.scale(1, 3, 3)) +
                Bases.paralog(self, o.scale(3, 3, 3), o.scale(3, 3, 1), o.scale(3, 1, 3)) +
                Bases.paralog(self, o.scale(3, 3, 5), o.scale(3, 3, 3), o.scale(3, -1, 5)) +
                Bases.paralog(self, o.scale(3, 3, 5), o.scale(3, 3, 3), o.scale(-1, 3, 5)) +
                Bases.paralog(self, o.scale(3, 3, 5), o.scale(3, -1, 5), o.scale(-1, 3, 5)))
        if ptype == "fbB":
            self.color = DGREEN
            return o.scale(1, 4, 4), (
                Bases.paralog(inner, o.scale(3, 5, 1), o.scale(-1, 5, 1), o.scale(3, 3, 1)) +
                Bases.paralog(inner, o.scale(3, 1, 5), o.scale(-1, 1, 5), o.scale(3, 1, 3)) +
                Bases.paralog(inner, o.scale(-1, 5, 1), o.scale(-1, 3, 1), o.scale(-1, 5, 5)) +
                Bases.paralog(inner, o.scale(-1, 1, 5), o.scale(-1, 1, 3), o.scale(-1, 3, 5)) +
                Bases.paralog(self, o.scale(3, 1, 1), o.scale(3, 5, 1), o.scale(3, 1, 5)) +
                Bases.paralog(self, o.scale(3, 1, 5), o.scale(-1, 1, 5), o.scale(3, 5, 5)) +
                Bases.paralog(self, o.scale(3, 5, 1), o.scale(-1, 5, 1), o.scale(3, 5, 5)))
        if ptype == "rlB":
            self.color = DGREEN
            return o.scale(4, 1, 4), (
                Bases.paralog(inner, o.scale(5, 3, 1), o.scale(5, -1, 1), o.scale(3, 3, 1)) +
                Bases.paralog(inner, o.scale(1, 3, 5), o.scale(1, -1, 5), o.scale(1, 3, 3)) +
                Bases.paralog(inner, o.scale(5, -1, 1), o.scale(3, -1, 1), o.scale(5, -1, 5)) +
                Bases.paralog(inner, o.scale(1, -1, 5), o.scale(1, -1, 3), o.scale(3, -1, 5)) +
                Bases.paralog(self, o.scale(1, 3, 1), o.scale(5, 3, 1), o.scale(1, 3, 5)) +
                Bases.paralog(self, o.scale(1, 3, 5), o.scale(1, -1, 5), o.scale(5, 3, 5)) +
                Bases.paralog(self, o.scale(5, 3, 1), o.scale(5, -1, 1), o.scale(5, 3, 5)))
        if ptype == "udB":
            self.color = DGREEN
            return o.scale(4, 4, 1), (
                Bases.paralog(inner, o.scale(5, 1, 3), o.scale(5, 1, -1), o.scale(3, 1, 3)) +
                Bases.paralog(inner, o.scale(1, 5, 3), o.scale(1, 5, -1), o.scale(1, 3, 3)) +
                Bases.paralog(inner, o.scale(5, 1, -1), o.scale(3, 1, -1), o.scale(5, 5, -1)) +
                Bases.paralog(inner, o.scale(1, 5, -1), o.scale(1, 3, -1), o.scale(3, 5, -1)) +
                Bases.paralog(self, o.scale(1, 1, 3), o.scale(5, 1, 3), o.scale(1, 5, 3)) +
                Bases.paralog(self, o.scale(1, 5, 3), o.scale(1, 5, -1), o.scale(5, 5, 3)) +
                Bases.paralog(self, o.scale(5, 1, 3), o.scale(5, 1, -1), o.scale(5, 5, 3)))


class VisualSolver:
    # Important: Do NOT change these coordinate points as they're tied to OCD!
        #If you want to rotate the cube, simply apply the rotation after generating the mesh instead.
    Locations = [  # OCD
        Point( 1,  1,  1), # 0
        Point( 1, -1,  1), # 1
        Point(-1, -1,  1), # 2
        Point(-1,  1,  1), # 3
        Point( 1,  1, -1), # 4
        Point( 1, -1, -1), # 5
        Point(-1, -1, -1), # 6
        Point(-1,  1, -1), # 7
    ]

    # Turn the absolute sequence into an axis-adjusted so lines up with visualisation
    def generateSequence(self):
        output = ""
        axis = self.oriented.value
        for char in self.absolute.value:
            if char == "*": continue  # skip identity
            elif char == "U": index, invert = "U", False
            elif char == "R": index, invert = "R", False
            elif char == "F": index, invert = "F", False
            elif char == "u": index, invert = "U", True
            elif char == "r": index, invert = "R", True
            elif char == "f": index, invert = "F", True
            else: raise Exception("Something went wrong!")
            output += " " + axis[index][0] + ("'" if invert else "")
            if axis[index][1]:  # the rotation moves along MMM (which determines orientation) -> udpate axis accordingly
                if index == "U": # R->F and F->R' if not inverted
                    axis = {"U": axis["U"], "R": (axis["F"][0], axis["F"][1] == invert), "F": (axis["R"][0], axis["R"][1] != invert)}
                elif index == "R":  # U->F' and F->U if not inverted
                    axis = {"U": (axis["F"][0], axis["F"][1] != invert), "R": axis["R"], "F": (axis["U"][0], axis["U"][1] == invert)}
                elif index == "F":  # U->R and R->U' if not inverted
                    axis = {"U": (axis["R"][0], axis["R"][1] == invert), "R": (axis["U"][0], axis["U"][1] != invert), "F": axis["F"]}
                else:
                    raise Exception("Something went wrong!")
        self.relative.update(output if output else " already solved")

    def compareComponents(self, v):
        dU, dF, dR = v.dot(self.Uaxis), v.dot(self.Faxis), v.dot(self.Raxis)
        mU, mF, mR = abs(dU), abs(dF), abs(dR)
        m = max(mU, mF, mR)
        if m == mU: return ("U", dU < 0)
        if m == mF: return ("F", dF < 0)
        if m == mR: return ("R", dR < 0)
        return None

    def generateTree(self):
        cube = [piece.getType() for piece in self.pieces]
        if Point.Validate(cube) is None: return None

        if "" in cube:  # incomplete construction
            self.absolute.update(None)
        else:
            e = serialiseState(cube)
            with shelve.open("dbs/puppet.db", flag="r") as db:
                self.absolute.update(reverse(db[e][1]) if e in db else -1)

        mesh = []
        for piece in self.pieces:
            center, points = piece.getPolygons()
            for i in points: i.orient(center)
            mesh.extend(points)

        for i in mesh: i.transform(Matrix.rotationT(-math.pi/2, Matrix.unitX) @ Matrix.rotationT(math.pi/2, Matrix.unitZ))
        self.tree.update(BSP.makeBSP(mesh))

    def __init__(self, optimised=False):
        self.optimised = optimised
        pygame.init()
        font = pygame.font.SysFont('Consolas', 18)
        window = pygame.display.set_mode((700, 700), pygame.RESIZABLE)

        self.cursor = Cached()
        self.preserveCursor = False
        self.absolute = Cached()
        self.oriented = Cached()
        self.relative = (Cached()
            .dependsOn(self.absolute)
            .dependsOn(self.oriented))
        self.pieces = [CubePiece(self, location) for location in VisualSolver.Locations]
        self.pieces[6].fixed = "MMM"  # MMM should stay the same!
        for p, s in enumerate(CubePiece.Solved):
            if s: self.pieces[p].n = s

        # These are chosen so they match U, R and F rotations; depend on engine space orientation
        self.Uaxis = Matrix.unitY
        self.Faxis = Matrix.unitZ
        self.Raxis = -Matrix.unitX 

        transformation = Cached(Matrix.scaleT(.3))
        def compose(new):
            # Note: set() used here instead of update() because equality on numpy matrices is fucked up
            # (also, the chances of update() ever saving us an update here are slim)
            transformation.set(new @ transformation.value)
        pygame.display.set_caption("Automated Solver")
        clock = pygame.time.Clock()

        self.tree = Cached()
        self.generateTree()
        dirty = (Cached(True)  # becomes True when someting changes; manually set to False once screen is updated
            .dependsOn(self.tree)
            .dependsOn(transformation)
            .dependsOn(self.cursor))

        BSP.window = window
        BSP.dims = pygame.display.get_surface().get_size()

        dt = .07
        while True:
            for event in pygame.event.get():
                if event.type == pygame.VIDEORESIZE:
                    BSP.dims = pygame.display.get_surface().get_size()
                    dirty.reset()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_f:
                        if self.cursor.value is not None:
                            # change the current cursor piece
                            self.preserveCursor = True
                            self.tree.update(None)
                            while self.tree.value is None:
                                self.cursor.value.cycle()
                                self.generateTree()

                elif event.type == pygame.QUIT:
                    quit()

            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]: compose(Matrix.traslationT((0, +1*dt, 0)))
            if keys[pygame.K_LSHIFT]: compose(Matrix.traslationT((0, -1*dt, 0)))
            if keys[pygame.K_w]: compose(Matrix.traslationT((0, 0, -1*dt)))
            if keys[pygame.K_s]: compose(Matrix.traslationT((0, 0, +1*dt)))
            if keys[pygame.K_d]: compose(Matrix.traslationT((-1*dt, 0, 0)))
            if keys[pygame.K_a]: compose(Matrix.traslationT((+1*dt, 0, 0)))
            if keys[pygame.K_e]: compose(Matrix.rotationT(-20 * dt * math.pi/180, Matrix.unitZ))
            if keys[pygame.K_q]: compose(Matrix.rotationT(20 * dt * math.pi/180, Matrix.unitZ))
            if keys[pygame.K_LEFT]: compose(Matrix.rotationT(-20 * dt * math.pi/180, Matrix.unitY))
            if keys[pygame.K_RIGHT]: compose(Matrix.rotationT(20 * dt * math.pi/180, Matrix.unitY))
            if keys[pygame.K_DOWN]: compose(Matrix.rotationT(-20 * dt * math.pi/180, Matrix.unitX))
            if keys[pygame.K_UP]: compose(Matrix.rotationT(20 * dt * math.pi/180, Matrix.unitX))

            if dirty.value:
                dirty.update(False)

                # basis tell us, for each original cube axis, which physical axis carries it now (and whether it's reversed)
                common = Matrix.applyTo(transformation.value, Matrix.zero)
                newBasis = {
                    "U": self.compareComponents(Matrix.applyTo(transformation.value, self.Uaxis) - common),
                    "F": self.compareComponents(Matrix.applyTo(transformation.value, self.Faxis) - common),
                    "R": self.compareComponents(Matrix.applyTo(transformation.value, self.Raxis) - common)}
                if ((not newBasis["U"]) or (not newBasis["F"]) or (not newBasis["R"])
                        or newBasis["U"][0] == newBasis["F"][0]
                        or newBasis["F"][0] == newBasis["R"][0]
                        or newBasis["R"][0] == newBasis["U"][0]):
                    newBasis = None
                self.oriented.update(newBasis)

                window.fill(GRAY)

                BSP.count = 0
                BSP.cursor = None
                BSP.consultBSP(self.tree.value, transformation.value)
                self.cursor.update(
                    self.cursor.value if self.preserveCursor else  # if we just pressed F, don't change cursor!
                    BSP.cursor.parent if isinstance(BSP.cursor, CubePiece.Inner) else
                    BSP.cursor if isinstance(BSP.cursor, CubePiece) else
                    None)
                self.preserveCursor = False

                pygame.draw.circle(BSP.window, WHITE, (BSP.dims[0]//2, BSP.dims[1]//2), 3)
                window.blit(font.render(f"WASD, SHIFT and SPACE to move. Arrow keys to adjust camera. Press F on a piece to swap it.", True, (0, 0, 0)), (10, 10))
                window.blit(font.render(f"{BSP.count} polygons visible", True, (80, 80, 80)), (10, 40))

                if self.absolute.value == -1:  # -> unsolvable
                    window.blit(font.render("Unsolvable!", True, (0, 0, 0)), (0, 70))
                elif self.absolute.value is not None:  # -> solvable
                    window.blit(font.render(f"Solution (orientationless): {self.absolute.value}", True, (0, 0, 0)), (10, 70))
                    if self.oriented.value and (self.relative.value is None):  # compute relative solution from basis
                        self.generateSequence()
                if self.relative.value:
                    window.blit(font.render(f"Solution: {self.relative.value}", True, (0, 0, 0)), (10, 100))

                pygame.display.flip()

            clock.tick(60)

