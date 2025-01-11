
import subprocess
import os

import logging
logger = logging.getLogger("launch")
logging.basicConfig(level=logging.INFO, format='%(message)s')

class SystemLaunched:

    def __init__(self, dir):
        self.path = dir
        self.oldpath = os.getcwd()

    def __enter__(self):
        logger.debug("Launch environment...")
        os.chdir(self.path)
        self.unlaunch()
        self.launch()

    def __exit__(self, *args):
        logger.debug("Undeploy environment...")
        self.unlaunch()
        os.chdir(self.oldpath)

    def unlaunch(self):
        proc = subprocess.run(
            [
                "podman-compose", "-f", "launch.yaml",
                "down", "-v", "-t", "0"
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        if proc.returncode != 0:
            raise RuntimeError("Clearout failed")

    def launch(self):

        logger.debug("Pulling containers...")
        proc = subprocess.run(
            [
                "podman-compose", "-f", "launch.yaml",
                "pull"
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        logger.debug("Deploy containers...")
        proc = subprocess.run(
            [
                "podman-compose", "-f", "launch.yaml",
                "up", "-d"
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        if proc.returncode != 0:
            raise RuntimeError("Clearout failed")

        if proc.returncode != 0:
            raise RuntimeError("Clearout failed")
