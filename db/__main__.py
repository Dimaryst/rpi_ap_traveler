import argparse
from schema import fill_db
parser = argparse.ArgumentParser()
parser.add_argument("first")
args = parser.parse_args()

if args.first == "init":
    fill_db()
    print("Tables was created")
else:
    print("Nothing")

