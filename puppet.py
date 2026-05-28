import math
from eng import *
from gexplorer import *

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

def do120(cube):  # Rotate cube 120 degrees around cube[0,6] diagonal (keeping CC in place) in x->y->z direction
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
        if piece == "MMM":
            return [o.scale(1, 1, 1),
                o.scale(1, 1, 0), o.scale(1, 0, 1), o.scale(0, 1, 1),
                o.scale(0, 0, 1), o.scale(0, 1, 0), o.scale(1, 0, 0)]
        if piece == "CCC":
            return [o.scale(1, 1, 1),
                o.scale(1, 1, 2), o.scale(1, 2, 1), o.scale(2, 1, 1),
                o.scale(2, 2, 1), o.scale(2, 1, 2), o.scale(1, 2, 2),
                o.scale(2, 2, 2)]
        # L pattern: [o, fix active axis in 2 and combine others with (0,1)]
        if piece == "fbL":
            return [o.scale(1, 1, 1), o.scale(2, 1, 1), o.scale(2, 1, 0), o.scale(2, 0, 1), o.scale(2, 0, 0)]
        if piece == "rlL":
            return [o.scale(1, 1, 1), o.scale(1, 2, 1), o.scale(1, 2, 0), o.scale(0, 2, 1), o.scale(0, 2, 0)]
        if piece == "udL":
            return [o.scale(1, 1, 1), o.scale(1, 1, 2), o.scale(0, 1, 2), o.scale(1, 0, 2), o.scale(0, 0, 2)]
        # B pattern: [o, fix active axis in 1 and combine others with (1,2), fix active axis in 0 and combine others with (1,2)]
        if piece == "fbB":
            return [o.scale(1, 1, 1),
                o.scale(1, 2, 2), o.scale(1, 1, 2), o.scale(1, 2, 1),
                o.scale(0, 2, 2), o.scale(0, 1, 2), o.scale(0, 2, 1)]
        if piece == "rlB":
            return [o.scale(1, 1, 1),
                o.scale(2, 1, 2), o.scale(2, 1, 1), o.scale(1, 1, 2),
                o.scale(2, 0, 2), o.scale(2, 0, 1), o.scale(1, 0, 2)]
        if piece == "udB":
            return [o.scale(1, 1, 1),
                o.scale(2, 2, 1), o.scale(2, 1, 1), o.scale(1, 2, 1),
                o.scale(2, 2, 0), o.scale(2, 1, 0), o.scale(1, 2, 0)]
        raise Exception(f"Unknown piece label {piece}!")
    @staticmethod
    def Validate(cube):
        if cube is None: return None
        occupied = []
        for cube, loc in zip(cube, VisualSolver.Locations): occupied.extend(Point.PlacePiece(cube, loc))
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
GRAY = (64, 64, 64)

