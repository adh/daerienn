import base64

class PersistentMetaclass(type):
    def __init__(self, *args):
        super().__init__(*args)
        ta = {}
        for superclass in reversed(self.__mro__):
            if hasattr(superclass, "__transient_attrs__"):
                ta.update(superclass.__transient_attrs__)
        if hasattr(self, "__transient_attrs__"):
            ta.update(self.__transient_attrs__)
        self.__transient_attrs__ = ta

class Persistent(object, metaclass=PersistentMetaclass):
    def __getstate__(self):
        return {k: v for k, v in self.__dict__.items()
                if k not in self.__transient_attrs__}
    
    def __setstate__(self, state):
        self.__dict__.update(state)
        for k, v in self.__transient_attrs__:
            if callablle(v):
                v = v()
            self.__dict__[k] = v

