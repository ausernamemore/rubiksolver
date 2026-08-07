from puppet import *
import sys

DEFAULT = 64  # default depth

"""
All physically possible (non-intersecting) arrangements of the pieces are split into:
    (note: I'll be using 'uts' to refer to 'up-to-symmetry' when counting orders.)

    -> 13'174 (4'398 uts) solvable ones:
        Why 4'398 up to symmetry? Because the only fixed piece is the main block. Thus a reorientation (120°)
        that keeps it fix is considered a "different" position, even though it's obviously the same position.
        All except the 10 symmetric positions (which remain the same under this reorientation). You can see
        why there are 10, and see each of them, in the function 'countSymmetricArrangements()'. There you can
        also check that all are solvable, and thus belong to this group.
        Because of this, there are
            (13'174 - 10) / 3  +  10   =   4'398 uts
        For the unsolvable groups, just divide the raw count by 3, as they have no symmetric elements in them.

        If accounting for piece coloring, each of the 13'174 can be seen as unique, since each triply-counted
        state corresponds to the 3 ways to color the main block. Then we have 3! ways to place the L blocks
        (we can only rearrange them, since their orientation is already determined); the same applies to the
        Big blocks, giving us 36 different variants. The binding corner cannot be freely oriented because its
        orientation is uniquely determined by that of the other corners.
        Thus, there are 13'174*36  =  474'264 unique corner arrangements, accounting for coloring.
        -> You can verify this by decompressing colored.zip and loading it up as a database!

    -> 858 (286 uts) unsolvable states, which are temselves split into:
        - x16 of order 12 (4 uts) -> one face turns freely but only that face
        - x28 of order  9 (3 uts) -> one face turns, but one position is impossible
        - x20 of order  6 (2 uts) -> only a quarter turn back and forth is possible
        - x20 of order  3 (1 uts) -> no moves possible; cube is completely stuck
            (These 74 groups I call "Boring" because they're too restricted)

        -  x1 of order 138 (46 uts) -> the beast
            -> minimal generator:
                either CCC-udL-udB-fbB-rlL-fbL-MMM-rlB or CCC-rlB-udB-fbB-udL-rlL-MMM-fbL
        -  x2 of order  48 (16 uts) -> the two devils
            -> minimal generator:
                either udL-CCC-fbB-fbL-fbL-fbB-MMM-fbB or fbB-CCC-fbB-fbL-fbL-fbB-MMM-udL (devil A)
                either fbL-CCC-udB-udL-udL-udB-MMM-udB or udB-CCC-udB-udL-udL-udB-MMM-fbL (devil B)
            (By minimal I mean the one that is closest to all other positions)
"""

# Call with an argment to skip visual solver and run as command-line tool
if len(sys.argv) < 2:
    VisualSolver(optimised=True)
        # Set optimised=True to hide internal faces (improves CPU usage but looks slightly uglier)


explorer = GroupExplorer(f"dbs/puppet.db", serialiseState, legalMoves)
    # You can download the fully-explored puppet.db or compute it yourself
    # You may also load up other dbs or explore ones yourself

# Common moves (in normal orientations; mirror for mirror cases):
    #      exchange: F' U' F  U  (with BBs aligned) (last U is irrelevant)
    # sledge-hammer: R' F  R  F' (with BBs aligned)
    #  inverse-sexy: U  R  U' R' (with BBs aligned)
    #  quasi-hammer:    F  R  F' (with BBs misaligned)

both = [
    'udL-fbB-MMM-fbL-udL-fbB-CCC-rlB',  # -> exchange
    'fbL-fbB-MMM-udL-udL-fbB-CCC-rlB',  # -> exchange
    'rlL-fbB-MMM-udL-udL-fbB-CCC-rlB',  # -> exchange
    'rlB-rlL-MMM-udL-udL-fbB-CCC-rlB',  # -> wont exchange, but sledge-hammer
    'udL-fbB-MMM-rlL-udL-fbB-CCC-rlB',  # -> wont exchange nor sledge-hammer, but inverse-sexy
    'fbL-udL-MMM-fbB-udL-fbB-CCC-rlB']  # -> wont exchange nor sledge-hammer nor inverse-sexy, but U' R' U  R

