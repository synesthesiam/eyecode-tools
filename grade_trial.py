#!/usr/bin/env python

import argparse
from io import StringIO

MATCH_EXACT = 3
MATCH_LINES = 2
MATCH_VALUES = 1
MATCH_NONE = 0

CORRECT_EXACT = 10
CORRECT_LINES = 9
CORRECT_VALUES = 7
COMMON_EXACT = 4
COMMON_LINES = 3
COMMON_VALUES = 2

def common_errors(base, version):
    """Returns a list of common error responses for the given
    program base and version"""
    if base == "between":
        return ["[8, 7, 9]\n[1, 0, 8, 1]\n[8]"]
    elif base == "scope":
        return ["22"]
    elif base == "counting":
        return ["The count is 1\nThe count is 2\nThe count is 3\nThe count is 4\nDone counting"]
    elif base == "partition":
        if version == "balanced":
            return ["low\nlow\nhigh\nhigh"]
        elif (version == "unbalanced") or (version == "unbalanced_pivot"):
            return ["low\nlow\nhigh"]
    elif base == "overload":
        if version == "plusmixed":
            return ["7\n9\n\"53\"", "7\n9\n8"]
        elif version == "multmixed":
            return ["12\n14\n8"]
        elif version == "strings":
            return ["hibye\nstreetpenny\n8"]
    elif base == "funcall":
        return ["-60", "0", "-80"]
    elif base == "order":
        return ["5 2 10"]
    elif base == "whitespace":
        return ["0 5\n1 10\n2 15"]
    elif base == "initvar":
        if version == "bothbad":
            return ["0\n10"]
        elif version == "good":
            return ["1\n2\n3\n4\n1\n2\n3\n4"]
        elif version == "onebad":
            return ["24\n10"]
    return []

def grade_string(expected, actual):
    """Grades a single response against the true (actual) output.
    Possible return values are:
        * MATCH_EXACT (perfect match)
        * MATCH_LINES (correct number of lines, non-formatting characters match)
        * MATCH_VALUES (non-formatting characters match)
        * MATCH_NONE (no match)"""
    # Convert to universal newlines, strip extraneous whitespace
    expected_io = StringIO(unicode(expected.strip()), newline=None)
    actual_io = StringIO(unicode(actual.strip()), newline=None)

    expected_str = expected_io.read()
    actual_str = actual_io.read()

    # Pefect match
    if expected_str == actual_str:
        return MATCH_EXACT

    format_chars = ['[', ']', ',', ' ', '\n', '"', '\'']
    table = dict.fromkeys(map(ord, format_chars), None)

    expected_io.seek(0)
    expected_lines = [line.strip() for line in expected_io.readlines()]
    actual_io.seek(0)
    actual_lines = [line.strip() for line in actual_io.readlines()]

    # Remove blank lines
    removed_blanks = False

    if len(expected_lines) != len(actual_lines):
        actual_lines = [line for line in actual_lines if len(line.strip()) > 0]
        removed_blanks = True

    # Check for line by line exact/partial match
    if len(expected_lines) == len(actual_lines):
        exact_match = True
        partial_match = False

        for (e_line, a_line) in zip(expected_lines, actual_lines):
            if e_line != a_line:
                exact_match = False
                if (e_line.translate(table).lower() == a_line.translate(table).lower()):
                    partial_match = True
                else:
                    partial_match = False
                    break

        if exact_match:
            return MATCH_EXACT if not removed_blanks else MATCH_LINES
        elif partial_match:
            return MATCH_LINES

    # Check for partial match of values only
    if expected_str.translate(table).lower() == actual_str.translate(table).lower():
        return MATCH_VALUES

    return MATCH_NONE

def auto_grade(base, version, true_output, response):
    """Auto-grades a trial response against the true output. Response
    must either be correct or a common error (otherwise, a manual grade
    should have existed)"""
    category = "unknown"
    value = -1
    match = grade_string(true_output, response)

    # Try common errors
    if match == MATCH_NONE:
        for error_output in common_errors(base, version):
            match = grade_string(error_output, response)
            if match != MATCH_NONE:
                break

        # Common error
        category = "common "
        if match == MATCH_EXACT:
            category += "exact"
            value = COMMON_EXACT
        elif match == MATCH_LINES:
            category += "lines"
            value = COMMON_LINES
        elif match == MATCH_VALUES:
            category += "values"
            value = COMMON_VALUES
        else:
            raise ValueError("Invalid match value")
    else:
        # Correct answer
        category = "correct "
        if match == MATCH_EXACT:
            category += "exact"
            value = CORRECT_EXACT
        elif match == MATCH_LINES:
            category += "lines"
            value = CORRECT_LINES
        elif match == MATCH_VALUES:
            category += "values"
            value = CORRECT_VALUES
        else:
            raise ValueError("Invalid match value")

    return category, value

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=str, required=True, help="Program base")
    parser.add_argument("--version", type=str, required=True, help="Program version")
    parser.add_argument("--expected", type=str, required=True, help="Path to expected output text file")
    parser.add_argument("--actual", type=str, required=True, help="Path to actual output text file")
    args = parser.parse_args()

    response = open(args.actual, "r").read()
    true_output = open(args.expected, "r").read()

    try:
        category, value = auto_grade(args.base, args.version, true_output, response)
        print category, value
    except ValueError:
        print "Response must be manually graded"
