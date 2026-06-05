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

PUPPETDB = "dbs/puppet.db"

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
    def Validate(cube, discardSymmetric=False):
        if cube is None: return None

        # Reject symmetric arrangements
        if discardSymmetric and cube == do120(cube): return None

        occupied = []
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

legalMoves = {
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

asymmetricMoves = {
    "U": lambda c: Point.Validate(doU(c), discardSymmetric=True),
    "R": lambda c: Point.Validate(doR(c), discardSymmetric=True),
    "F": lambda c: Point.Validate(doF(c), discardSymmetric=True),
    "u": lambda c: Point.Validate(doU(doU(doU(c))), discardSymmetric=True),  # U'
    "r": lambda c: Point.Validate(doR(doR(doR(c))), discardSymmetric=True),  # R'
    "f": lambda c: Point.Validate(doF(doF(doF(c))), discardSymmetric=True),  # F'
}

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

OLD = object()

class CubePiece(Tag):
    Options = ["", "rlL", "udL", "fbL", "rlB", "udB", "fbB", "CCC"]

    class Inner(Tag):
        def __init__(self, parent): self.parent = parent
        def ondraw(self): return BLACK, None

    def __init__(self, solver, i, location):
        self.solver = solver
        self.inner = CubePiece.Inner(self)
        self.location = location  # where this piece should be
        self.index = i  # which index of pieces this piece corresponds to
        self.fixed = None
    def ondraw(self): return self.color, (GREEN if self.solver.cursor.get() is self and self.fixed is None else DGRAY)
    def getType(self): return self.solver.cube.get()[self.index]
    def cycle(self):
        if self.fixed: return
        i = CubePiece.Options.index(self.getType())
        cube2 = self.solver.cube.get().copy()
        while True:
            i = (i + 1) % len(CubePiece.Options)
            cube2[self.index] = CubePiece.Options[i]
            if Point.Validate(cube2) is not None: break
        self.solver.cube.update(cube2)

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


def countSymmetricArrangements():
    """ Symmetric elements:
        Because there are two unique pieces (MMM and CCC), the only symmetry the cube can have is through
    the diagonal (120°) that keeps both of those fixed. Then because L Blocks and Big Blocks are different,
    they have to be either all L Blocks around MMM and all Big Blocks around CCC (as in the solved state),
    or vice versa. Finally, because it must be rotationally symmetric, all L Blocks must be either clockwise
    or counterclockwise, and similarly with Big Blocks.
    That means there can only be: 2(from LB swap) * 3(L Blocks flip) * 3(Big Blocks flip) = 18.
    Of those, only 10 are possible arrangements (the other 8 self-intersect). Below is code to verify this.
    """

    #BxLx -> normal
    #LxBx -> LB swapped
    #. -> no flip
    #+ -> flipped clockwise
    #- -> flipped counterclockwise

    # These are all 18 symmetric candidates
    candidates = {
        # Physically possible arrangements:
        "B.L.": ["CCC", "rlB", "udL", "fbB", "udB", "fbL", "MMM", "rlL"],  # <-- solved state
        "L.B.": ["CCC", "rlL", "udB", "fbL", "udL", "fbB", "MMM", "rlB"],  # <-- cool shape btw!
        "B.L+": ["CCC", "rlB", "fbL", "fbB", "udB", "rlL", "MMM", "udL"],
        "L+B.": ["CCC", "fbL", "udB", "udL", "rlL", "fbB", "MMM", "rlB"],
        "B.L-": ["CCC", "rlB", "rlL", "fbB", "udB", "udL", "MMM", "fbL"],
        "L-B.": ["CCC", "udL", "udB", "rlL", "fbL", "fbB", "MMM", "rlB"],
        "B-L-": ["CCC", "udB", "rlL", "rlB", "fbB", "udL", "MMM", "fbL"],
        "L-B-": ["CCC", "udL", "rlB", "rlL", "fbL", "udB", "MMM", "fbB"],
        "B+L+": ["CCC", "fbB", "fbL", "udB", "rlB", "rlL", "MMM", "udL"],
        "L+B+": ["CCC", "fbL", "fbB", "udL", "rlL", "rlB", "MMM", "udB"],

        # Impossible arrangements:
        "B+L.": ["CCC", "fbB", "udL", "udB", "rlB", "fbL", "MMM", "rlL"],
        "L.B+": ["CCC", "rlL", "fbB", "fbL", "udL", "rlB", "MMM", "udB"],
        "B-L.": ["CCC", "udB", "udL", "rlB", "fbB", "fbL", "MMM", "rlL"],
        "L.B-": ["CCC", "rlL", "rlB", "fbL", "udL", "udB", "MMM", "fbB"],
        "B-L+": ["CCC", "udB", "fbL", "rlB", "fbB", "rlL", "MMM", "udL"],
        "L+B-": ["CCC", "fbL", "rlB", "udL", "rlL", "udB", "MMM", "fbB"],
        "B+L-": ["CCC", "fbB", "rlL", "udB", "rlB", "udL", "MMM", "fbL"],
        "L-B+": ["CCC", "udL", "fbB", "rlL", "fbL", "rlB", "MMM", "udB"],
    }

    solvable = GroupExplorer(PUPPETDB, serialiseState, allMoves)
    for k, v in candidates.items():
        isSymmetric = v == do120(v)
        isValid = Point.Validate(v) is not None
        isSolvable = solvable.lookup(serialiseState(v))
        print(f"Is {k} symmetric? {isSymmetric}. Is it valid? {isValid}")
        if isValid: print(f"    Construction path? {solvable.lookup(serialiseState(v))}")


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
    Solved = ["CCC", "rlB", "udL", "fbB", "udB", "fbL", "MMM", "rlL"]  # OCD

    def compareComponents(self, v):
        dU, dF, dR = v.dot(self.Uaxis), v.dot(self.Faxis), v.dot(self.Raxis)
        mU, mF, mR = abs(dU), abs(dF), abs(dR)
        m = max(mU, mF, mR)
        if m == mU: return ("U", dU < 0)
        if m == mF: return ("F", dF < 0)
        if m == mR: return ("R", dR < 0)
        return None

    def getOriented(self):
        # basis tell us, for each original cube axis, on which physical axis it's now (and whether it's reversed)
        common = Matrix.applyTo(self.transformation.get(), Matrix.zero)
        newBasis = {
            "U": self.compareComponents(Matrix.applyTo(self.transformation.get(), self.Uaxis) - common),
            "F": self.compareComponents(Matrix.applyTo(self.transformation.get(), self.Faxis) - common),
            "R": self.compareComponents(Matrix.applyTo(self.transformation.get(), self.Raxis) - common)}
        if ((not newBasis["U"]) or (not newBasis["F"]) or (not newBasis["R"])
                or newBasis["U"][0] == newBasis["F"][0]
                or newBasis["F"][0] == newBasis["R"][0]
                or newBasis["R"][0] == newBasis["U"][0]):
            return None
        return newBasis

    # Turn the absolute sequence into an axis-adjusted so lines up with visualisation
    def generateSequence(self):
        if self.oriented.get() is None: return None
        output = ""
        axis = self.oriented.get()
        for char in self.absolute.get():
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
        return output if output else " already solved"

    def getAbsolute(self):
        if "" in self.cube.get():  # incomplete construction
            return None
        else:
            e = serialiseState(self.cube.get())
            with shelve.open(PUPPETDB, flag="r") as db:
                return reverse(db[e][1]) if e in db else -1

    def generateTree(self):
        mesh = []
        for cubie in self.cubies:
            center, points = cubie.getPolygons()
            for i in points: i.orient(center)
            mesh.extend(points)
        for i in mesh:
            i.transform(Matrix.rotationT(-math.pi/2, Matrix.unitX) @ Matrix.rotationT(math.pi/2, Matrix.unitZ))
        return BSP.makeBSP(mesh)


    def __init__(self, optimised=False):
        self.optimised = optimised
        pygame.init()
        font = pygame.font.SysFont('Consolas', 18)
        window = pygame.display.set_mode((700, 700), pygame.RESIZABLE)

        self.cubies = [CubePiece(self, i, location) for i, location in enumerate(VisualSolver.Locations)]
        self.cubies[6].fixed = "MMM"  # MMM should stay the same!

        self.transformation = Cached()
        self.transformation.set(Matrix.scaleT(.3))
        def compose(new):
            # Note: set() used here instead of update() because equality on numpy matrices is fucked up
            # (also, the chances of update() ever saving us an update here are slim)
            self.transformation.set(new @ self.transformation.get())

        self.cursor = Cached()
        self.cursor.set(None)
        self.preserveCursor = False

        self.cube = Cached()
        self.cube.set(VisualSolver.Solved)
        self.symmetric = Cached(lambda: self.cube.get() == do120(self.cube.get())).dependsOn(self.cube)

        self.absolute = Cached(self.getAbsolute).dependsOn(self.cube)
        self.oriented = Cached(self.getOriented).dependsOn(self.transformation)
        self.relative = (Cached(self.generateSequence)
            .dependsOn(self.absolute)
            .dependsOn(self.oriented))

        # These are chosen so they match U, R and F rotations; depend on engine space orientation
        self.Uaxis = Matrix.unitY
        self.Faxis = Matrix.unitZ
        self.Raxis = -Matrix.unitX 

        pygame.display.set_caption("Automated Solver")
        clock = pygame.time.Clock()

        self.tree = Cached(self.generateTree).dependsOn(self.cube)
        dirty = (Cached(lambda: True)  # becomes True against visual changes; manually set to False once screen is updated
            .dependsOn(self.tree)
            .dependsOn(self.transformation)
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
                        if self.cursor.get() is not None:
                            # change the current cursor piece
                            self.preserveCursor = True
                            self.cursor.get().cycle()
                    elif event.key == pygame.K_r:
                        self.cube.update(VisualSolver.Solved)
                    else:
                        if pygame.key.get_pressed()[pygame.K_RSHIFT]:
                            new = Point.Validate(
                                doU(doU(doU(self.cube.get()))) if event.key == pygame.K_i else
                                doF(doF(doF(self.cube.get()))) if event.key == pygame.K_k else
                                doR(doR(doR(self.cube.get()))) if event.key == pygame.K_l else
                                None)
                        else:
                            new = Point.Validate(
                                doU(self.cube.get()) if event.key == pygame.K_i else
                                doF(self.cube.get()) if event.key == pygame.K_k else
                                doR(self.cube.get()) if event.key == pygame.K_l else
                                None)
                        if new is not None: self.cube.update(new)

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

            if dirty.get():
                window.fill(GRAY)

                BSP.count = 0
                BSP.cursor = None
                BSP.consultBSP(self.tree.get(), self.transformation.get())
                dirty.set(False)
                self.cursor.update(
                    self.cursor.get() if self.preserveCursor else  # if we just pressed F, don't change cursor!
                    BSP.cursor.parent if isinstance(BSP.cursor, CubePiece.Inner) else
                    BSP.cursor if isinstance(BSP.cursor, CubePiece) else
                    None)
                self.preserveCursor = False

                pygame.draw.circle(BSP.window, WHITE, (BSP.dims[0]//2, BSP.dims[1]//2), 3)
                window.blit(font.render(f"WASD, SHIFT and SPACE to move. Arrow keys to adjust camera. Press F on a piece to swap it.", True, (0, 0, 0)), (10, 10))
                window.blit(font.render(f"{BSP.count} polygons visible", True, (80, 80, 80)), (10, 40))

                if self.absolute.get() == -1:  # -> unsolvable
                    window.blit(font.render("Unsolvable!", True, (0, 0, 0)), (0, 70))
                elif self.absolute.get() is not None:  # -> solvable
                    window.blit(font.render(f"Solution (orientationless): {self.absolute.get()}", True, (0, 0, 0)), (10, 70))
                    if self.relative.get():
                        window.blit(font.render(f"Solution: {self.relative.get()}", True, (0, 0, 0)), (10, 100))

                if self.symmetric.get():
                    window.blit(font.render(f"(symmetric state!)", True, (0, 0, 0)), (10, 130))

                pygame.display.flip()

            clock.tick(60)

