from base_task import BaseTask
from utils import *
import tempfile
import luigi
import requests

class PassiveAssetDiscoveryV1(BaseTask):
    def output(self):
        return luigi.LocalTarget(f"{self.save_directory}/{self.__class__.__name__}-{self.case}")

    def run(self):
        cmd = f"subfinder -t 100 -all -silent -d {self.domain} 2> /dev/null"
        self.run_cmd(cmd, self.output().path)


class PassiveAssetDiscoveryV2(BaseTask):
    def output(self):
        return luigi.LocalTarget(f"{self.save_directory}/{self.__class__.__name__}-{self.case}")

    def run(self):
        cmd = f"assetfinder --subs-only {self.domain} 2> /dev/null"
        self.run_cmd(cmd, self.output().path)


class DNSBruteforcing(BaseTask):
    def output(self):
        return luigi.LocalTarget(f"{self.save_directory}/{self.__class__.__name__}-{self.case}")

    def run(self):
        cmd = f"puredns bruteforce ~/best-dns-wordlist.txt {self.domain} -q -r ~/resolvers.txt | anew -d {self.save_directory}/DNSResolving-passive"
        self.run_cmd(cmd, self.output().path)


class AssetEnrichment(BaseTask):

    def requires(self):
        if self.case == "passive":
            return [PassiveAssetDiscoveryV1(domain=self.domain,case=self.case,save_directory=self.save_directory,scan_id=self.scan_id), PassiveAssetDiscoveryV2(domain=self.domain,case=self.case,save_directory=self.save_directory,scan_id=self.scan_id)]
        else:
            return [DNSBruteforcing(domain=self.domain,case=self.case,save_directory=self.save_directory,scan_id=self.scan_id)]

    def run(self):
        # Aggregate outputs from dependencies
        input_files = [input_file.path for input_file in self.input()]
        # Command for aggregating and enriching asset data
        cmd = f"cat {' '.join(input_files)} | sed 's/\*\.//g' | sort -u | dsieve  2> /dev/null || true"  # Assuming dsieve or another enrichment tool follows
        self.run_cmd(cmd, self.output().path)

    def output(self):
        # Adjusted output path to reflect dynamic case handling
        return luigi.LocalTarget(f"{self.save_directory}/{self.__class__.__name__}-{self.case}")


class WordlistGenerator(BaseTask):

    def requires(self):
        return AssetEnrichment(domain=self.domain,case=self.case,save_directory=self.save_directory,scan_id=self.scan_id)

    def output(self):
        return luigi.LocalTarget(f"{self.save_directory}/{self.__class__.__name__}-{self.case}")

    def run(self):
        cmd = f"cat {self.input().path} | alterx -enrich -silent 2> /dev/null || true"
        self.run_cmd(cmd, self.output().path)

class DNSResolving(BaseTask):

    def requires(self):
        return WordlistGenerator(domain=self.domain,case=self.case,save_directory=self.save_directory,scan_id=self.scan_id)

    def output(self):
        return luigi.LocalTarget(f"{self.save_directory}/{self.__class__.__name__}-{self.case}")

    def run(self):
        cmd = f"cat {self.input().path} | puredns resolve -r ~/resolvers.txt -l 1000 2> /dev/null"
        self.run_cmd(cmd, self.output().path)


class PortScaning(BaseTask):

    def requires(self):
        return DNSResolving(domain=self.domain,case=self.case,save_directory=self.save_directory,scan_id=self.scan_id)

    def output(self):
        return luigi.LocalTarget(f"{self.save_directory}/{self.__class__.__name__}-{self.case}")

    def run(self):
        cmd = f"cat {self.input().path} | naabu -silent -c 100 -rate 2000 -p '443,80,81,300,591,593,832,981,1010,1311,1099,2082,2095,2096,2480,3000,3128,3333,4243,4567,4711,4712,4993,5000,5104,5108,5280,5281,5601,5800,6543,7000,7001,7396,7474' || true"
        self.run_cmd(cmd, self.output().path)



class HTTPProbing(BaseTask):

    def requires(self):
        return PortScaning(domain=self.domain,case=self.case,save_directory=self.save_directory,scan_id=self.scan_id)


    def output(self):
        return luigi.LocalTarget(f"{self.save_directory}/{self.__class__.__name__}-{self.case}")

    def run(self):
        cmd = f"cat {self.input().path} | httpx -silent -vhost -tls-probe -favicon -t 500 -fhr -sr -store-chain -srd ~/bugbounty/archive/"
        self.run_cmd(cmd, self.output().path)


class YieldWrapper(BaseTask):
    def requires(self):
        return HTTPProbing(domain=self.domain, case=self.case, save_directory=self.save_directory,scan_id=self.scan_id)

    def output(self):
        return luigi.LocalTarget(f"{self.save_directory}/{self.__class__.__name__}-{self.case}")

    def run(self):
        with self.output().open('w') as f:
            f.write("Completed")
        self.update_status('done')
        yield Miscellaneous(domain=self.domain, case=self.case, save_directory=self.save_directory,scan_id=self.scan_id)

