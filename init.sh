apt install python3-pip --yes
pip3 install luigi --break-system-packages
pip3 install flask --break-system-packages
apt install npm
wget https://go.dev/dl/go1.22.1.linux-amd64.tar.gz
rm -rf /usr/local/go && tar -C /usr/local -xzf go1.22.1.linux-amd64.tar.gz
echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.profile
echo 'export PATH=$PATH:/root/go/bin' >> ~/.profile
source ~/.profile
apt install build-essential --yes
sudo apt-get install libpcap-dev --yes
git clone https://github.com/blechschmidt/massdns.git
cd massdns
make
sudo make install
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install -v github.com/projectdiscovery/naabu/v2/cmd/naabu@latest
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
go install -v github.com/tomnomnom/assetfinder@latest
go install -v github.com/tomnomnom/anew@latest
go install github.com/d3mondev/puredns/v2@latest
go install github.com/projectdiscovery/alterx/cmd/alterx@latest
go install github.com/projectdiscovery/tlsx/cmd/tlsx@latest
go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest
go install github.com/trickest/dsieve@latest

wget https://wordlists-cdn.assetnote.io/data/manual/best-dns-wordlist.txt -O ~/best-dns-wordlist.txt
wget https://raw.githubusercontent.com/trickest/resolvers/main/resolvers.txt -O ~/resolvers.txt

wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt-get install fonts-liberation libu2f-udev
sudo dpkg -i google-chrome-stable_current_amd64.deb