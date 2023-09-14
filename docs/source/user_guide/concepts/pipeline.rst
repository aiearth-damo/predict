.. _user_guide_pipeline_index:

==========
pipeline
==========

pipeline是对复杂任务流的更高层次的封装，每个pipeline表示一种任务类型

支持的pipeline任务类型请参考：:ref:`reference_apis_pipelines_index`

自定义pipeline
---------------

需要继承 ``Pipeline`` ，并实现 ``__init__``、 ``__call__`` 两个接口函数：

* __init__: pipeline初始化函数
* __call__: pipeline调用函数
