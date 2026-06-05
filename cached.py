"""
    Stores a single value and allows for elegant update chaining between multiple Cached objects.

    Cached(function=None)
        Function is used to recompute the cached value when necessary. If not provided,
        UncomputableCacheError will be raised instead on that situation.
    .dependsOn(Cached) -> self
        Chains another Cached object so this Cached gets invalidated when the provided one changes
    .set(value)
        Updates the cached value, and triggers invalidation on all dependant Cached objects
    .update(value)
        Same as set, but modifies the value only if the cached one is different (uses __eq__ to compare)
    .reset()
        Invalidates this Cached object, and propagates invalidation on all dependant Cached objects
    .get() -> value
        Returns the current cached value. If currently invalidated, .set() is called internally with
        the result of the assigned function. If none assigned, UncomputableCacheError is rasied.
        
"""

class Cached:
    _Invalidated = object()  # Internal sentinel; SHOULD NOT BE USED BY USER!
    class UncomputableCacheError(Exception): pass

    def __init__(self, getter=None):
        self.modifying = []
        self.getter = getter
        self.value = Cached._Invalidated

    def dependsOn(self, c):
        if not isinstance(c, Cached): raise Exception("Cached objects can only depend on other cached objects!")
        c.modifying.append(self)
        return self

    def set(self, newvalue):
        self.value = newvalue
        for c in self.modifying:
            c.reset()
    def update(self, newvalue):
        if self.value == newvalue: return
        self.set(newvalue)

    def reset(self):
        if self.value is Cached._Invalidated: return  # already reset; do nothing
        self.set(Cached._Invalidated)

    def get(self):
        if self.value is Cached._Invalidated:  # recompute if currently invalidated
            if self.getter is None:
                raise Cached.UncomputableCacheError()
            self.set(self.getter())
        return self.value

