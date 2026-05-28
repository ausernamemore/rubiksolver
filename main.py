from puppet import *

"""
All physically possible (non-intersecting) arrangements of the pieces are split into:
    (note: I'll be using 'uts' to refer to 'up-to-symmetry' when counting orders.)

    -> 858 (286 uts) unsolvable states, which are temselves split into:
        - x16 of order 12 (4 uts) -> one face turns freely but only that face
        - x28 of order  9 (3 uts) -> one face turns, but one position is impossible
        - x20 of order  6 (2 uts) -> only a quarter back and forth turn possible
        - x20 of order  3 (1 uts) -> no moves possible; cube is completely stuck
            (These 74 groups I call "Simple" because they're boringly restrictive)

        -  x1 of order 138 (46 uts) -> the beast
            -> minimal generators:
                either CCC-udL-udB-fbB-rlL-fbL-MMM-rlB or CCC-rlB-udB-fbB-udL-rlL-MMM-fbL
        -  x2 of order  48 (16 uts) -> the two devils
            -> minimal generators:
                either udL-CCC-fbB-fbL-fbL-fbB-MMM-fbB or fbB-CCC-fbB-fbL-fbL-fbB-MMM-udL (devil A)
                either fbL-CCC-udB-udL-udL-udB-MMM-udB or udB-CCC-udB-udL-udL-udB-MMM-fbL (devil B)
            (These ones are rather interesting!)

    -> 13'174 (4'398 uts) solvable ones:
        *Symmetric elements:
            Because there are two unique pieces (MMM and CCC), the only symmetry the cube can have is through
        a diagonal (120°) that keeps both of those fixed. Then because L Blocks and Big Blocks are different,
        they have to be either all L Blocks around MMM and all Big Blocks around CCC (as in the solved state),
        or vice versa. Finally, because it must be rotationally symmetric, all L Blocks must be either clockwise
        or counterclockwise, and similarly with Big Blocks.
        That means there can only be: 2(from LB swap) * 3(L Blocks flip) * 3(Big Blocks flip) = 18.
        Out of those, 8 are self-intersecting (you can check this by hand!). These are the 10 possible ones, all solvable:
            CCC-rlB-udL-fbB-udB-fbL-MMM-rlL  (no flip)  <-- solved position
            CCC-rlL-udB-fbL-udL-fbB-MMM-rlB  (no flip, LB swapped)  <-- looks really cool btw, try it out!
            CCC-rlB-rlL-fbB-udB-udL-MMM-fbL  (L   flip clockwise)
            CCC-fbL-udB-udL-rlL-fbB-MMM-rlB  (L   flip clockwise, LB swapped)
            CCC-rlB-fbL-fbB-udB-rlL-MMM-udL  (L   flip countercw)
            CCC-udL-udB-rlL-fbL-fbB-MMM-rlB  (L   flip countercw, LB swapped)
            CCC-fbB-fbL-udB-rlB-rlL-MMM-udL  (L&B flip clockwise)
            CCC-fbL-fbB-udL-rlL-rlB-MMM-udB  (L&B flip clockwise, LB swapped)
            CCC-udB-rlL-rlB-fbB-udL-MMM-fbL  (L&B flip countercw)
            CCC-udL-rlB-rlL-fbL-udB-MMM-fbB  (L&B flip countercw, LB swapped)
        These 10 are the only elements that aren't counted thrice. This is because they
        remain the same when reoriented. All the other ones are counted thrice because
        X, Xo, and Xoo are all distinct internally (even though they look the same).
        This is why, in S, there are
            (13'174 - 10) / 3  +  10   =   4'398 uts
        For the unsolvable groups, just divide the raw count by 3, as they have no symmetric elements.
"""

    # Commet the line below out to run as command-line tool
VisualSolver()

explorer = GroupExplorer("dbs/puppet.db", serialiseState, allMoves)
    # You can download the fully-explored puppet.db or compute it yourself

seed = deserialise("MMM-udB-rlL-rlB-fbB-udL-CCC-fbL")

if explorer.listResults() is None:
    # -> if group isn't fully explored, run the explorer from the starting position
    print("Grpup is incomplete! Invoking a search...")
    explorer.runSearch(seed)

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

