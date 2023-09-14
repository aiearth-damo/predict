import rasterio

from aiearth.predict.dataset.raster.rasterio_dataset import RasterioDataset
from aiearth.predict.utils import Box


class TiffFileRasterDataset(RasterioDataset):
    def open(self, uri: str):
        with rasterio.Env(GDAL_CACHEMAX=200):
            return rasterio.open(uri)

    def __init__(
        self,
        uri,
        extent: Box = None,
        open_args={},
        read_args={"boundless": True, "fill_value": 0},
    ):
        super().__init__(uri, extent, open_args, read_args)

    def set_chip_data_info(self):
        prefetch_data = self.get_data_by_window_box(Box(0, 0, 1, 1))
        self.chip_dtype = prefetch_data.dtype
        self.chip_item_byte_size = prefetch_data.dtype.itemsize
        self.chip_num_channels = prefetch_data.shape[0]

    def read_chip_data(
        self,
        dataset: "rasterio.io.DatasetReader",
        window: "rasterio.windows.Window",
        **read_args,
    ):
        with rasterio.Env(GDAL_CACHEMAX=200):
            return dataset.read(window=window, **read_args)
