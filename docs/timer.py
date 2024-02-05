import time


class Timer:
    """Simple context manager that can store a sequence of 'laps'"""

    def __enter__(self):
        self.start = time.time()
        self.laps = []
        return self

    def __exit__(self, *args):
        pass

    @property
    def elapsed(self):
        return time.time() - self.start

    def lap(self):
        self.laps.append(self.elapsed)
        self.start += self.laps[-1]

    @property
    def average_lap(self):
        return sum(self.laps) / len(self.laps)


if __name__ == "__main__":
    # Usage example:
    with Timer() as t:
        assert t.elapsed < 0.1
        time.sleep(0.5)
        assert 0.4 < t.elapsed < 0.6
        t.lap()
        assert t.elapsed < 0.1
        assert len(t.laps) == 1
        t.lap()
        assert 0.2 < t.average_lap < 0.3
