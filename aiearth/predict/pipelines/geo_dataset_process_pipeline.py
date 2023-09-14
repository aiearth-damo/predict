import os
import sys
import ray
from typing import Any, Dict, List, Optional, Union, Callable, Tuple
from ray.data.preprocessors import Chain

from aiearth.predict.dataset import read_raster_dataset
from aiearth.predict.dataset.raster import (
    TiffFileRasterDataset,
    AIEGeoserverRasterDataset,
)
from aiearth.predict.dataset.vector import ShapeFileVectorDataset
from aiearth.predict.pipelines.pipeline import Pipeline
from aiearth.predict.pipelines.raster_dataset_protocol import (
    RasterDatasetProtocol,
    resolve_uri,
)
from aiearth.predict.schedule import ExecutionBundleOptions, GiB
from aiearth.predict.utils import (
    Box,
    get_chunk_windows,
    Polygonization,
    merge_shapes,
    merge_tiffs,
    TiffPredictWritter,
    remove_files,
)
from aiearth.predict.logging import root_logger as logger


class GeoDatasetProcessPipeline(Pipeline):
    def __init__(
        self, processors: List["Callable"], image_size: int = 1024, bound: int = 0
    ):
        self.processors = processors
        self.image_size = image_size
        self.bound = bound

    def __call__(
        self,
        uri: str,
        out_dir: str = ".",
        out_filename: str = None,
        temp_dir: str = None,
        extent: Union[Box, "shapely.geometry.polygon.Polygon"] = None,
        aoi_shape_file: str = None,
        sink_raster_count: int = 1,
        mask_zeros: bool = False,
        chunk_size: int = 20000,
        polygonization=True,
        merged=True,
        dissolve_merged_boundary=True,
        max_num_pending_write: int = 100,
        raster_dataset_open_args: dict = {},
        skip_errors: bool = False,
    ):
        try:
            dataset_protocol, uri = resolve_uri(uri)
            if dataset_protocol == RasterDatasetProtocol.local:
                raster_dataset = TiffFileRasterDataset(
                    uri, open_args=raster_dataset_open_args
                )
            elif dataset_protocol == RasterDatasetProtocol.geoserver:
                raster_dataset = AIEGeoserverRasterDataset(
                    uri, open_args=raster_dataset_open_args
                )

            if extent:
                raster_dataset.set_extent(extent)

            determined_extent = raster_dataset.get_extent()

            if out_filename is None:
                out_filename = "result"

            windows, indexes = get_chunk_windows(determined_extent, chunk_size)
            logger.info(f"------Job {out_filename} start-----")
            logger.info(
                f"width:{raster_dataset.get_extent_width()}, height:{raster_dataset.get_extent_height()}"
            )
            logger.info(f"indexes: {indexes}")
            logger.info("-------------------")

            mask_out_files = []
            shape_out_files = []
            for window, index in zip(windows, indexes):
                logger.info(f"predict {index}")
                raster_dataset.set_extent(window)

                if aoi_shape_file:
                    sfvd = ShapeFileVectorDataset(aoi_shape_file)
                    data = read_raster_dataset(
                        raster_dataset,
                        self.image_size,
                        self.bound,
                        aoi_vector_dataset=sfvd,
                    )
                else:
                    data = read_raster_dataset(
                        raster_dataset,
                        self.image_size,
                        self.bound,
                    )

                processor = Chain(*self.processors)
                data = processor.transform(data)

                if temp_dir is None:
                    temp_dir = out_dir
                mask_out_filename = f"{out_filename}-{index[0]}.{index[1]}.tif"
                shape_out_filename = f"{out_filename}-{index[0]}.{index[1]}.shp"
                result_refs = []
                # GDAL_CACHEMAX
                # https://docs.ray.io/en/latest/ray-core/api/doc/ray.actor.ActorClass.options.html?highlight=actor%20options#ray.actor.ActorClass.options
                mask_out_path = os.path.join(temp_dir, mask_out_filename)
                shp_out_path = os.path.join(temp_dir, shape_out_filename)
                writter = TiffPredictWritter.options(num_cpus=1).remote(
                    mask_out_path,
                    raster_dataset.get_extent_width(),
                    raster_dataset.get_extent_height(),
                    sink_raster_count,
                    raster_dataset.get_chip_dtype(),
                    raster_dataset.get_crs(),
                    raster_dataset.get_extent_transform(),
                )

                for batch in data.iterator().iter_batches(batch_size=1):
                    if len(result_refs) > max_num_pending_write:
                        ready_refs, result_refs = ray.wait(result_refs, num_returns=1)
                        ray.get(ready_refs)

                    result_refs.append(
                        writter.write.remote(
                            batch, "image", "meta", origin=raster_dataset.get_extent()
                        )
                    )
                ray.get(result_refs)
                ray.get(writter.finalize.remote())

                mask_out_files.append(mask_out_path)

                if polygonization:
                    logger.info("-----polygonization-----")
                    converters = Polygonization.remote()
                    result_ref = converters.tiff_to_shape_file.remote(
                        mask_out_path,
                        shp_out_path,
                        mask_zeros=mask_zeros,
                    )
                    ray.get(result_ref)

                    remove_files(mask_out_path)

                    shape_out_files.append(shp_out_path)

            if merged:
                logger.info("-----merged-----")
                if polygonization:
                    merged_shape_file = os.path.join(out_dir, f"{out_filename}.shp")
                    ray.get(
                        merge_shapes.remote(
                            shape_out_files,
                            merged_shape_file,
                            dissolve=dissolve_merged_boundary,
                        )
                    )

                    remove_files(
                        [
                            f"{os.path.splitext(shape_file)[0]}.*"
                            for shape_file in shape_out_files
                        ]
                    )
                else:
                    merged_mask_file = os.path.join(out_dir, f"{out_filename}.tif")
                    ray.get(merge_tiffs.remote(mask_out_files, merged_mask_file))

                    remove_files(mask_out_files)

        except Exception as e:
            logger.error(f"!!!failed!!!")
            import traceback

            ex_message = str(e).replace("\n", " ")
            logger.error(f"{ex_message}. \n{traceback.format_exc()}")

            if not skip_errors:
                sys.exit(-1)