class Miscellaneous(BaseTask):
    def requires(self):

        return [
            
            Screenshots(domain=self.domain,case=self.case,save_directory=self.save_directory,scan_id=self.scan_id),
            TlsGrabber(domain=self.domain,case=self.case,save_directory=self.save_directory,scan_id=self.scan_id),
            TlsFilter(domain=self.domain,case=self.case,save_directory=self.save_directory,scan_id=self.scan_id),
            RecordsDump(domain=self.domain,case=self.case,save_directory=self.save_directory,scan_id=self.scan_id),
            VulnerabilityScanner(domain=self.domain,case=self.case,save_directory=self.save_directory,scan_id=self.scan_id) 

            ]
    def output(self):
        return luigi.LocalTarget(f"{self.save_directory}/{self.__class__.__name__}-{self.case}")


    def run(self):
       with self.output().open('w') as f:
            f.write("Completed")
       self.update_status('done')


class TlsGrabber(BaseTask):

    def output(self):
        return luigi.LocalTarget(f"{self.save_directory}/{self.__class__.__name__}-{self.case}")

    def run(self):
        cmd = f"cat {self.save_directory}/HTTPProbing-{self.case} | tlsx -san -cn -silent -resp-only -c 500 | sort -u"
        self.run_cmd(cmd, self.output().path)

class Screenshots(BaseTask):

    def output(self):
        return luigi.LocalTarget(f"{self.save_directory}/{self.__class__.__name__}-{self.case}")

    def run(self):
        cmd = f"cat {self.save_directory}/HTTPProbing-{self.case} | awk '{{print $1}}' | gowitness file --disable-db --delay 1 --header 'User-Agent: Mozilla/5.0 (Linux; Android 12; SM-S906N Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/80.0.3987.119 Mobile Safari/537.36' -t 200 --timeout 5 -f x.txt -P {self.save_directory}/gowitness"
        self.run_cmd(cmd, self.output().path)


class TlsFilter(BaseTask):

    def output(self):
        return luigi.LocalTarget(f"{self.save_directory}/{self.__class__.__name__}-{self.case}")

    def run(self):
        cmd = f"cat {self.save_directory}/TlsGrabber-{self.case} | grep -v {self.domain} || true"
        self.run_cmd(cmd, self.output().path)


class RecordsDump(BaseTask):


    def output(self):
        return luigi.LocalTarget(f"{self.save_directory}/{self.__class__.__name__}-{self.case}")

    def run(self):
        cmd = f"cat {self.save_directory}/DNSResolving-{self.case} | dnsx -silent -recon -resp"
        self.run_cmd(cmd, self.output().path)


class VulnerabilityScanner(BaseTask):

    def output(self):
        return luigi.LocalTarget(f"{self.save_directory}/{self.__class__.__name__}-{self.case}")

    def run(self):
        cmd = f"cat {self.save_directory}/HTTPProbing-{self.case} | nuclei -c 100 -silent -es low,info"
        self.run_cmd(cmd, self.output().path)


class PrototypePollution(BaseTask):

    def output(self):
        return luigi.LocalTarget(f"{self.save_directory}/{self.__class__.__name__}-{self.case}")

    def run(self):
        with tempfile.NamedTemporaryFile(dir='/tmp', delete=False) as tmpfile:
            temp_output_path = tmpfile.name

        cmd = f"cat {self.save_directory}/HTTPProbing-{self.case} | plution -o {temp_output_path} && cat {temp_output_path}"
        self.run_cmd(cmd, self.output().path)

class AXScanner(BaseTask):
    def run(self):
        try:
            unique_urls = set()  # To store unique URLs after removing http:// and https:// prefixes
            with open(f"{self.save_directory}/HTTPProbing-{self.case}", 'r') as file:
                for line in file:
                    url = line.strip()
                    # Removing http:// and https:// prefixes
                    url = url.replace("http://", "").replace("https://", "")
                    unique_urls.add(url)
            
            # Now unique_urls contains only unique URLs without http:// and https://
            for url in unique_urls:
                response = requests.get(f"http://207.244.237.10:3442/add_target/{url}")
                if response.status_code == 200:
                    print(f"Success: Added {url} to pending targets. Response: {response.text}")
                else:
                    print(f"Error for {url}: Received status code {response.status_code}")
        except FileNotFoundError:
            self.update_status('failed', file_path)
        except Exception as e:
            self.update_status('failed', e)
            
        self.update_status('done')


    def output(self):
        return luigi.LocalTarget(f"{self.save_directory}/{self.__class__.__name__}-{self.case}")


class MainEnumerationTask(BaseTask):
    def requires(self):
        if self.scan_type == 'hybrid':

            scan = [

            YieldWrapper(domain=self.domain, case='active', save_directory=self.save_directory,scan_id=self.scan_id),
            YieldWrapper(domain=self.domain, case='passive', save_directory=self.save_directory,scan_id=self.scan_id)
        ]

        elif self.scan_type == 'passive':
            scan = [YieldWrapper(domain=self.domain, case='passive', save_directory=self.save_directory,scan_id=self.scan_id)]
            
        return scan

    def run(self):
        self.update_status('done')
        self.update_scan_status('done')