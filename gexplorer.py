import shelve
import time

"""
    Code by u/Adventurous_Fill7251
    Make sure to check out my Puppet Cube guide, available on my Reddit profile ;)

    General purpose finite group explorer tool for non-closed groups (like that of bandaged puzzles).
    You provide a persistent storage path, a serialiser function to uniquely stringify states
    and a dictionary mapping move labels (ONE character only!) to functions between states.
    Move functions can return None if the move is not valid in the puzzle's context.

    Then the class provides a few functions for working and exploring that puzzle space.
"""

class GroupExplorer:
    def __init__(self, path, serialiser, allMoves):
        self.path = path
        self.serialiser = serialiser
        self.allMoves = allMoves

    def _explore(self, db, depthLeft, seq, state):  # returns TRUE if state is fully explored (all continuations are exhausted), FALSE if uncertain.
        if state is None: return True  # invalid state -> nothing to do

        e = self.serialiser(state)
        if (e not in db) or len(db[e][1]) > len(seq): db[e] = (len(seq), seq)

        if db[e][0] == -1 or db[e][1] != seq: return True  # state or sequence is exhausted -> no need to keep exploring (exhausted)
        if depthLeft <= db[e][0]-len(seq): return False  # not enoguh depth to explore further -> stop but keep path open (uncertain)

        exhausted = True
        for label, func in self.allMoves.items():
            if (not isinstance(label, str)) or len(label) != 1: raise Exception(f"Invalid label '{label}' for move!")
            exhausted = self._explore(db, depthLeft-1, seq+label, func(state)) and exhausted
        # once all recursive calls finished exploring, increase sequence's explored depth (or close it altogether if fully explored)
        db[e] = (-1 if exhausted else len(seq)+depthLeft, seq)
        # if all recurisve calls (continuations) were exhausted, this state is exhausted too
        return exhausted

    """
        Apply a sequence of moves (left-to-right) to a state
    """
    def apply(self, state, seq):
        for char in seq:
            if char not in self.allMoves: raise Exception(f"Unknown move '{char}' in sequence!")
            state = self.allMoves[char](state)
        return state

    """
        Call to perform a depth-limited search on the puzzle, providing an identity/base state as starting point
    """
    def runSearch(self, stateIdentity, depth):
        with shelve.open(self.path) as db:
            identity = self.serialiser(stateIdentity)
            if identity in db and db[identity][1] != "*":
                raise Exception(
                    "Warning: the starting position provided does not match the stored identity. Proceeding will corrupt the database!")
            s = time.time()
            self._explore(db, depth, "*", stateIdentity)
            return time.time() - s

    def getResults(self):
        with shelve.open(self.path) as db:
            return list(db.items())

    """
        Call to print full list of each explored state, its explored depth (-1 if fully explored), and the optimal sequence to reach it.
        Returns the order (size) of the group if fully explored, and None otherwise.
    """
    def listResults(self):
        with shelve.open(self.path) as db:
            openOnes = []
            maxSeq = ""
            for state, seq in db.items():
                if seq[0] != -1:
                    openOnes.append((state, seq))
                    continue
                if len(seq[1]) > len(maxSeq): maxSeq = seq[1]
                print(state, seq[0], seq[1])
            for state, seq in openOnes:
                print(state, seq[0], seq[1])
            total = len(db.items())
            if total > 0:
                p = int(100 - 100*len(openOnes)/total)
                print(f"~> found {total} distinct elements in the group, with {len(openOnes)} of them left to explore ({p}% explored).")
                if maxSeq:
                    print(f"~> The longest irreducible sequence known is {maxSeq}, with {len(maxSeq)} elements.")
                # Return order of group once it's complete
                if len(openOnes) == 0: return total

    """
        Call to query the database for an optimal path to a state; the state shall be serialised/stringified (not raw)
        Returns None if no sequence has been found to reach the queried state.
    """
    def lookup(self, e):
        with shelve.open(self.path) as db:
            if e in db: return db[e][1]

    """
        Call to query the database and check how deep a state has been explored (how many moves have been applied and registered to it).
        Returns -1 if every possible subsequence has been found already.
    """
    def checkDepth(self, e):
        with shelve.open(self.path) as db:
            if e in db: return db[e][0]
            else: return 0

