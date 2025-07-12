"""ItemStats module for Smite Divine Arsenal."""


class ItemStats:
    """Class to handle item stats with dictionary-like behavior."""

    def __init__(self, stats_dict):
        self._stats = {k: float(v) for k, v in stats_dict.items()}

    def __getattr__(self, name):
        return self._stats.get(name, 0.0)

    def __getitem__(self, key):
        return self._stats.get(key, 0.0)

    def get(self, key, default=0.0):
        return self._stats.get(key, default)

    def items(self):
        return self._stats.items()

    def __len__(self):
        return len(self._stats)

    def __gt__(self, other):
        if isinstance(other, (int, float)):
            return any(value > other for value in self._stats.values())
        return False

    def __float__(self):
        return sum(self._stats.values())

    def to_dict(self):
        return dict(self._stats)
