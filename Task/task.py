class MapReducer:

    def __init__(self, text):
        self.text = text
        self.dict = {}

    def map_run(self):
        words = self.text.split()

        for w in words:
            self.emit(w)

    def emit(self, w):
        if self.dict.get(w):
            self.dict[w] += 1
        else:
            self.dict[w] = 1

    def reduce(self):
        return self.dict
