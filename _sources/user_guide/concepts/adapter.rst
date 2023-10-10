.. _user_guide_adapter_index:

========
adapter
========

模型pipeline部署到云平台AI解译工具箱时，需要对工具箱的参数进行适配，adapter提供了工具箱模式的输入参数解析接口，将输入参数解析为 ``InputArgs`` 对象

.. literalinclude:: /snippets/parse_toolbox_args.py
    :language: python

InputArgs
    * working_dir: 运行时工作目录
    * temp_dir: 运行结果临时目录
    * result_dir: 运行结果输出目录
    * src: 输入文件
    * out_filename: 输出结果文件名

只有运行模式为 ``云平台AI解译工具箱`` 时才需要从adapter适配器解析获取输入参数
