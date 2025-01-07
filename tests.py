
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

        print("** Embeddings test")

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

        print("Got embeddings")

    def test_text_completion(self):

        print("** Text completion test")

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

        print("Got text completion")

    def test_prompt(self):

        print("** Prompt test")

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

        print("Got prompt response")

    def test_graph_rag(self):

        print("** Graph RAG test")

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

        print("Got graph RAG response")

    def test_load_text(self):

        print("** Load text")

        load_text(self.api, self.engine)

        print("Text loaded")

    def test_triples(self):

        print("** Query triples")

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
                    logger.info(f"Got {num} triples.")
                    return

            except:
                pass

            time.sleep(2)

        raise RuntimeError("Timeout waiting for triples")

    def run(self):

        logger.info("=== TESTS BEGIN ===")

        self.test_load_text()

        self.test_text_completion()

        self.test_prompt()

        self.test_embeddings()

        print("Sleep for a bit")
        time.sleep(15)

        self.test_triples()

        self.test_graph_rag()

        logger.info("=== TESTS COMPLETED ===")

        time.sleep(2)

