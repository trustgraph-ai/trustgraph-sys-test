
import time
import requests
import importlib
import json
import logging
import os

from environment import TestEnvironment
from launch import SystemLaunched
from tests import Tester

logger = logging.getLogger("engine")
logging.basicConfig(level=logging.INFO, format='%(message)s')

import yaml

class TestEngine:
    def __init__(
            self, trustgraph_dir, templates_dir, version,
            target_run_dir="target-environment",
    ):
        self.trustgraph_dir = trustgraph_dir
        self.templates_dir = templates_dir
        self.target_run_dir = target_run_dir
        self.version = version
        self.pulsar = "http://localhost:9090"
        self.test_dir = os.getcwd()

        spec = importlib.util.spec_from_file_location(
            'generate', f'{self.templates_dir}/generate.py'
        )
        self.generate = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.generate)

    def generate_config(self, target):

        return [
            {
                "name": target["graph"],
                "parameters": {}
            },
            {
                "name": "pulsar",
                "parameters": {}
            },
            {
                "name": target["vector"],
                "parameters": {}
            },
            {
                "name": "embeddings-hf",
                "parameters": {}
            },
            {
                "name": "graph-rag",
                "parameters": {}
            },
            {
                "name": "document-rag",
                "parameters": {}
            },
            {
                "name": "grafana",
                "parameters": {}
            },
            {
                "name": "trustgraph-base",
                "parameters": {}
            },
            {
                "name": "googleaistudio",
                "parameters": {
                    "googleaistudio-temperature": 0.1,
                    "googleaistudio-max-output-tokens": 8000,
                    "googleaistudio-model": "gemini-1.5-flash-002"
                }
            },
            {
                "name": "googleaistudio-rag",
                "parameters": {
                    "googleaistudio-temperature": 0.1,
                    "googleaistudio-max-output-tokens": 8000,
                    "googleaistudio-model": "gemini-1.5-flash-002"
                }
            },
            {
                "name": "prompt-template",
                "parameters": {}
            },
            {
                "name": "override-recursive-chunker",
                "parameters": {
                    "chunk-size": 1000,
                    "chunk-overlap": 50
                }
            },
            {
                "name": "prompt-overrides",
                "parameters": {
                    "system-template": "You are a helpful assistant that performs NLP, Natural Language Processing, tasks.\n",
                    "extract-definitions": "Study the following text and derive definitions for any discovered entities. Do not provide definitions for entities whose definitions are incomplete or unknown. Output relationships in JSON format as an array of objects with keys:\n- entity: the name of the entity\n- definition: English text which defines the entity\n\nHere is the text:\n{{text}}\n\nRequirements:\n- Do not provide explanations.\n- Do not use special characters in the response text.\n- The response will be written as plain text.\n- Do not include null or unknown definitions.\n- The response shall use the following JSON schema structure:\n\n```json\n[{\"entity\": string, \"definition\": string}]\n```",
                    "extract-relationships": "Study the following text and derive entity relationships.  For each relationship, derive the subject, predicate and object of the relationship. Output relationships in JSON format as an array of objects with keys:\n- subject: the subject of the relationship\n- predicate: the predicate\n- object: the object of the relationship\n- object-entity: FALSE if the object is a simple data type and TRUE if the object is an entity\n\nHere is the text:\n{{text}}\n\nRequirements:\n- You will respond only with well formed JSON.\n- Do not provide explanations.\n- Respond only with plain text.\n- Do not respond with special characters.\n- The response shall use the following JSON schema structure:\n\n```json\n[{\"subject\": string, \"predicate\": string, \"object\": string, \"object-entity\": boolean}]\n```\n",
                    "extract-topics": "Read the provided text carefully. You will identify topics and their definitions found in the provided text. Topics are intangible concepts.\n\nReading Instructions:\n- Ignore document formatting in the provided text.\n- Study the provided text carefully for intangible concepts.\n\nHere is the text:\n{{text}}\n\nResponse Instructions: \n- Do not respond with special characters.\n- Return only topics that are concepts and unique to the provided text.\n- Respond only with well-formed JSON.\n- The JSON response shall be an array of objects with keys \"topic\" and \"definition\". \n- The response shall use the following JSON schema structure:\n\n```json\n[{\"topic\": string, \"definition\": string}]\n```\n\n- Do not write any additional text or explanations.",
                    "extract-rows": "<instructions>\nStudy the following text and derive objects which match the schema provided.\n\nYou must output an array of JSON objects for each object you discover\nwhich matches the schema.  For each object, output a JSON object whose fields\ncarry the name field specified in the schema.\n</instructions>\n\n<schema>\n{{schema}}\n</schema>\n\n<text>\n{{text}}\n</text>\n\n<requirements>\nYou will respond only with raw JSON format data. Do not provide\nexplanations. Do not add markdown formatting or headers or prefixes.\n</requirements>",
                    "kg-prompt": "Study the following set of knowledge statements. The statements are written in Cypher format that has been extracted from a knowledge graph. Use only the provided set of knowledge statements in your response. Do not speculate if the answer is not found in the provided set of knowledge statements.\n\nHere's the knowledge statements:\n{% for edge in knowledge %}({{edge.s}})-[{{edge.p}}]->({{edge.o}})\n{%endfor%}\n\nUse only the provided knowledge statements to respond to the following:\n{{query}}\n",
                    "document-prompt": "Study the following context. Use only the information provided in the context in your response. Do not speculate if the answer is not found in the provided set of knowledge statements.\n\nHere is the context:\n{{documents}}\n\nUse only the provided knowledge statements to respond to the following:\n{{query}}\n",
                    "agent-react": "Answer the following questions as best you can. You have\naccess to the following functions:\n\n{% for tool in tools %}{\n    \"function\": \"{{ tool.name }}\",\n    \"description\": \"{{ tool.description }}\",\n    \"arguments\": [\n{% for arg in tool.arguments %}        {\n            \"name\": \"{{ arg.name }}\",\n            \"type\": \"{{ arg.type }}\",\n            \"description\": \"{{ arg.description }}\",\n        }\n{% endfor %}\n    ]\n}\n{% endfor %}\n\nYou can either choose to call a function to get more information, or\nreturn a final answer.\n    \nTo call a function, respond with a JSON object of the following format:\n\n{\n    \"thought\": \"your thought about what to do\",\n    \"action\": \"the action to take, should be one of [{{tool_names}}]\",\n    \"arguments\": {\n        \"argument1\": \"argument_value\",\n        \"argument2\": \"argument_value\"\n    }\n}\n\nTo provide a final answer, response a JSON object of the following format:\n\n{\n  \"thought\": \"I now know the final answer\",\n  \"final-answer\": \"the final answer to the original input question\"\n}\n\nPrevious steps are included in the input.  Each step has the following\nformat in your output:\n\n{\n  \"thought\": \"your thought about what to do\",\n  \"action\": \"the action taken\",\n  \"arguments\": {\n      \"argument1\": action argument,\n      \"argument2\": action argument2\n  },\n  \"observation\": \"the result of the action\",\n}\n\nRespond by describing either one single thought/action/arguments or\nthe final-answer.  Pause after providing one action or final-answer.\n\n{% if context %}Additional context has been provided:\n{{context}}{% endif %}\n\nQuestion: {{question}}\n\nInput:\n    \n{% for h in history %}\n{\n    \"action\": \"{{h.action}}\",\n    \"arguments\": [\n{% for k, v in h.arguments.items() %}        {\n            \"{{k}}\": \"{{v}}\",\n{%endfor%}        }\n    ],\n    \"observation\": \"{{h.observation}}\"\n}\n{% endfor %}"
                }
            },
            {
                "name": "agent-manager-react",
                "parameters": {
                    "tools": [
                        {
                            "id": "sample-query",
                            "name": "Sample query",
                            "type": "knowledge-query",
                            "config": {},
                            "description": "Query a knowledge base that has already been extracted.  The query should be a simple natural language question.",
                            "arguments": [
                                {
                                    "name": "query",
                                    "type": "string",
                                    "description": "Describe the search query here."
                                }
                            ]
                        },
                        {
                            "id": "sample-completion",
                            "name": "Sample text completion",
                            "type": "text-completion",
                            "config": {},
                            "description": "Describe the request to send to LLM. This request will be sent with no additional context.",
                            "arguments": [
                                {
                                    "name": "response",
                                    "type": "string",
                                    "description": "The response expected from the LLM."
                                }
                            ]
                        }
                    ]
                }
            },
            {
                "name": "workbench-ui",
                "parameters": {}
            }
        ]
    
    def generate_launch_config(self, target):

        cfg = self.generate_config(target)

        platform = "docker-compose"

        with open(f"{self.templates_dir}/config-to-{platform}.jsonnet", "r") as f:
            wrapper = f.read()

        gen = self.generate.Generator(
            json.dumps(cfg).encode("utf-8"),
            version=self.version,
            base=self.templates_dir,
        )

        processed = gen.process(wrapper)

        y = yaml.dump(processed)

        return y

