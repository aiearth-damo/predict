class Box:
    def __init__(self, xmin, ymin, xmax, ymax):
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmax
        self.ymax = ymax

    @classmethod
    def from_bounds(cls, bounds):
        return cls(bounds[0], bounds[1], bounds[2], bounds[3])

    @classmethod
    def from_xywh(cls, x, y, width, height):
        return cls(x, y, x + width, y + height)

    @classmethod
    def from_window(cls, window: "rasterio.windows.Window"):
        return cls(
            window.col_off,
            window.row_off,
            window.col_off + window.width,
            window.row_off + window.height,
        )

    def translate(self, dx: int, dy: int):
        return Box(self.xmin + dx, self.ymin + dy, self.xmax + dx, self.ymax + dy)

    def subtract_origin(self, extent: "Box"):
        return self.translate(dx=-extent.xmin, dy=-extent.ymin)

    def __str__(self):
        return f"[{self.xmin}, {self.ymin}, {self.xmax}, {self.ymax}]"

    def __repr__(self):
        return f"[{self.xmin}, {self.ymin}, {self.xmax}, {self.ymax}]"

    def get_height(self):
        return self.ymax - self.ymin

    def get_width(self):
        return self.xmax - self.xmin

    def set_width(self, width):
        self.xmax = self.xmin + width

    def set_height(self, height):
        self.ymax = self.ymin + height

    def to_polygon(self):
        from shapely.geometry.polygon import Polygon

        return Polygon.from_bounds(
            xmin=self.xmin, ymin=self.ymin, xmax=self.xmax, ymax=self.ymax
        )

    def to_window(self):
        return ((self.ymin, self.ymax), (self.xmin, self.xmax))

    def to_xywh(self):
        return (self.xmin, self.ymin, self.xmax - self.xmin, self.ymax - self.ymin)

    def to_bounds(self):
        return (self.xmin, self.ymin, self.xmax, self.ymax)
