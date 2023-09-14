.. _user_guide_predictor_index:

==========
predictor
==========

predictor是执行推理的包装类，需要从Checkpoint加载模型来进行实例化

支持的predictor请参考：:ref:`reference_apis_predictors_index`

自定义predictor
---------------

需要继承 ``Predictor`` ，并实现 ``__init__`` 、 ``_predict_numpy`` 接口：

* __init__: 从checkpoint加载模型对predictor进行延迟实例化
* _predict_numpy: 推理调用入口，返回类型 ``pandas.DataFrame``
  
