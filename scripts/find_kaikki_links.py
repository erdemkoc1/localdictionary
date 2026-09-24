import urllib.request
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

url = 'https://kaikki.org/dictionary/rawdata.html'
try:
    html = urllib.request.urlopen(url).read().decode('utf-8', 'ignore')
    links = re.findall(r'https?://[^\s"\'<>]+', html)
    for l in sorted(set(links)):
        if 'kaikki.org' in l and ('.json' in l or '.gz' in l or '.tar' in l or 'dict' in l):
            print(l)
except Exception as e:
    print('Error:', e)
