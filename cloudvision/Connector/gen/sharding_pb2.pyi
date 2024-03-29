"""
@generated by mypy-protobuf.  Do not edit manually!
isort:skip_file
"""
import builtins
import google.protobuf.descriptor
import google.protobuf.internal.enum_type_wrapper
import google.protobuf.message
import typing
import typing_extensions

DESCRIPTOR: google.protobuf.descriptor.FileDescriptor

class _ShardingFunction:
    ValueType = typing.NewType('ValueType', builtins.int)
    V: typing_extensions.TypeAlias = ValueType
class _ShardingFunctionEnumTypeWrapper(google.protobuf.internal.enum_type_wrapper._EnumTypeWrapper[_ShardingFunction.ValueType], builtins.type):
    DESCRIPTOR: google.protobuf.descriptor.EnumDescriptor
    DATASETANDPATH: _ShardingFunction.ValueType  # 0
    """DATASETANDPATH shards by the association of dataset and path"""

    DATASET: _ShardingFunction.ValueType  # 1
    """DATASET shards by dataset"""

    PATH: _ShardingFunction.ValueType  # 2
    """PATH shards by path"""

class ShardingFunction(_ShardingFunction, metaclass=_ShardingFunctionEnumTypeWrapper):
    pass

DATASETANDPATH: ShardingFunction.ValueType  # 0
"""DATASETANDPATH shards by the association of dataset and path"""

DATASET: ShardingFunction.ValueType  # 1
"""DATASET shards by dataset"""

PATH: ShardingFunction.ValueType  # 2
"""PATH shards by path"""

global___ShardingFunction = ShardingFunction


class Sharding(google.protobuf.message.Message):
    """Sharding contains the information for horizontal scaling of subscriptions and get requests.
    Multitenancy, i.e., matching notifications across multiple parent datasets, is enabled by setting
    numParentShards >= 1. Dataset/Path sharding must be configured orthogonally to Parent sharding.
    This makes it possible to map an entire org to a single client instance. Examples:
      {numShards = 1, numParentShards = M} => distributes notifs among M shards preserving org grouping
      {numShards = N, numParentShards = 1} => distributes among N shards without preserving org grouping
      {numShards = N, numParentShards = M} => means that there will be N*M shards in total where the
         notification from a single org will be sharded into N bins based on the ShardingFunction.
    """
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    SHARD_FIELD_NUMBER: builtins.int
    NUMSHARDS_FIELD_NUMBER: builtins.int
    SHARDINGFUNC_FIELD_NUMBER: builtins.int
    PARENTSHARD_FIELD_NUMBER: builtins.int
    NUMPARENTSHARDS_FIELD_NUMBER: builtins.int
    shard: builtins.int
    """shard is the unique ID of the client instance for horizontal scaling"""

    numShards: builtins.int
    """numShards is the number of instances of the client for horizontal scaling"""

    shardingFunc: global___ShardingFunction.ValueType
    """shardingFunc defines which sharding function to use for horizontal scaling"""

    parentShard: builtins.int
    """parentShard is the unique ID of the client instance if multitenant is enabled"""

    numParentShards: builtins.int
    """numParentShards is the number of client instances for parent dataset sharding"""

    def __init__(self,
        *,
        shard: builtins.int = ...,
        numShards: builtins.int = ...,
        shardingFunc: global___ShardingFunction.ValueType = ...,
        parentShard: builtins.int = ...,
        numParentShards: builtins.int = ...,
        ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["numParentShards",b"numParentShards","numShards",b"numShards","parentShard",b"parentShard","shard",b"shard","shardingFunc",b"shardingFunc"]) -> None: ...
global___Sharding = Sharding
