from difflib import Differ as DifferBase

class Differ(DifferBase):
    def diff(self, a, b):
        raise NotImplementedError