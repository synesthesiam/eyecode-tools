import csv, argparse, sys

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Filters a Tobii data file so that only valid samples are written out")
parser.add_argument("-v", "--validmax", type=int, default=1,
        help="Maximum valid code (Tobii recommends 1)")

parser.add_argument("--tsv", action="store_true",
        help="Read and write tab-separated (tsv) instead of comma-separated (csv) data")

parser.add_argument("-o", "--output", type=str, default=None,
        help="Output filtered data to file instead of stdout")

parser.add_argument("csvfile", type=str)
args = parser.parse_args()

dialect = "excel"
if args.tsv:
    dialect = "excel-tab"

# Read and write data
with open(args.csvfile, "r") as in_file:
    out_file = sys.stdout

    if args.output:
        out_file = open(args.output, "w")

    reader = csv.DictReader(in_file, dialect=dialect)
    writer = csv.DictWriter(out_file, reader.fieldnames, dialect=dialect)
    writer.writeheader()

    for row in reader:
        try:
            v_left = int(row["ValidityLeft"])
            v_right = int(row["ValidityRight"])

            # Filter by validity code sum
            if (v_left + v_right) <= args.validmax:
                writer.writerow(row)
        except:
            pass
