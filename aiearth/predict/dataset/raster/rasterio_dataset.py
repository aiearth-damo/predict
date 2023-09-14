import math
import rasterio
from typing import Any, Dict, List, Optional, Union, Callable, Tuple

from aiearth.predict.dataset.raster.raster_dataset import RasterDataset
from aiearth.predict.utils import Box

from aiearth.predict.logging import root_logger as logger


class RasterioDataset(RasterDataset):
    def __init__(self, uri, extent: Box = None, open_args={}, read_args={}):
        with self.open(uri, **open_args) as dataset:
            self.crs = dataset.crs
            if self.crs is None:
                self.crs = rasterio.crs.CRS.from_epsg(4326)

            self.transform = dataset.transform
            self.width = dataset.width
            self.height = dataset.height
            self.count = dataset.count
            self.dtypes = dataset.dtypes

            if extent is None:
                self.extent = self.round_extent(Box(0, 0, self.width, self.height))
            else:
                self.extent = self.round_extent(extent)

            self.read_band_order = [i for i in range(dataset.count)]

        self.uri = uri
        self.open_args = open_args
        self.read_args = read_args

        self.chip_dtype = None
        self.chip_item_byte_size = None
        self.chip_num_channels = None

    def open(self, uri, **kwargs):
        raise NotImplementedError

    def set_extent_width(self, width):
        self.extent.set_width(width)

    def set_extent_height(self, height):
        self.extent.set_height(height)

    def set_extent(self, extent: Union[Box, "shapely.geometry.polygon.Polygon"]):
        from shapely.geometry.polygon import Polygon

        if isinstance(extent, Box):
            self.set_extent_from_box(extent)
        elif isinstance(extent, Polygon):
            self.set_extent_from_polygon(extent)

    def set_extent_from_box(self, box: Box):
        self.extent = self.round_extent(box)

    def set_extent_from_polygon(
        self, polygon: "shapely.geometry.polygon.Polygon", transform=None
    ):
        if transform is None:
            transform = self.transform
        self.extent = self.round_extent(
            Box.from_window(rasterio.windows.from_bounds(*polygon.bounds, transform))
        )

    def set_read_band_order(self, order: List[int]):
        self.read_band_order = order

    def set_chip_data_info(self):
        # self.chip_dtype =
        # self.chip_item_byte_size =
        # self.chip_num_channels =
        raise NotImplementedError

    def get_chip_dtype(self):
        if self.chip_dtype is None:
            self.set_chip_data_info()
        if self.chip_dtype is None:
            raise RuntimeError(
                "chip_dtype is None. please override set by set_chip_data_info"
            )
        return self.chip_dtype

    def get_chip_item_byte_size(self):
        if self.chip_item_byte_size is None:
            self.set_chip_data_info()
        if self.chip_item_byte_size is None:
            raise RuntimeError(
                "chip_item_byte_size is None. please override set by set_chip_data_info"
            )
        return self.chip_item_byte_size

    def get_chip_num_channels(self):
        if self.chip_num_channels is None:
            self.set_chip_data_info()
        if self.chip_num_channels is None:
            raise RuntimeError(
                "chip_num_channels is None. please override set by set_chip_data_info"
            )
        return self.chip_num_channels

    def get_extent_width(self):
        return self.extent.get_width()

    def get_extent_height(self):
        return self.extent.get_height()

    def get_crs(self):
        return self.crs

    def get_extent_transform(self):
        with self.open(self.uri, **self.open_args) as dataset:
            return dataset.window_transform(
                rasterio.windows.Window(*self.extent.to_xywh())
            )

    def get_extent(self):
        return self.extent

    def round_extent(self, extent: Box):
        return Box(
            math.ceil(extent.xmin),
            math.ceil(extent.ymin),
            math.floor(extent.xmax),
            math.floor(extent.ymax),
        )

    def read_chip_data(
        self,
        dataset: "rasterio.io.DatasetReader",
        window: "rasterio.windows.Window",
        **read_args,
    ):
        raise NotImplementedError

    def get_data_by_window_box(self, boxes: Union[Box, List[Box]]):
        if isinstance(boxes, Box):
            with self.open(self.uri, **self.open_args) as dataset:
                return self.read_chip_data(dataset, boxes.to_window(), **self.read_args)

        with self.open(self.uri, **self.open_args) as dataset:
            return [
                self.read_chip_data(dataset, box.to_window(), **self.read_args)
                for box in boxes
            ]

    def get_data_by_bounding_box(self, boxes: Union[Box, List[Box]]):
        if isinstance(boxes, Box):
            with self.open(self.uri, **self.open_args) as dataset:
                return self.read_chip_data(
                    dataset,
                    rasterio.windows.from_bounds(*boxes.to_bounds(), self.transform),
                    **self.read_args,
                )

        with self.open(self.uri, **self.open_args) as dataset:
            return [
                self.read_chip_data(
                    dataset,
                    rasterio.windows.from_bounds(*boxes.to_bounds(), self.transform),
                    **self.read_args,
                )
                for box in boxes
            ]

    def calc_window_box_bounds(self, box: Box):
        w = rasterio.windows.Window(*box.to_xywh())
        return Box.from_bounds(rasterio.windows.bounds(w, self.transform))

    def calc_window_bounds(self, w: "rasterio.windows.Window"):
        return Box.from_bounds(rasterio.windows.bounds(w, self.transform))
