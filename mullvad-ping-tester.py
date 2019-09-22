import requests
import subprocess
import re
import progressbar
import pprint
from bs4 import BeautifulSoup
from collections import OrderedDict
from operator import itemgetter


url = "https://www.mullvad.net/ru/servers/"


def get_html(url):
    page = requests.get(url).text
    return page


def get_data(html):
    data = BeautifulSoup(html, "lxml")
    trs = data.find("table").find_all("tr")
    ips = []
    for tr in trs[1:]:
        ip = tr.find("td").text
        ips.append(ip + ".mullvad.net")
    ips = ips[1:]
    return ips


def ping(hosts):
    bar = progressbar.ProgressBar(
        maxval=100, widgets=[progressbar.Bar(
         '■', '[', ']'), ' ', progressbar.Percentage()])
    bar.start()
    counter = 0
    avg_ping_list = []
    pattern = r"Average = (\d+\S+)"
    for host in hosts:
        bar.update(counter / len(hosts) * 100)
        counter += 1
        ping = subprocess.Popen(
               ["ping", host, "-n", "1"],
               stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output = ping.communicate()
        avg_ping = ''.join(re.findall(pattern, output[0].decode()))
        try:
            avg_ping_list.append(int(avg_ping[:-2]))
        except ValueError:
            avg_ping_list.append(99999999999999999)  # Server is DOWN. TODO
    bar.finish()
    servers_pings = dict(zip(hosts, avg_ping_list))
    servers_pings_sorted = OrderedDict(sorted(
                                             servers_pings.items(),
                                             key=itemgetter(1), reverse=False))
    best3 = dict(list(servers_pings_sorted.items())[:3])
    while True:
        choice = input(
                 "Choose type of output (type best3/all). Type exit to close:")
        if choice == "best3":
            pprint.pprint(best3)
            continue
        elif choice == "all":
            pprint.pprint(servers_pings_sorted)
            continue
        elif choice == "exit":
            break
        else:
            print("Invalid type")
            continue


def main():
    ping(get_data(get_html(url)))


if __name__ == "__main__":
    main()
