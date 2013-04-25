# eyeCode Tools

A collection of tools for analyzing data from the [eyeCode experiment](http://arxiv.org/abs/1304.5257).
Please cite the linked paper if you use this data set!

Author: Michael Hansen (mihansen@indiana.edu)

## Scripts

There are two main scripts for the data analysis:

1. `grade_trial.py` - Attempts to automatically grade a single trial (see code for a list of common errors)
2. `response_stats.py` - Plots results and computes some simple stats

## Data Format

The eyeCode response data set is available in the `data` directory as an XML file.
The format of the response data XML is described below.

* `<experiments>` - top-level element
    * `created` - date and time when the file was created (format = %Y-%m-%d %H:%M:%S)
    * `<experiment>` - a single experiment (10 trials)
        * `started` - date and time when experiment started (including surveys, format = %Y-%m-%d %H:%M:%S)
        * `ended` - date and time when experiment ended (including surveys, format = %Y-%m-%d %H:%M:%S)
        * `<questions>` - all survey questions
            * `<question>` - a single survey question
                * `name` - name of question, one of:
                    * **age** - Participant's age in years
                    * **correct** - How many programs did you correctly predict? Response is one of "few", "half", "most".
                    * **difficulty** - How hard were the programs? Response is one of "easy", "medium", "hard".
                    * **education** - What is the highest degree you've received? Response is one of "none", "bachelors", "masters", "phd", "other".
                    * **gender** - Participant's gender. Response is one of "male", "female", "unreported"
                    * **major** - Are you (or were you) a Computer Science major? Response is one of "no", "current", "past".
                    * **programming_years** - Years of overall programming experience (may be fractional)
                    * **python_years** - Years of Python experience (may be fractional)
                * `value` - participant's answer
        * `<trials>` - all trials (should be 10, unless some were discarded)
            * `<trial>` - single trial with one program
                * `started` - date and time when trial started (format = %Y-%m-%d %H:%M:%S)
                * `ended` - date and time when trial ended (format = %Y-%m-%d %H:%M:%S)
                * `language` - should always be python
                * `order` - numerical ordering of the trial (starting at 0)
                * `base` - program base type (there were 10 total base types)
                * `version` - version of the program (2-3 per base)
                * `grade-value` - response quality from 0-10
                * `grade-category` - category of grade, one of:
                    * **correct exact** - response matched correct output, character-for-character
                    * **correct lines** - response formatting was off, but had the right values and number of lines
                    * **correct values** - response values matched, but not formatting or lines
                    * **common \*** - response was incorrect, but matched a common error (exact/lines/values same as **correct**)
                    * **manual** - response was graded manually
                * `response-duration` - number of seconds between first and last response keystrokes
            * `<metrics>` - code metrics for this trial's program
                * `<metric>` - single code metric
                    * `name` - name of metric. One of:
                        * **code chars** - number of characters in the program
                        * **code lines** - number of lines in the program
                        * **cyclomatic complexity** - McCabe's CC metric
                        * **halstead effort** - _E_ from Halstead software metrics
                        * **halstead volume** - _V_ from Halstead software metrics
                        * **output chars** - number of characters in the true output
                        * **output lines** - number of lines in the true output
            * `<true-output>` - what the program actually outputs
            * `<predicted-output>` - the participant's predicted output
