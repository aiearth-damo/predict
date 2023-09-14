import rasterio
import numpy as np

from aiearth.predict.dataset.raster.rasterio_dataset import RasterioDataset
from aiearth.predict.logging import root_logger as logger


class AIEGeoserverRasterDataset(RasterioDataset):
    def open(
        self,
        uri: str,
        data_format: str = "image/jpeg",
        tile_size: int = 256,
        max_level: int = 18,
        up_sample_level_limit: int = 16,
    ):
        import urllib

        params = {
            "service": "WMS",
            "version": "1.1.1",
            "request": "GetMap",
            "layers": "google_map_tile",
            "tileSize": tile_size,
            "minResolution": 360 / tile_size / pow(2, max_level),
            "format": data_format,
        }
        return rasterio.open("WMS:" + uri + urllib.parse.urlencode(params))

    def set_chip_data_info(self):
        self.chip_dtype = np.uint8
        self.chip_item_byte_size = 1
        self.chip_num_channels = 3

    def read_chip_data(self, dataset, window, **read_args):
        import time

        start = time.time()
        image = dataset.read(window=window, **read_args)
        end = time.time()

        if image.size == 0:
            raise RuntimeError(
                f"window: {window}, bounds: {self.calc_window_bounds(window)}"
            )

        logger.info(f"read_chip_data time:{end-start}, window:{window}")
        return image
