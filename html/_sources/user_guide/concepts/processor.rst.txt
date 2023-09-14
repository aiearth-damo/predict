.. _user_guide_processor_index:

==========
processor
==========

processor是pipeline任务流中的前后处理和操作转换算子

支持的processor请参考：:ref:`reference_apis_processors_index`

自定义processor
---------------

需要继承 ``Processor`` ，并实现 ``pandas_udf`` 接口：

* pandas_udf: 算子处理函数，输入和输出类型都为 ``pandas.DataFrame``
