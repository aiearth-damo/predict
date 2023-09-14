import math
import pandas as pd
from typing import Any, Dict, List, Optional, Union, Callable, Tuple
from ray.data.block import Block, BlockMetadata
from ray.data.datasource.datasource import Datasource, Reader, ReadTask

from aiearth.predict.dataset.raster import RasterDataset
from aiearth.predict.dataset.vector import VectorDataset
from aiearth.predict.utils import Box, PadBounds


class RasterDatasetReader(Reader):
    def __init__(
        self,
        raster_dataset: RasterDataset,
        image_size,
        bound,
        block_size,
        block_memory_buffer,  # MiB
        aoi_vector_dataset: VectorDataset,
        read_block_image_column,
        read_block_box_column,
        read_block_pad_bounds_column,
        size_bytes_growth_factor,
    ):
        self.raster_dataset = raster_dataset
        self.image_size = image_size
        self.bound = bound
        self.block_size = block_size
        self.aoi_vector_dataset = aoi_vector_dataset
        self.read_block_image_column = read_block_image_column
        self.read_block_box_column = read_block_box_column
        self.read_block_pad_bounds_column = read_block_pad_bounds_column
        self.size_bytes_growth_factor = size_bytes_growth_factor

        self.chip_size_bytes = (
            self.image_size
            * self.image_size
            * self.raster_dataset.get_chip_num_channels()
            * self.raster_dataset.get_chip_item_byte_size()
            * self.size_bytes_growth_factor
        )

        if self.block_size is None:
            self.block_size = math.floor(
                block_memory_buffer * 1024 * 1024 / self.chip_size_bytes
            )

    def _get_sliding_windows(self):
        extent = self.raster_dataset.get_extent()
        valid_size = self.image_size - self.bound * 2

        image_width = self.image_size
        image_height = self.image_size

        xmin, ymin, xmax, ymax = (
            extent.xmin,
            extent.ymin,
            extent.xmax,
            extent.ymax,
        )

        windows = []
        bounds = []
        for y in range(ymin - self.bound, ymax, valid_size):
            for x in range(xmin - self.bound, xmax, valid_size):
                right_x_bound = max(self.bound, x + image_width - extent.xmax)
                bottom_y_bound = max(self.bound, y + image_height - extent.ymax)

                box = Box.from_xywh(x, y, image_width, image_height)
                if self.aoi_vector_dataset is not None:
                    p_bounds = self.raster_dataset.calc_window_box_bounds(box)
                    if not self.aoi_vector_dataset.is_intersects_with_box(p_bounds):
                        continue

                pad_bounds = PadBounds(
                    self.bound, bottom_y_bound, self.bound, right_x_bound
                )
                windows.append(box)
                bounds.append(pad_bounds)

        return (windows, bounds)

    def _read_blocks(self, boxes, pad_bounds) -> List[Block]:
        images = self.raster_dataset.get_data_by_window_box(boxes)
        block = pd.DataFrame(
            {
                self.read_block_image_column: images,
                self.read_block_box_column: boxes,
                self.read_block_pad_bounds_column: pad_bounds,
            }
        )
        return [block]

    def _get_read_tasks(self, parallelism):
        read_tasks = []

        boxes = []
        pad_bounds = []

        windows, bounds = self._get_sliding_windows()
        # n = len(windows)
        # block_size = max(1, n // parallelism)
        block_size = self.block_size

        for window, bound in zip(windows, bounds):
            boxes.append(window)
            pad_bounds.append(bound)

            if len(boxes) == block_size:
                blocks_meta = BlockMetadata(
                    num_rows=block_size,
                    size_bytes=block_size * self.chip_size_bytes,
                    schema=None,
                    input_files=None,
                    exec_stats=None,
                )

                read_task = ReadTask(
                    lambda boxes=boxes, pad_bounds=pad_bounds: self._read_blocks(
                        boxes, pad_bounds
                    ),
                    blocks_meta,
                )
                read_tasks.append(read_task)

                boxes = []
                pad_bounds = []

        if len(boxes) > 0:
            blocks_meta = BlockMetadata(
                num_rows=len(boxes),
                size_bytes=len(boxes) * self.chip_size_bytes,
                schema=None,
                input_files=None,
                exec_stats=None,
            )
            read_task = ReadTask(
                lambda boxes=boxes, pad_bounds=pad_bounds: self._read_blocks(
                    boxes, pad_bounds
                ),
                blocks_meta,
            )
            read_tasks.append(read_task)

        return read_tasks

    def estimate_inmemory_data_size(self) -> Optional[int]:
        return None

    def get_read_tasks(self, parallelism: int) -> List[ReadTask]:
        return self._get_read_tasks(parallelism)
