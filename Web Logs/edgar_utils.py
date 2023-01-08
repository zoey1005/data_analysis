from bisect import bisect
import re
import netaddr
import pandas as pd

ips = pd.read_csv("ip2location.csv")


def lookup_region(ip_ad):
    ip_add = re.sub(r'[a-z]', '0', ip_ad)
    index3 = bisect(list(ips['low']), int(netaddr.IPAddress(ip_add)))
    info = ips.iloc[index3 - 1].region
    return info


def line_result(html):
    global f_line1
    global f_line2
    all_line = []
    for addr_html in re.findall(r'<div class="mailer">([\s\S]+?)</div>', html):
        lines = []
        for line in re.findall(r'<span class="mailerAddress">([\s\S]+?)</span>', addr_html):
            lines.append(line.strip())
        if lines:
            all_line.append('\n'.join(lines))
    return all_line


def result(html):
    result2 = re.findall(r"SIC=([0-9]{3,4})", html)
    if len(result2) == 0:
        return None
    else:
        return int(result2[0])


class Filing:
    def __init__(self, html):
        self.dates = re.findall(r"19\d{2}-\d{2}-\d{2}|20\d{2}-\d{2}-\d{2}", html)
        self.sic = result(html)
        self.addresses = line_result(html)

    def state(self):
        for addr in self.addresses:
            states = re.findall(r"[A-Z]{2}\s[0-9]{5}", addr)
            if states:
                return states[0][0:2]
        return None
