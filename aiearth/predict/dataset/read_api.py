from ray.data.read_api import read_datasource
from typing import Any, Dict, List, Optional, Union, Callable, Tuple

from aiearth.predict.dataset.raster import RasterDataset
from aiearth.predict.dataset.vector import VectorDataset
from aiearth.predict.dataset.datasource.raster_datasource import RasterDatasource


def read_raster_dataset(
    raster_dataset: RasterDataset,
    image_size,
    bound,
    block_size=1,
    block_memory_buffer=100,
    aoi_vector_dataset: VectorDataset = None,
    read_block_image_column="image",
    read_block_box_column="box",
    read_block_pad_bounds_column="pad_bounds",
    size_bytes_growth_factor=1.25,
    ray_remote_args: Dict[str, Any] = None,
    **read_args,
):
    return read_datasource(
        RasterDatasource(),
        raster_dataset=raster_dataset,
        image_size=image_size,
        bound=bound,
        block_size=block_size,
        block_memory_buffer=block_memory_buffer,
        aoi_vector_dataset=aoi_vector_dataset,
        read_block_image_column=read_block_image_column,
        read_block_box_column=read_block_box_column,
        read_block_pad_bounds_column=read_block_pad_bounds_column,
        size_bytes_growth_factor=size_bytes_growth_factor,
        ray_remote_args=ray_remote_args,
        **read_args,
    )
