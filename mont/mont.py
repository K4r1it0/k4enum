import luigi
import subprocess
import os
import sys
import argparse
from luigi.contrib.schedulers import Scheduler
import time

# Global list to store output paths
output_paths = []

class BaseTask(luigi.Task):
    domain = luigi.Parameter()

    def run_cmd(self, cmd, output_path):
        print(f"Executing command: {cmd}")
        output_paths.append(output_path)
        try:
            with open(output_path, 'w') as file:
                subprocess.run(cmd, shell=True, check=True, stdout=file, stderr=subprocess.STDOUT)
            with open(output_path, 'r') as file:
                output = file.read()
                print(output)  # For debugging

        except subprocess.CalledProcessError as e:
            error_message = f"Command failed with error: {e}"
            with open(output_path, 'w') as file:
                file.write(error_message)

    def output(self):
        directory = f"./mont/{self.domain}"
        if not os.path.exists(directory):
            os.makedirs(directory)
        return luigi.LocalTarget(f"{directory}/{self.__class__.__name__}.txt")

class PassiveAssetDiscoveryV1(BaseTask):

    def run(self):
        cmd = f"subfinder -t 100 -all -silent -d {self.domain} 2> /dev/null"
        self.run_cmd(cmd, self.output().path)

class PassiveAssetDiscoveryV2(BaseTask):

    def run(self):
        cmd = f"assetfinder --subs-only {self.domain} 2> /dev/null"
        self.run_cmd(cmd, self.output().path)

class AssetEnrichment(BaseTask):

    def requires(self):
        return [PassiveAssetDiscoveryV1(domain=self.domain), PassiveAssetDiscoveryV2(domain=self.domain)]

    def run(self):
        input_files = [input_file.path for input_file in self.input()]
        cmd = f"cat {' '.join(input_files)} | sed 's/\\*\\.//g' | sort -u | dsieve 2> /dev/null || true"
        self.run_cmd(cmd, self.output().path)

class WordlistGenerator(BaseTask):

    def requires(self):
        return AssetEnrichment(domain=self.domain)

    def run(self):
        cmd = f"cat {self.input().path} | alterx -enrich -silent 2> /dev/null || true"
        self.run_cmd(cmd, self.output().path)

class DNSResolving(BaseTask):

    def requires(self):
        return WordlistGenerator(domain=self.domain)

    def run(self):
        cmd = f"cat {self.input().path} | puredns resolve -r ~/resolvers.txt -l 1000 2> /dev/null"
        self.run_cmd(cmd, self.output().path)

class PortScanning(BaseTask):

    def requires(self):
        return DNSResolving(domain=self.domain)

    def run(self):
        cmd = f"cat {self.input().path} | naabu -silent -c 100 -rate 2000 -p '443,80,81,300,591,593,832,981,1010,1311,1099,2082,2095,2096,2480,3000,3128,3333,4243,4567,4711,4712,4993,5000,5104,5108,5280,5281,5601,5800,6543,7000,7001,7396,7474' || true"
        self.run_cmd(cmd, self.output().path)

class HTTPProbing(BaseTask):

    def requires(self):
        return PortScanning(domain=self.domain)

    def run(self):
        cmd = f"cat {self.input().path} | httpx -t 500 2> /dev/null"
        self.run_cmd(cmd, self.output().path)

class Anew(BaseTask):
    def requires(self):
        return HTTPProbing(domain=self.domain)

    def run(self):
        latest_path = f"./mont/{self.domain}/latest.txt"
        if os.path.exists(latest_path):
            cmd = f"cat {self.input().path} | anew {latest_path}"
        else:
            cmd = f"cat {self.input().path} | anew {latest_path} > /dev/null"
        self.run_cmd(cmd, self.output().path)

class Notify(BaseTask):

    def requires(self):
        return Anew(domain=self.domain)

    def run(self):
        cmd = f"cat {self.input().path} | notify -bulk"
        self.run_cmd(cmd, self.output().path)

class Cleanup(BaseTask):

    def requires(self):
        return Notify(domain=self.domain)

    def run(self):
        cmd = f"find ./mont/{self.domain} -type f ! -name 'latest.txt' ! -name 'Cleanup.txt' -exec rm -f {{}} +"
        self.run_cmd(cmd, self.output().path)

class MainEnumerationTask(BaseTask):

    def requires(self):
        return Cleanup(domain=self.domain)

    def run(self):
        cmd = f"rm {self.input().path}"
        self.run_cmd(cmd, self.output().path)

    def complete(self):
        """
        Always return False to ensure the MainEnumerationTask runs even if the output file exists.
        """
        return False

def main():
    parser = argparse.ArgumentParser(description="Run enumeration tasks for domains.")
    parser.add_argument('domain', metavar='domain', type=str, nargs='?', help='Single domain name')
    parser.add_argument('-f', '--file', type=str, help='File containing list of domains')

    args = parser.parse_args()

    domains = []

    if args.domain:
        domains.append(args.domain)

    if args.file:
        with open(args.file, 'r') as file:
            domains.extend(file.read().splitlines())

    max_workers = 100

    while True:
        tasks = [MainEnumerationTask(domain=domain) for domain in domains]
        luigi.build(tasks, local_scheduler=True, workers=max_workers)
        
        # Sleep for 12 hours before running again
        print("Sleeping for 12 hours before next run...")
        time.sleep(12 * 60 * 60)  # 12 hours in seconds

if __name__ == '__main__':
    main()
