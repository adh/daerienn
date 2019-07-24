import base64
import os
import pickle
from flask import current_app

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
        self._init_transient_attrs()
        
    def _init_transient_attrs(self):
        for k, v in self.__transient_attrs__.items():
            if callable(v):
                v = v(self)
            self.__dict__[k] = v

    def __init__(self):
        self._init_transient_attrs()

        
