"""
    Stores a single value and allows for elegant update chaining between multipe Cached objects.
    Caches can be invalidated by dependencies and set to None; keep in mind when reading raw .value
    data or use .readSafe() instead.
    
    dependsOn(Cached) -> self :: chain another Cached object so this Cached gets invalidated when it changes
    readSafe() -> value :: returns the value of this Cached if it's valid, throws InvalidCacheError otherwise
    set(value=None) -> None :: updates the value of this Cached regardless whether it has changed or not
        -> Note: call without arguments to invalidate this Cached.
    update(value) -> None :: same as set(), but checks if new value equals (==) current one to avoid unnecessary updates
        -> Note: relies on comparing (__eq__) the values.
"""

class Cached:
    class InvalidatedCacheError(Exception): pass

    def __init__(self, value=None):
        self.modifying = []
        self.value = value

    def dependsOn(self, c):
        if not isinstance(c, Cached): raise Exception("Cached objects can only depend on other cached objects!")
        c.modifying.append(self)
        return self

    def readSafe(self):
        if self.value is None:
            raise Cached.InvalidCacheError()
        return self.value

    def set(self, newvalue=None):
        if newvalue is None and self.value is None:
            return  # cache already invalidated -> do nothing
        self.value = newvalue
        for c in self.modifying:
            c.set()  # invalidate dependants

    def update(self, newvalue):
        if self.value != newvalue:
            self.set(newvalue)

