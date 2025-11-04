import urllib.request
import sys

url = 'http://127.0.0.1:8000/'
try:
    with urllib.request.urlopen(url, timeout=5) as r:
        print('status', r.status)
        body = r.read().decode('utf-8')
        print(body[:2000])
except Exception as e:
    print('ERR', repr(e))
    sys.exit(2)
