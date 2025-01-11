
import logging
logger = logging.getLogger("targets")
logging.basicConfig(level=logging.INFO, format='%(message)s')

def get_targets():
    for graph in [ "cassandra", "memgraph", "falkordb", "neo4j" ]:
        for vector in [ "qdrant", "milvus" ]:
            yield {
                "graph": "triple-store-" + graph,
                "vector": "vector-store-" + vector,
            }

