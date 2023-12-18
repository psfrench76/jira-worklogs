#!/usr/bin/env python3

# TODO:
#   - make "./pull-worklogs.py | xargs open" usage easier

from jira import JIRA
import keyring
from datetime import datetime
import pandas
import pytz
import yaml
import re


# This is intended as a full-service input filter function -- any other systematic value manipulation should
# happen here. Strings which match Jira's standard date format are converted to a python datetime object.
def jira_string_filter(input_string, time_zone="UTC"):
    match input_string:
        case str():
            if re.search(".*T.*:.*:.*\+", input_string):
                time_zone = pytz.timezone(time_zone)
                return datetime.strptime(input_string, '%Y-%m-%dT%H:%M:%S.%f%z').astimezone(time_zone)
    return input_string


# Takes a field dictionary (loaded from the config file), a jira response object (as a raw python dict), which is either
# all or a portion of a single issue, and a worklog object which is passed to use when encountering worklog fields.
# author_timzone is to help with timezone conversions into worklog author's local time (default behavior).
#
# Processes fields_dict recursively -- each sub-dictionary is passed to flatten_fields to flatten "from the bottom up."
# The worklog must be passed separately as issues are the primary iterable object and worklog entries are a sublist,
# but we are converting to a list of worklogs in the end, so each issue must be parsed
# one or more times while each worklog entry will be processed once.
def flatten_fields(fields_dict, response_raw, worklog_raw=None, author_timezone="UTC"):
    flat_dict = {}
    # key will be the jira field id, and value will be the config value for that field -- either a dict (representing
    # a sub-object) or a string (which is the column label to use in the end result)
    for key, value in fields_dict.items():
        if key == "worklogs":
            # here is where we use worklog_raw, and we pass it up to the response_raw parameter on the next pass
            flat_dict.update(flatten_fields(value, worklog_raw, author_timezone=author_timezone))
            continue

        match value:
            case str():
                try:
                    flat_dict[value] = jira_string_filter(response_raw[key], author_timezone)
                except(KeyError):
                    flat_dict[value] = ""  # when a non-object field is not included in the response, use empty string
            case dict():
                try:
                    flat_dict.update(flatten_fields(value, response_raw[key], worklog_raw, author_timezone))
                except(KeyError):
                    # when a sub-object field is not included in the response, use empty response dict and recurse
                    # again, to preserve column labels
                    flat_dict.update(flatten_fields(value, {}, worklog_raw, author_timezone))
    return flat_dict


with open('config.yaml', 'r') as config_file:
    config = yaml.safe_load(config_file)

# Load all configs
system_user = config['system_user']
jira_token = keyring.get_password('jira-worklogs.token', system_user)
jira_email = config['jira_instance']['user_email']
jira_url = config['jira_instance']['url']
jira_issue_query = config['issue_query']
jira_issue_fields = config['fields']['issue']
jira_search_fields = list(jira_issue_fields['fields'].keys())
jira_max_results = config['jira_instance']['max_results']

jira = JIRA(server=jira_url, basic_auth=(jira_email, jira_token))
all_worklogs = []
issue_list_length = 100
issues_processed = 0

# Iterate through each page of Jira results
while issues_processed < issue_list_length:
    issues = jira.search_issues(jira_issue_query, fields=jira_search_fields,
                                startAt=issues_processed, maxResults=jira_max_results)  # returns: ResultList

    # Iterate through all issues in this page
    for issue in issues:
        worklogs = issue.fields.worklog.worklogs

        # Iterate through each worklog, and build a flattened representation including issue data
        for worklog in worklogs:
            flat_worklog = flatten_fields(jira_issue_fields, issue.raw, worklog.raw, worklog.author.timeZone)
            all_worklogs.append(flat_worklog)

    issue_list_length = issues.total
    issues_returned = len(issues)
    issues_processed = issues_processed + issues_returned

now = datetime.now()
time_label = now.strftime('%Y%m%d_%H%M%S')
filepath = f'results/worklogs_{time_label}.csv'

# Use pandas to convert Python list to csv
data_frame = pandas.DataFrame(all_worklogs)
data_frame.to_csv(filepath, index=False, date_format=config['output_date_format'])

# print filepath for use in pipe ('./pull-worklogs.py | xargs open' for mac)
print(filepath)
