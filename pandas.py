class Series(list):
    def __init__(self, data):
        self.data = list(data)
    def __iter__(self):
        return iter(self.data)
    def __getitem__(self, idx):
        return self.data[idx]
    def __repr__(self):
        return f"Series({self.data})"
    def tolist(self):
        return list(self.data)
