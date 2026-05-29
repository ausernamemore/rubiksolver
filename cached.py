"""
    Stores a single value and allows for elegant update chaining between multipe Cached objects.
    Creation must receive a default value; when reset (a dependency gets updated), this value is used.
    When updating the value, all dependants are set to their defaults.

    .value :: current stored value of this Cached
    dependsOn(Cached) -> self :: chain another Cached object so this Cached gets reset when it changes
    reset() :: updates the value of this Cached to its default and resets its dependants
    set(value) :: updates the value of this Cached and resets its dependants
    update(value) :: same as .set, but checks if the passed value equals (==) current one to avoid unnecessary updates
        -> Note: relies on comparing (__eq__) the values.
"""

class Cached:
    def __init__(self, default=None):
        self.modifying = []
        self.value = self.default = default

    def dependsOn(self, c):
        if not isinstance(c, Cached): raise Exception("Cached objects can only depend on other cached objects!")
        c.modifying.append(self)
        return self

    def reset(self):
        self.set(self.default)
    def set(self, newvalue):
        if newvalue is self.value: return  # same object -> do nothing
        self.value = newvalue
        for c in self.modifying:
            c.reset()  # reset dependants

    def update(self, newvalue):
        if self.value != newvalue:
            self.set(newvalue)

