
import time
import requests
import json
import logging

from load_text import load_text

logger = logging.getLogger("tests")
logging.basicConfig(level=logging.INFO, format='%(message)s')

class Tester:

    def __init__(self, engine):
        self.api = "http://localhost:8088/api/v1/"
        self.engine = engine

    def test_embeddings(self):

        logger.debug("** Embeddings test")

        input = {
            "text": "What is a cat?",
        }

        resp = requests.post(
            f"{self.api}embeddings",
            timeout=10,
            json=input,
        )

        resp = resp.json()

        if "error" in resp:
            raise RuntimeError("Embeddings: " + resp["error"])

        logger.debug("Got embeddings")

    def test_text_completion(self):

        logger.debug("** Text completion test")

        input = {
            "system": "Answer the question",
            "prompt": "What is 2 + 2?",
        }

        resp = requests.post(
            f"{self.api}text-completion",
            timeout=30,
            json=input,
        )

        resp = resp.json()

        if "error" in resp:
            raise RuntimeError("Text completion: " + resp["error"])

        logger.debug("Got text completion")

    def test_prompt(self):

        logger.debug("** Prompt test")

        input = {
            "id": "question",
            "variables": {
                "question": "What is 2 + 2?",
            }
        }

        resp = requests.post(
            f"{self.api}prompt",
            timeout=30,
            json=input,
        )

        resp = resp.json()

        if "error" in resp:
            raise RuntimeError("Prompt: " + resp["error"])

        logger.debug("Got prompt response")

    def test_graph_rag(self):

        logger.debug("** Graph RAG test")

        input = {
            "query": "What is a cat?",
        }

        resp = requests.post(
            f"{self.api}graph-rag",
            timeout=90,
            json=input,
        )

        resp = resp.json()

        if "error" in resp:
            raise RuntimeError("Prompt: " + resp["error"])

        logger.debug("Got graph RAG response")

    def test_load_text(self):

        logger.debug("** Load text")

        load_text(self.api, self.engine)

        logger.debug("Text loaded")

    def test_triples(self):

        logger.debug("** Query triples")

        timeout = 120
        until = time.time() + timeout
        
        input = {
            "limit": 10,
        }

        while time.time() < until:

            try:
                resp = requests.post(
                    f"{self.api}triples-query",
                    timeout=10,
                    json=input,
                )

                resp = resp.json()

                num = len(resp["response"])
                if num > 1:
                    logger.debug(f"Got {num} triples.")
                    return

            except:
                pass

            time.sleep(2)

        raise RuntimeError("Timeout waiting for triples")

    def run(self):

        logger.debug("=== TESTS BEGIN ===")

        self.test_load_text()

        self.test_text_completion()

        self.test_prompt()

        self.test_embeddings()

        logger.debug("Sleep for a bit")

        time.sleep(15)

        self.test_triples()

        self.test_graph_rag()

        logger.debug("=== TESTS COMPLETED ===")

        time.sleep(2)

