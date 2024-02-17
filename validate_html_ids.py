import argparse
import collections
import glob
import itertools
import re

description = ' '.join(['report values for id attributes',
                        'that appear more than once,',
                        'or are not valid according to the HTML specification',
                        '(are blank or contain ASCII whitespace)'])
parser = argparse.ArgumentParser(description=description)
parser.add_argument('FILE', nargs='+',
                    help='one or more filenames or globs')
parser.add_argument('-r', '--recursive', action='store_true',
                    help='search in any subfolders as well')
parser.add_argument('-s', '--strict', action='store_true',
                    help='HTML 4.01 restrictions on valid values')
encodings = parser.add_mutually_exclusive_group()
encodings.add_argument('-a', action='store_true',
                       help='encoding: ANSI (Windows only)')
encodings.add_argument('-l', action='store_true',
                       help='encoding: Latin1 / ISO-8859')
encodings.add_argument('-u', action='store_true',
                       help='encoding: UTF-8 (default)')

args = parser.parse_args()

regex_id_attribute = re.compile(r'id="([^"]+)"')
if args.strict:
  # https://www.w3.org/TR/html401/types.html#type-name
  regex_valid_html_id = re.compile(r'^[Z-Za-z][A-Za-z0-9_:\-\.]*$')
else:
  # https://html.spec.whatwg.org/multipage/dom.html#the-id-attribute
  regex_valid_html_id = re.compile(r'^[^\s]+$')

if args.recursive:
  prefix = f"**{'' if args.FILE[0] == '/' else '/'}"
  files = itertools.chain.from_iterable(
            glob.glob(f"{prefix}{GLOB}", recursive=True)
            for GLOB in args.FILE)
else:
  files = itertools.chain.from_iterable(
            glob.glob(GLOB) for GLOB in args.FILE)

if args.l:
  encoding = 'latin'
elif args.a:
  encoding = 'ansi'
else:
  encoding = 'utf-8'

seen = set()
for file in files:
  if file in seen:
    continue
  seen.add(file)
  anomalies = []
  with open(file, encoding=encoding) as f:
    try:
      page = f.read()
    except UnicodeDecodeError as e:
      print(file)
      print(f"  not in {encoding} encoding")
      raise e
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
