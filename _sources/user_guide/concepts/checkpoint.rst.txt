.. _user_guide_checkpoint_index:

==========
checkpoint
==========

模型训练完成之后导出的格式统一称为 ``ModelCheckpoint``，定义了模型访问的通用接口，包括模型文件路径、模型参数以及模型其他附属文件（比如TensorRT转换的trt engine文件），ModelCheckpoint是 ``predictor`` 对象初始化的输入参数， ``predictor`` 需要通过 ``from_checkpoint`` 接口进行延迟实例化

checkpoint可以通过两种方式进行创建：from_local_path、from_remote_tag

from_local_path
-----------------

从本地模型模型路径进行创建：

* path: 本地模型路径
* image_size: 模型输入image大小
* bound: 预测边界大小，不计入最后结果
* use_quant: 是否使用quant量化模型
* attached_files: 模型
* kwargs 模型其他参数

from_remote_tag
-----------------

从云平台保存的模型，根据tag进行创建：

* tag: 云平台模型save时返回的模型tag，唯一
* model_cache_dir: 本地cache目录

checkpoint创建时会自动从云平台将模型下载到本地cache目录，并加载模型相关参数