class CubePiece(Tag):
    Options = ["", "rlL", "udL", "fbL", "rlB", "udB", "fbB", "CCC"]
    Solved = [7, 4, 2, 6, 5, 3, None, 1]

    class Inner(Tag):
        def __init__(self, parent): self.parent = parent
        def ondraw(self): return WHITE, (GREEN if self.parent.solver.cursor is self.parent else GRAY)

    def __init__(self, solver, location):
        self.solver = solver
        self.inner = CubePiece.Inner(self)
        self.location = location  # where this piece should be
        self.n = 0  # which type of piece this should be
        self.fixed = None
    def ondraw(self): return self.color, (GREEN if self.solver.cursor is self and self.fixed is None else GRAY)
    def getType(self): return self.fixed if self.fixed else CubePiece.Options[self.n]
    def cycle(self):
        if self.fixed: return
        self.n = (self.n + 1) % len(CubePiece.Options)

    def getPolygons(self):
        o = self.location
        ptype = self.getType()
        inner = self.inner

        if ptype == "":
            self.color = None
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
                Bases.paralog(self, o.scale(3, 3, 3), o.scale(3, -1, 3), o.scale(-1, 3, 3)))
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
    # OCD convention definition
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
    @staticmethod
    def moveSequence(moves, axis):
        output = ""
        for char in moves:
            if char == "*": continue  # skip identity
            elif char == "U": index, invert = "U", False
            elif char == "R": index, invert = "R", False
            elif char == "F": index, invert = "F", False
            elif char == "u": index, invert = "U", True
            elif char == "r": index, invert = "R", True
            elif char == "f": index, invert = "F", True
            else: return " something went wrong!"

            output += " " + axis[index][0] + ("'" if invert else "")
            if axis[index][1]:  # the rotation moves along MMM (which determines orientation) -> udpate axis accordingly
                if index == "U": # R->F and F->R' if not inverted
                    axis = {"U": axis["U"], "R": (axis["F"][0], axis["F"][1] == invert), "F": (axis["R"][0], axis["R"][1] != invert)}
                elif index == "R":  # U->F' and F->U if not inverted
                    axis = {"U": (axis["F"][0], axis["F"][1] != invert), "R": axis["R"], "F": (axis["U"][0], axis["U"][1] == invert)}
                elif index == "F":  # U->R and R->U' if not inverted
                    axis = {"U": (axis["R"][0], axis["R"][1] == invert), "R": (axis["U"][0], axis["U"][1] != invert), "F": axis["F"]}
                else:
                    return " something went wrong!"

        return output if output else " (do nothing)"

    def compareComponents(self, v):
        dU, dF, dR = v.dot(self.Uaxis), v.dot(self.Faxis), v.dot(self.Raxis)
        mU, mF, mR = abs(dU), abs(dF), abs(dR)
        m = max(mU, mF, mR)
        if m == mU: return ("U", dU < 0)
        if m == mF: return ("F", dF < 0)
        if m == mR: return ("R", dR < 0)
        return None

    def generateCube(self):
        mesh = []
        for piece in self.pieces:
            center, points = piece.getPolygons()
            for i in points: i.orient(center)
            mesh.extend(points)

        cube = [piece.getType() for piece in self.pieces]
        if Point.Validate(cube) is None: return None
        if "" in cube:  # incomplete construction
            self.cached.absolute = self.cached.relative = None
        else:
            e = serialiseState(cube)
            with shelve.open("dbs/puppet.db", flag="r") as db:
                if e in db:
                    self.cached.absolute = reverse(db[e][1])
                    self.cached.relative = None
                else:
                    self.cached.absolute = -1
                    self.cached.relative = None

        for i in mesh: i.transform(Matrix.rotationT(-math.pi/2, Matrix.unitX) @ Matrix.rotationT(math.pi/2, Matrix.unitZ))
        return mesh

    class Cached:
        def __init__(self):
            self.absolute = None
            self.basis = None
            self.relative = None

    def __init__(self):
        pygame.init()
        font = pygame.font.SysFont('Consolas', 18)
        window = pygame.display.set_mode((700, 700), pygame.RESIZABLE)

        self.cursor = None
        self.preserveCursor = False
        self.cached = VisualSolver.Cached()
        self.pieces = [CubePiece(self, location) for location in VisualSolver.Locations]
        self.pieces[6].fixed = "MMM"  # MMM should stay the same!
        for p, s in enumerate(CubePiece.Solved):
            pass
            if s: self.pieces[p].n = s

        self.bsptree = BSP()
        self.bsptree.build(self.generateCube())

        # These are chosen so they match U, R and F rotations; depend on engine space orientation
        self.Uaxis = Matrix.unitY
        self.Faxis = Matrix.unitZ
        self.Raxis = -Matrix.unitX 
                
        transformation = Matrix.scaleT(.3)
        self.bsptree.dirty = True
        pygame.display.set_caption("Automated Solver")
        clock = pygame.time.Clock()

        BSP.window = window
        BSP.dims = pygame.display.get_surface().get_size()

        dt = .07
        while True:
            for event in pygame.event.get():
                if event.type == pygame.VIDEORESIZE:
                    BSP.dims = pygame.display.get_surface().get_size()
                    self.bsptree.dirty=True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_f:
                        if isinstance(self.cursor, CubePiece):
                            # change the piece
                            cube = None
                            while cube is None:
                                self.cursor.cycle()
                                cube = self.generateCube()
                            self.bsptree.build(cube)
                            self.bsptree.dirty=True
                            self.preserveCursor = True

                elif event.type == pygame.QUIT:
                    quit()

            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:  # space and shift
                transformation = Matrix.traslationT((0, +1*dt, 0)) @ transformation
                self.bsptree.dirty=True
            if keys[pygame.K_LSHIFT]:
                transformation = Matrix.traslationT((0, -1*dt, 0)) @ transformation
                self.bsptree.dirty=True
            if keys[pygame.K_w]:  # w and s
                transformation = Matrix.traslationT((0, 0, -1*dt)) @ transformation
                self.bsptree.dirty=True
            if keys[pygame.K_s]:
                transformation = Matrix.traslationT((0, 0, +1*dt)) @ transformation
                self.bsptree.dirty=True
            if keys[pygame.K_d]:  # a and d
                transformation = Matrix.traslationT((-1*dt, 0, 0)) @ transformation
                self.bsptree.dirty=True
            if keys[pygame.K_a]:
                transformation = Matrix.traslationT((+1*dt, 0, 0)) @ transformation
                self.bsptree.dirty=True
            if keys[pygame.K_e]:  # q and e (rotation)
                transformation = Matrix.rotationT(-20 * dt * math.pi/180, Matrix.unitZ) @ transformation
                self.bsptree.dirty=True
            if keys[pygame.K_q]:
                transformation = Matrix.rotationT(20 * dt * math.pi/180, Matrix.unitZ) @ transformation
                self.bsptree.dirty=True
            if keys[pygame.K_LEFT]:  # left and right
                transformation = Matrix.rotationT(-20 * dt * math.pi/180, Matrix.unitY) @ transformation
                self.bsptree.dirty=True
            if keys[pygame.K_RIGHT]:
                transformation = Matrix.rotationT(20 * dt * math.pi/180, Matrix.unitY) @ transformation
                self.bsptree.dirty=True
            if keys[pygame.K_DOWN]:  # up and down
                transformation = Matrix.rotationT(-20 * dt * math.pi/180, Matrix.unitX) @ transformation
                self.bsptree.dirty=True
            if keys[pygame.K_UP]:
                transformation = Matrix.rotationT(20 * dt * math.pi/180, Matrix.unitX) @ transformation
                self.bsptree.dirty=True

            if self.bsptree.dirty:
                self.bsptree.dirty = False

                common = Matrix.applyTo(transformation, Matrix.zero)
                # Basis dictionary tell us, for each canonical cube axis, which physical rotation achieves it (and whether it's reversed)
                newBasis = {
                    "U": self.compareComponents(Matrix.applyTo(transformation, self.Uaxis) - common),
                    "F": self.compareComponents(Matrix.applyTo(transformation, self.Faxis) - common),
                    "R": self.compareComponents(Matrix.applyTo(transformation, self.Raxis) - common)}
                if ((not newBasis["U"]) or (not newBasis["F"]) or (not newBasis["R"])
                        or newBasis["U"][0] == newBasis["F"][0]
                        or newBasis["F"][0] == newBasis["R"][0]
                        or newBasis["R"][0] == newBasis["U"][0]):
                    newBasis = None
                if newBasis != self.cached.basis:
                    self.cached.basis = newBasis
                    self.cached.relative = None

                window.fill((128, 128, 128))
                self.bsptree.render(transformation)
                if self.preserveCursor:
                    self.preserveCursor = False
                else:
                    if self.bsptree.cursor != self.cursor:  # cursor changed -> update cursor and force redraw
                        self.cursor = self.bsptree.cursor.parent if isinstance(self.bsptree.cursor, CubePiece.Inner) else self.bsptree.cursor
                        self.bsptree.dirty = True

                pygame.draw.circle(BSP.window, WHITE, (BSP.dims[0]//2, BSP.dims[1]//2), 3)
                window.blit(font.render(f"WASD, SHIFT and SPACE to move. Arrow keys to adjust camera. Press F on a piece to swap it.", True, (0, 0, 0)), (10, 10))
                window.blit(font.render(f"{self.bsptree.count} polygons visible", True, (80, 80, 80)), (10, 40))

                if self.cached.absolute == -1:  # -> unsolvable
                    window.blit(font.render("Unsolvable!", True, (0, 0, 0)), (0, 70))
                elif self.cached.absolute is not None:  # -> solvable
                    if self.cached.relative is None and self.cached.basis:
                        self.cached.relative = VisualSolver.moveSequence(self.cached.absolute, self.cached.basis)  # compute relative solution from basis

                    if self.cached.relative: window.blit(font.render(f"Solution: {self.cached.relative}", True, (0, 0, 0)), (10, 70))
                    window.blit(font.render(f"Solution (on default orientation): {self.cached.absolute}", True, (0, 0, 0)), (10, 100))

                pygame.display.flip()
            clock.tick(60)

