import csv, argparse, sys
from collections import defaultdict

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Counts the number of valid/invalid samples in a Tobii data file")

# The Tobii developer's guide suggests that samples
# with a validity code of 2 or higher should be
# considered "invalid"
parser.add_argument("-v", "--validmax", type=int, default=1,
        help="Maximum valid code (Tobii recommends 1)")

parser.add_argument("--tsv", action="store_true")
parser.add_argument("csvfile", type=str)
args = parser.parse_args()

# Count up left/right validity codes
codes = defaultdict(int)
with open(args.csvfile, "r") as csv_file:
    dialect = "excel"
    if args.tsv:
        dialect = "excel-tab"

    reader = csv.DictReader(csv_file, dialect=dialect)
    for row in reader:
        try:
            v_left = int(row["ValidityLeft"])
            v_right = int(row["ValidityRight"])
            codes[(v_left, v_right)] += 1
        except:
            pass

# Print results
total = sum(codes.values())
print("{0:,} samples".format(total))

if total == 0:
    sys.exit(0)  # No samples!

valid = 0
invalid = 0

for (v_both, count) in codes.iteritems():
    if sum(v_both) > args.validmax:
        invalid += count
    else:
        valid += count

print("Valid: {0:,} ({1:.0f}%)".format(valid,
    valid / float(total) * 100))

print("Invalid: {0:,} ({1:.0f}%)".format(invalid,
    invalid / float(total) * 100))

