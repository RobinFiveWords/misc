import argparse
import collections
import glob
import itertools
import re

parser = argparse.ArgumentParser()
parser.add_argument('FILE', nargs='+',
                    help='one or more filenames or globs')
parser.add_argument('-r', '--recursive', action='store_true',
                    help='search in any subfolders as well')
args = parser.parse_args()

regex_id_attribute = re.compile(r'id="([^"]+)"')
regex_valid_html_id = re.compile(r'^[A-Za-z][A-Za-z0-9_:\-\.]*$')

if args.recursive:
  prefix = f"**{'' if args.FILE[0] == '/' else '/'}"
  files = itertools.chain.from_iterable(
            glob.glob(f"{prefix}{GLOB}", recursive=True)
            for GLOB in args.FILE)
else:
  files = itertools.chain.from_iterable(
            glob.glob(GLOB) for GLOB in args.FILE)

seen = set()
for file in files:
  if file in seen:
    continue
  seen.add(file)
  anomalies = []
  with open(file) as f:
    page = f.read()
  id_counts = collections.Counter(regex_id_attribute.findall(page))
  for id_value, count in id_counts.items():
    if not regex_valid_html_id.match(id_value):
      anomalies.append(f"  invalid {count:>4d} {id_value}")
    elif count > 1:
      anomalies.append(f"  {count:>4d} {id_value}")
  if not anomalies:
    print(f"{file} : ok")
  else:
    print(file)
    for anomaly in anomalies:
      print(anomaly)
