import json


def KiB(val):
    return val * 1 << 10


def MiB(val):
    return val * 1 << 20


def GiB(val):
    return val * 1 << 30


class ExecutionBundleOptions:
    def __init__(self, num_cpus=None, num_gpus=None, memory=None, batch_size=None):
        self.num_cpus = num_cpus
        self.num_gpus = num_gpus
        self.memory = memory
        self.batch_size = batch_size

    def to_dict(self):
        d = {}
        if self.num_cpus:
            d["num_cpus"] = self.num_cpus
        if self.num_gpus:
            if d.get("num_cpus", 0) != 0:
                raise RuntimeError(
                    "It is not allowed to specify both num_cpus and num_gpus"
                )
            d["num_gpus"] = self.num_gpus
        if self.memory:
            d["memory"] = self.memory
        if self.batch_size:
            d["batch_size"] = self.batch_size
        return d

    def __str__(self):
        return json.dumps(self.to_dict())

    def __repr__(self):
        return json.dumps(self.to_dict())
