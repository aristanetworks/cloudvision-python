import sys, os
# Required otherwise the generated files get failed dependencies
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
from router_pb2 import *
from router_pb2_grpc import *
from notification_pb2 import *
from notification_pb2_grpc import *
from sharding_pb2 import *
from sharding_pb2_grpc import *

