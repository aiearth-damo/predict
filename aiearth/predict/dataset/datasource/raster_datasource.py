from ray.data.datasource.datasource import Datasource, Reader, ReadTask

from aiearth.predict.dataset.datasource.raster_dataset_reader import RasterDatasetReader


class RasterDatasource(Datasource):
    def create_reader(
        self,
        raster_dataset,
        image_size,
        bound,
        block_size,
        block_memory_buffer,
        aoi_vector_dataset,
        read_block_image_column,
        read_block_box_column,
        read_block_pad_bounds_column,
        size_bytes_growth_factor,
        **read_args,
    ) -> "Reader[T]":
        return RasterDatasetReader(
            raster_dataset,
            image_size,
            bound,
            block_size,
            block_memory_buffer,
            aoi_vector_dataset,
            read_block_image_column,
            read_block_box_column,
            read_block_pad_bounds_column,
            size_bytes_growth_factor,
        )
