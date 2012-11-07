import csv, os, argparse

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Converts a tab-separated (tsv) file to a comma-separated (csv) file")
parser.add_argument("tsvfile", type=str)
parser.add_argument("-o", "--output", type=str, default=None,
        help="Write csv file to the given path instead of just changing the input path's extension")
args = parser.parse_args()

tsv_path = args.tsvfile
csv_path = args.output

if csv_path is None:
    csv_path = "{0}.csv".format(os.path.splitext(tsv_path)[0])

with open(tsv_path, "r") as tsv_file:
    with open(csv_path, "w") as csv_file:
        reader = csv.DictReader(tsv_file, dialect="excel-tab")
        writer = csv.DictWriter(csv_file, reader.fieldnames)
        writer.writeheader()

        for row in reader:
            writer.writerow(row)
