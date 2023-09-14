import pycuda.driver as cuda


def get_accelerator_type(device_id: int = 0):
    try:
        import pycuda.autoprimaryctx
    except ModuleNotFoundError:
        import pycuda.autoinit

    acc_type = cuda.Device(device_id).name()
    return acc_type.replace(" ", "")
