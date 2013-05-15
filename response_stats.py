#!/usr/bin/env python
import os, argparse, pandas
from lxml import etree
from datetime import datetime
from pretty_plot import shade_axis

import matplotlib
matplotlib.use("Agg")
from matplotlib import pyplot

# Constants {{{

TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
font_family = ["Arial"]
title_size = 20
text_size = 16
colors = [
    "#FF8A8A",
    "#86BCFF",
    "#33FDC0",
    "#FFFFAA",
    "#AAFFFF"
]

# }}}

# Utility functions {{{

def make_dataframe(experiments):
    """Converts XML experiments into a data frame with a row for each trial"""
    rows = []
    for e in experiments:
        exp_id = int(e.attrib["id"])
        age = int(e.xpath(".//question[@name='age']/text()")[0])
        degree = e.xpath(".//question[@name='education']/text()")[0]
        gender = e.xpath(".//question[@name='gender']/text()")[0]
        py_years = float(e.xpath(".//question[@name='python_years']/text()")[0])
        prog_years = float(e.xpath(".//question[@name='programming_years']/text()")[0])
        location = e.attrib["location"]

        for t in e.xpath(".//trial"):
            id = int(t.attrib["id"])
            base = t.attrib["base"]
            version = t.attrib["version"]

            grade_category = t.attrib["grade-category"]
            grade_value = int(t.attrib["grade-value"])

            started = datetime.strptime(t.attrib["started"], TIME_FORMAT)
            ended = datetime.strptime(t.attrib["ended"], TIME_FORMAT)
            response_duration = float(t.attrib["response-duration"])

            code_lines = int(t.xpath(".//metric[@name='code lines']/@value")[0])

            rows.append([id, exp_id, base, version, grade_value, grade_category,
                started, ended, response_duration, py_years, prog_years, age,
                degree, gender, location, code_lines])

    cols = ("id", "exp_id", "base", "version", "grade_value",
            "grade_category", "started", "ended", "response_duration",
            "py_years", "prog_years", "age", "degree", "gender", "location",
            "code_lines")

    df = pandas.DataFrame(rows, columns=cols)

    # Derived columns
    df["duration"] = df.apply(lambda r: (r["ended"] - r["started"]).total_seconds(), axis=1)
    df["response_percent"] = df.apply(lambda r: r["duration"] / float(r["response_duration"])
        if r["response_duration"] > 0 else 0, axis=1)

    df["common"] = df.grade_category.apply(lambda gc: "common" in gc)

    return df

# }}}

# Plotting {{{

def response_times(df, base, versions, threshold=300):
    """Boxplot of response times for different versions of a program"""
    rows = []
    for v in versions:
        v_rows = df[(df["base"] == base) & (df["version"] == v)]
        for _, row in v_rows.iterrows():
            duration = row["duration"]
            if duration <= threshold:
                rows.append([v, duration])

    resp_df = pandas.DataFrame(rows, columns=("version", "response_time"))
    x_labels = []
    for v, v_df in resp_df.groupby("version"):
        x_labels.append("{0}\n({1})".format(v, len(v_df)))
        print "{0} - mean: {1}, std: {2}".format(v,
            v_df.response_time.mean(), v_df.response_time.std())

    # Plot
    ax = resp_df.boxplot(column="response_time", by="version", figsize=(10, 5))
    fig = ax.figure
    fig.texts[0].set_text("")
    ax.set_title("Response times for {0}".format(base))
    ax.set_ylabel("Response time (s)")
    ax.set_xlabel("Version")
    ax.set_xticklabels(x_labels)
    fig.tight_layout()
    fig.savefig("plots/response_times-{0}.png".format(base))

def grade_pie(df, base, versions):
    """Pie chart of grade distribution for all versions of a program"""
    perfect = 0
    correct = 0
    common_error = 0
    incorrect = 0

    fig = pyplot.figure(figsize=(len(versions) * 5, 5))
    for i, v in enumerate(versions):
        v_rows = df[(df["base"] == base) & (df["version"] == v)]
        ax = fig.add_subplot(1, len(versions), i + 1)
        ax.set_title(v)
        for _, row in v_rows.iterrows():
            grade_category = row["grade_category"]
            grade_value = int(row["grade_value"])

            if grade_value == 10:
                perfect += 1
            elif grade_value >= 7:
                correct += 1
            elif "common" in grade_category:
                common_error += 1
            else:
                incorrect += 1

        bins = [perfect, correct, incorrect, common_error]
        patches, _, _ = ax.pie(bins, autopct="%1.1f%%", shadow=False, colors=colors)
        shade_axis(ax)

    #fig.suptitle(base)
    pyplot.tight_layout()
    pyplot.legend(patches, ["Perfect", "Correct", "Incorrect", "Common Error"],
            loc="lower left", ncol=2)

    pyplot.savefig("plots/grade_pie-{0}.png".format(base))

