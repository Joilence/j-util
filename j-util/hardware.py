""" Try to use available libraries to get hardware information. """
import multiprocessing
import platform


def get_ram_info() -> str:
    """ get RAM information """
    try:
        import psutil
        ram = psutil.virtual_memory()
        return (f"Total RAM: {round(ram.total / 1024.0 ** 3)} GB\n"
                f"Available RAM: {round(ram.available / 1024.0 ** 3)} GB")
    except ImportError:
        return 'psutil is not available. Cannot retrieve RAM information.'


def get_cpu_info() -> str:
    """ get CPU information """
    return (f"CPU Model: {platform.processor()}\n"
            f"CPU Cores: {multiprocessing.cpu_count()}")


def get_gpu_info_torch() -> str:
    """ try to get GPU information from torch """
    try:
        import torch
    except ImportError:
        return ""
    if torch.cuda.is_available():
        return '\n'.join(
            f"GPU {i}: {torch.cuda.get_device_name(i)}, "
            f"Memory: {torch.cuda.get_device_properties(i).total_memory / 1024 ** 3:.2f}GB"
            for i in range(torch.cuda.device_count())
        )
    else:
        return "PyTorch is installed but no GPUs or CUDA are available."


def get_gpu_info_tf() -> str:
    """ try to get GPU information from tensorflow """
    try:
        import tensorflow as tf
    except ImportError:
        return ""
    if gpus := tf.config.list_physical_devices('GPU'):
        return '\n'.join(
            f"GPU {i}: {gpu.name}, Memory: {gpu.memory_limit / 1024 ** 3:.2f}GB"
            for i, gpu in enumerate(gpus)
        )
    else:
        return "Tensorflow is installed but no GPUs are available."


def get_gpu_info_GPUtil() -> str:
    """ try to get GPU information from GPUtil """
    try:
        import GPUtil
    except ImportError:
        return ""
    if gpus := GPUtil.getGPUs():
        return '\n'.join(
            f"GPU {i}: {gpu.name}, Memory: {gpu.memoryTotal}MB"
            for i, gpu in enumerate(gpus)
        )
    else:
        return "GPUtil is installed but no GPUs are available."


def get_gpu_info_gpustat() -> str:
    """ try to get GPU information from gpustat """
    try:
        from gpustat import GPUStatCollection
    except ImportError:
        return ""
    if gpus := GPUStatCollection.new_query():
        return '\n'.join(
            f"GPU {i}: {gpu.name}, Memory: {gpu.memory_total}MB"
            for i, gpu in enumerate(gpus)
        )
    else:
        return "gpustat is installed but no GPUs are available."


def get_gpu_info() -> str:
    """ try to get GPU information from all available libraries """
    result = None
    result = result or get_gpu_info_torch()
    result = result or get_gpu_info_tf()
    result = result or get_gpu_info_GPUtil()
    result = result or get_gpu_info_gpustat()
    return result or 'No libraries available to retrieve GPU information.'


def get_machine_specs() -> str:
    """ get machine specs """
    return (
        f"Platform: {platform.platform()}\n"
        f"{get_cpu_info()}\n"
        f"{get_ram_info()}\n"
        f"{get_gpu_info()}"
    )
