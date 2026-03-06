from dataclasses import dataclass, asdict


@dataclass
class Entity:
    def to_dict(self):
        return {k: getattr(getattr(self, k), 'to_py_value', lambda : v)() for k, v in asdict(self).items()}
