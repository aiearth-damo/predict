class PadBounds:
    def __init__(self, top, bottom, left, right):
        self.top = top
        self.bottom = bottom
        self.left = left
        self.right = right

    def __str__(self):
        return f"[{self.top}, {self.bottom}, {self.left}, {self.right}]"

    def __repr__(self):
        return f"[{self.top}, {self.bottom}, {self.left}, {self.right}]"
