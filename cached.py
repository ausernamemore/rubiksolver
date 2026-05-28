"""
    Stores a single value and allows for elegant update chaining between multipe Cached objects.
    Caches can be invalidated by dependencies and set to None; keep in mind when reading raw .value
    data or use .readSafe() instead.
    
    modifies(Cached) -> self :: chain another Cached object so it gets invalidated when this Cached changes
    isInvalid() -> boolean :: returns whether this Cached is invalid or not
    readSafe() -> value :: returns the value of this Cached if it's valid, throws InvalidCacheError otherwise
    update(value=None) -> None :: updates the value of this Cached only if it's different than the current one
        -> if value is None (or not passed), invalidates this Cached.
    force(value) -> None :: updates the value of this Cached regardless whether it has changed or not
"""

class Cached:
    class InvalidatedCacheError(Exception): pass
    def __init__(self, value=None):
        self.modifying = []
        self.value = value
    def modifies(self, c):
        if not isinstance(c, Cached): raise Exception("Cached objects can only modify other cached objects!")
        self.modifying.append(c)
        return self
    def isInvalid(self):
        return self.value is None
    def readSafe(self):
        if self.value is None:
            raise Cached.InvalidCacheError()
        return self.value
    def update(self, newvalue=None):
        if self.value != newvalue:
            self.force(newvalue)
    def force(self, newvalue):
        self.value = newvalue
        for c in self.modifying: c.update()

