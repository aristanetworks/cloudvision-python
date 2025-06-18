from cloudvision.Connector.grpc_client import PooledGRPCClient, create_query
from parser import base
from threading import Thread
import logging
import time

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)


def main(apiserverAddr, token=None, cert=None, key=None, ca=None):
    streams = 1500
    pathElts = [
        "/mytestpath",
    ]
    query = [
        create_query([(pathElts, ['testKey'])], "testdataset")
    ]
    client = PooledGRPCClient(apiserverAddr, token=token, certs=cert, key=key, ca=ca)

    for id in range(0, streams):
        def subscribe(id=id):
            i = 0
            stream = client.subscribe(query)
            for batch in stream:
                for notif in batch["notifications"]:
                    logging.info(f"{i} | {id} | {notif}")
                i += 1
        Thread(target=subscribe, daemon=False).start()
    return 0


if __name__ == "__main__":
    args = base.parse_args()
    exit(main(args.apiserver, ca=args.caFile,
              cert=args.certFile, key=args.keyFile, token=args.tokenFile))
