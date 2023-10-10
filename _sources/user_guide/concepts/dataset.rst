.. _user_guide_dataset_index:

==========
dataset
==========

dataset是AI Earth Predict对数据源的数据读取抽象层，分为栅格 ``raster`` 和矢量数据 ``vector``，请参考api :ref:`reference_apis_dataset_index` 


自定义数据源
------------

对栅格数据rasterio的读取进行了抽象 ``RasterioDataset`` ，兼容rasterio接口的数据源需要继承 ``RasterioDataset`` ，实现 ``open``、 ``set_chip_data_info`` 、 ``read_chip_data`` 接口即可完成自定义的栅格数据源接入：

* open: 打开栅格影像句柄，返回rasterio的DatasetReader
* set_chip_data_info: 设置影像的属性信息，chip_dtype影像波段数据类型/chip_item_byte_size单个像素存储占用byte大小/chip_num_channels影像波段数
* read_chip_data: 根据window对影像数据进行读取