def demographics(exp_df):
    """Pie chart of participant demographics"""
    pyplot.figure(figsize=(12, 12))

    # Bin and plot ages
    ax = pyplot.subplot(2, 2, 1)
    ax.set_title("Ages", family=font_family, size=title_size)
    ages = exp_df["age"]
    age_bins = [0, 0, 0, 0, 0]
    age_bins[0] = len(ages[ages <= 20])
    age_bins[1] = len(ages[(20 < ages) & (ages < 25)])
    age_bins[2] = len(ages[(25 <= ages) & (ages <= 30)])
    age_bins[3] = len(ages[(30 < ages) & (ages <= 35)])
    age_bins[4] = len(ages[35 < ages])

    ax.pie(age_bins, labels=["18-20", "20-24", "25-30", "31-35", "> 35"],
            autopct="%1.1f%%", shadow=False, colors=colors)

    shade_axis(ax, size=text_size)

    # Bin and plot Python experience
    ax = pyplot.subplot(2, 2, 2)
    ax.set_title("Years of\nPython Experience", family=font_family, size=title_size)
    py = exp_df["py_years"]
    py_bins = [0, 0, 0, 0, 0]
    py_bins[0] = len(py[py < .5])
    py_bins[1] = len(py[(.5 <= py) & (py <= 1)])
    py_bins[2] = len(py[(1 < py) & (py <= 2)])
    py_bins[3] = len(py[(2 < py) & (py <= 5)])
    py_bins[4] = len(py[5 < py])

    ax.pie(py_bins, labels=["< 1/2", "1/2-1", "1-2", "2-5", "> 5"],
            autopct="%1.1f%%", shadow=False, colors=colors)

    shade_axis(ax, size=text_size)

    # Bin and plot programming experience
    ax = pyplot.subplot(2, 2, 3)
    ax.set_title("Years of\nProgramming Experience", family=font_family, size=title_size)
    prog = exp_df["prog_years"]
    prog_bins = [0, 0, 0, 0, 0]
    prog_bins[0] = len(prog[prog < 2])
    prog_bins[1] = len(prog[(2 <= prog) & (prog <= 3)])
    prog_bins[2] = len(prog[(3 < prog) & (prog <= 5)])
    prog_bins[3] = len(prog[(5 < prog) & (prog <= 10)])
    prog_bins[4] = len(prog[10 < prog])

    ax.pie(prog_bins, labels=["< 2", "2-3", "3-5", "5-10", "> 10"],
            autopct="%1.1f%%", shadow=False, colors=colors)

    shade_axis(ax, size=text_size)

    # Bin and plot education
    ax = pyplot.subplot(2, 2, 4)
    ax.set_title("Highest Degree\nReceived", family=font_family, size=title_size)
    degrees = exp_df["degree"].value_counts()

    ax.pie(degrees.values, labels=[x.capitalize() for x in degrees.keys()],
            autopct="%1.1f%%", shadow=False, colors=colors)

    shade_axis(ax, size=text_size)

    pyplot.tight_layout()
    pyplot.savefig("plots/demographics.png")

def grade_vs_experience(df):
    """Scatter plot of grade versus Python experience"""
    rows = []
    for _, exp_rows in df.groupby("exp_id"):
        rows.append([exp_rows.grade_value.sum(), exp_rows.py_years.values[0]])
    
    summary_df = pandas.DataFrame(rows, columns=("grade_value", "py_years"))
    print "Grade/experience correlation:"
    print summary_df[["grade_value", "py_years"]].corr()

    ax = summary_df.plot(x="py_years", y="grade_value", linestyle="none", marker="o")
    ax.set_xlabel("Years of Python experience")
    ax.set_ylabel("Grade")
    ax.grid()
    ax.set_title("Grade vs. Years of Python experience ({0})"\
        .format(len(summary_df)))
    ax.figure.savefig("plots/grade_vs_experience.png")

# }}}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("xml_file", type=str, help="Path to reponse data xml file")
    args = parser.parse_args()

    if not os.path.exists("plots"):
        os.makedirs("plots")

    # Parse in XML
    root = etree.parse(args.xml_file)
    experiments = root.xpath("//experiment")
    print "{0} experiments".format(len(experiments))

    # Convert to data frame
    trial_df = make_dataframe(experiments)
    print "{0} trials".format(len(trial_df))

    exp_df = trial_df.drop_duplicates("exp_id")

    print "\nGender:"
    print exp_df["gender"].value_counts()

    print "\nLocation:"
    print exp_df["location"].value_counts()

    print "\nGrade categories"
    print trial_df.grade_category.value_counts()
    print ""

    # Make overall plots
    print "\nCreating overall plots"
    grade_vs_experience(trial_df)
    demographics(exp_df)

    # Gather all program bases/versions
    bases = {}
    for _, row in trial_df.drop_duplicates(("base", "version")).iterrows():
        b = row["base"]
        v = row["version"]

        if not b in bases:
            bases[b] = set()

        bases[b].add(v)

    # Make individual program plots
    for b, vs in sorted(bases.iteritems(), key=lambda kv: kv[0]):
        print "Plotting {0}".format(b)
        vs = sorted(vs)
        grade_pie(trial_df, b, vs)
        response_times(trial_df, b, vs)
