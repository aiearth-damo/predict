import fiona
from shapely.geometry import shape

from aiearth.predict.dataset.vector.vector_dataset import VectorDataset
from aiearth.predict.utils import Box


class ShapeFileVectorDataset(VectorDataset):
    def __init__(self, path):
        self.file_path = path

        self.features = None
        self.spatial_index = None

    def load_features(self):
        with fiona.open(self.file_path) as dataset:
            self.features = [feature for feature in dataset]

    def get_features(self):
        if self.features is None:
            self.load_features()

        return self.features

    def get_geoms(self):
        return [shape(feat.geometry) for feat in self.get_features()]

    def is_intersects_with_box(self, box: Box, need_index=True):
        if need_index:
            if self.spatial_index is None:
                from shapely.strtree import STRtree

                self.spatial_index = STRtree(self.get_geoms())

            box_polygon = box.to_polygon()
            indices = self.spatial_index.query(box_polygon)

            return any(
                [
                    box_polygon.intersects(self.spatial_index.geometries.take(idx))
                    for idx in indices
                ]
            )
        else:
            box_polygon = box.to_polygon()
            return any([box_polygon.intersects(poly) for poly in self.get_geoms()])
