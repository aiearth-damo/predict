.. _user_guide_operating_mode_index:

===============
运行模式
===============

AI Earth Predict 支持两种运行模式：本地运行、 `云平台AI解译工具箱 <https://engine-aiearth.aliyun.com/docs/page/guide?d=cc6bec#heading-0>`_ 

----------
本地运行
----------

``需提前设置好GPU显卡运行环境``

安装：

.. literalinclude:: /snippets/install.sh
    :language: shell

查看安装版本：

.. literalinclude:: /snippets/version.py
    :language: python

安装完成之后即可在本地进行相关业务逻辑代码编写

------------------
云平台AI解译工具箱
------------------

模型pipeline可部署到云平台工具箱模式下个人的 `AI解译工具 <https://engine-aiearth.aliyun.com/docs/page/guide?d=cc6bec#heading-0>`_ ，并通过云平台的 `工具箱模式 <https://engine-aiearth.aliyun.com/docs/page/guide?d=af4a0e#heading-0>`_ 从页面提交AI解译任务

.. image:: /images/toolbox.jpeg

模型部署请参考: `工具箱部署 <../examples/notebooks/deploy_to_toolbox.ipynb>`_ 