bigBlock = [
    'fbL-fbB-MMM-fbL-udL-fbB-CCC-rlB',  # -> exchange
    'fbL-fbB-MMM-rlL-udL-fbB-CCC-rlB',  # -> exchange
    'rlL-fbB-MMM-fbL-udL-fbB-CCC-rlB',  # -> exchange
    'rlB-rlL-MMM-rlL-udL-fbB-CCC-rlB',  # -> wont exchange, but sledge-hammer
    'rlB-rlL-MMM-fbL-udL-fbB-CCC-rlB',  # -> wont exchange, but sledge-hammer
    'fbL-rlL-MMM-fbB-udL-fbB-CCC-rlB']  # -> wont exchange nor sledge-hammer, but inverse-sexy

lBlock = [
    'fbL-udB-MMM-udL-udL-fbB-CCC-rlB',  # simplifiable
    'udB-fbL-MMM-udL-udL-fbB-CCC-rlB',  # simplifiable  # -> in these two the flat L and the big block form a rectangle
    'udL-fbL-MMM-udB-udL-fbB-CCC-rlB',  # -> quasi-hammer as Pistol
    'udL-udB-MMM-fbL-udL-fbB-CCC-rlB',  # -> quasi-hammer as Pistol
    'rlL-udB-MMM-udL-udL-fbB-CCC-rlB',  # -> wont quasi-hammer as Pistol, but quasi-hammer as Digit
    'udB-udL-MMM-fbL-udL-fbB-CCC-rlB']  # -> wont quasi-hammer as Pistol, but quasi-hammer as Digit

def axisY90(axis): return {"U": axis["F"], "R": axis["R"], "F": (axis["U"][0], not axis["U"][1])}  # Y90 rotation
def axis120(axis): return {"U": axis["F"], "R": axis["U"], "F": axis["R"]}

def findSolution(cube):  # Return a orientation-relative solution to any cube layout, regardless of where MMM is.
    start = cube.index("MMM")  # find position of MMM
    axis = {"U": ("U", False), "F": ("F", False), "R": ("R", False)}
    if start in [0, 1, 2, 5]:
        axis = axisY90(axis)
        cube = doY90(cube)
    if start in [1, 5]:
        axis = axisY90(axis)
        cube = doY90(cube)
    if start in [5]:
        axis = axisY90(axis)
        cube = doY90(cube)
    if start in [0, 3, 4, 7]:
        axis = axis120(axis)
        cube = do120(cube)
    if start in [4]:
        axis = axis120(axis)
        cube = do120(cube)
    if start in [0, 3, 4, 7]:
        axis = axisY90(axis)
        cube = doY90(cube)
    if start in [0, 3, 4]:
        axis = axisY90(axis)
        cube = doY90(cube)
    seq = reverse(explorer.lookup(serialiseState(cube)))
    return generateSequence(axis, seq)


for i in both:
    print(i, findSolution(deserialise(i)))

quit()

seed = VisualSolver.Solved

while explorer.listResults() is None:
    # -> if group isn't fully explored, run the explorer from the starting position
    depth = input(f"Group is incomplete! Depth of search ({DEFAULT})? ")
    elapsed = explorer.runSearch(seed, DEFAULT if depth=="" else int(depth))
    print(f"Search finished! Took {elapsed} seconds!")

"""
with open("generators", "r") as generators:
    for line in generators:
        generator = [line[0:3], line[4:7], line[8:11], line[12:15], line[16:19], line[20:23], line[24:27], line[28:31]]
        filepath = f"output/{line[:-1]}"
        explorer = GroupExplorer(filepath, serialiseState, allMoves)
        
        while explorer.listResults() is None:
            explorer.runSearch(generator, default=100)
        print(f"~~~~~~~~~~~~~~~~~~~~ Finished generator {line[:-1]}!")
quit()
"""

