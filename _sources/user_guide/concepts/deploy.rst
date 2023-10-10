.. _user_guide_deploy_index:

==========
deploy
==========

模型部署到云平台AI解译工具箱的客户端

授权
^^^^^^^^^^

当需要对云平台进行操作时，:ref:`reference_apis_deploy_index` module下面的函数，都需要先进行云平台的授权，获取用户个人token才可使用

.. literalinclude:: /snippets/auth.py
    :language: python

模型部署到云平台AI解译工具箱时，需要先创建项目空间 -> 模型版本，然后对模型pipeline进行部署

项目空间
^^^^^^^^^^

项目空间和模型任务一一对应，表示一类模型任务，并通过 ``project_id`` 进行索引

.. literalinclude:: /snippets/deploy.py
    :language: python
    :start-after: __create_project_start__
    :end-before: __create_project_end__


模型版本
^^^^^^^^^^

每个项目空间下面，可以有多个模型版本，模型版本命名规则请遵循 ``x.y.z``，xyz均为数字，如1.0.1，通过模型版本对模型进行管理，并通过 ``version_id`` 进行索引

.. literalinclude:: /snippets/deploy.py
    :language: python
    :start-after: __create_version_start__
    :end-before: __create_version_end__

部署
^^^^^^^^

请参考 场景案例/:ref:`examples_deploy_to_toolbox_index`
