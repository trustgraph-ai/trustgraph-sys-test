
import logging
logger = logging.getLogger("targets")
logging.basicConfig(level=logging.INFO, format='%(message)s')

def get_targets():
    for graph in [ "cassandra", "memgraph", "falkordb" ]:
        for vector in [ "qdrant", "milvus" ]:
            yield {
                "graph": graph, "vector": vector,
            }

            
