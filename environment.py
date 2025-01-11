
import subprocess
import os

import logging
logger = logging.getLogger("environment")
logging.basicConfig(level=logging.INFO, format='%(message)s')

class TestEnvironment:

    def __init__(self, engine, target):

        self.engine = engine
        self.target = target
        self.cfg = engine.generate_launch_config(target)
        self.target_dir = self.engine.target_run_dir

    def __enter__(self):
        logger.debug("Create environment...")
        self.wipe()
        self.setup()
        return self

    def __exit__(self, *args):
        logger.debug("Destroy environment...")
        self.wipe()

    def wipe(self):
        proc = subprocess.run( [ "rm", "-rf", self.target_dir, ] )
        if proc.returncode != 0:
            raise RuntimeError("Clearout failed")

    def create_directory(self):
        os.mkdir(self.target_dir)
        self.chcon(self.target_dir)

    def chcon(self, path):
        proc = subprocess.run([
            # -R for recursive?
            "chcon", "-t", "svirt_sandbox_file_t", path
        ])
        if proc.returncode != 0:
            raise RuntimeError("Clearout failed")


    def generate_deploy_package(self):

        path = f"{self.target_dir}/launch.yaml"
        with open(path, "w") as f:
            f.write(self.cfg)
        self.chcon(path)

        logger.debug(f"Generated launch.yaml.")

    def configure_extras(self):

        os.mkdir(self.target_dir + "/prometheus/")
        self.chcon(self.target_dir + "/prometheus/")

        os.mkdir(self.target_dir + "/grafana/")
        self.chcon(self.target_dir + "/grafana/")

        os.mkdir(self.target_dir + "/grafana/dashboards/")
        self.chcon(self.target_dir + "/grafana/dashboards/")

        os.mkdir(self.target_dir + "/grafana/provisioning/")
        self.chcon(self.target_dir + "/grafana/provisioning/")

        for file in [
                "prometheus/prometheus.yml",
                "grafana/dashboards/dashboard.json",
                "grafana/provisioning/dashboard.yml",
                "grafana/provisioning/datasource.yml",
        ]:
            with open(f"{self.engine.trustgraph_dir}/{file}", "r") as src:
                with open(f"{self.target_dir}/{file}", "w") as dest:
                    dest.write(src.read())
                    logger.debug(f"Wrote {file}.")
            self.chcon(self.target_dir)

    def setup(self):

        self.create_directory()
        self.generate_deploy_package()
        self.configure_extras()        