# /api/v1/query?query=processor_state{job="pdf-decoder",processor_state="running"}'
    

    def track_running(self, proc, timeout):

        until = time.time() + timeout

#        logger.info(f"Waiting for {proc} to start...")

        while time.time() < until:

            try:

                resp = requests.get(
                    f'{self.pulsar}/api/v1/query?query=processor_state{{job="{proc}",processor_state="running"}}'
                )

                resp = resp.json()

                datum = resp["data"]["result"][0]["value"][1]

                if datum == "1":
                    logger.info(f"{proc} is running")
                    return


            except Exception as e:
                pass
                
            time.sleep(2)

        raise RuntimeError(f"Timeout waiting for {proc} to start.")

    def track_up(self, proc, timeout):

        until = time.time() + timeout

#        logger.info(f"Waiting for {proc} to start...")

        while time.time() < until:

            try:

                resp = requests.get(
                    f'{self.pulsar}/api/v1/query?query=up{{job="{proc}"}}'
                )

                resp = resp.json()

                datum = resp["data"]["result"][0]["value"][1]

                if datum == "1":
                    logger.info(f"{proc} is up")
                    return


            except Exception as e:
                pass
                
            time.sleep(2)

        raise RuntimeError(f"Timeout waiting for {proc} to start.")

    def run_test(self, target):

        label = ", ".join(map(lambda x: f"{x[0]}={x[1]}", target.items()))
        logger.info(f"* Running tests for configuration ({label})")

        with TestEnvironment(self, target) as environment:
            with SystemLaunched(self.target_run_dir) as system:

                print("Waiting for processes to start...")

                self.track_up("zookeeper", 60)
                self.track_up("bookie", 60)
                self.track_up("pulsar", 60)

                self.track_running("agent-manager", 60)
                self.track_running("chunker", 10)
                self.track_running("embeddings", 60)
                self.track_running("graph-rag", 10)
                self.track_running("kg-extract-definitions", 10)
                self.track_running("kg-extract-relationships", 10)
                self.track_running("kg-extract-topics", 10)
                self.track_running("metering", 10)
                self.track_running("metering-rag", 10)
                self.track_running("pdf-decoder", 10)
                self.track_running("prompt", 10)
                self.track_running("prompt-rag", 10)
                self.track_running("query-graph-embeddings", 10)
                self.track_running("query-triples", 10)
                self.track_running("store-graph-embeddings", 10)
                self.track_running("store-triples", 10)
                self.track_running("text-completion", 10)
                self.track_running("text-completion-rag", 10)

                print("System is up!")

                tester = Tester(self)
                tester.run()

                print("Tests passed!")

