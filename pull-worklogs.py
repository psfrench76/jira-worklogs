#!/usr/bin/env python3

from jira import JIRA
import keyring
from datetime import datetime
import pandas
import pytz
import yaml
import re

# Authentication token should be stored in system password manager (keychain for mac)
# jira-worklogs.token, with the username that is stored as system_user in the config
# using keyring in python terminal:
# >>> import keyring
# >>> keyring.set_password('jira-worklogs.token', 'username', 'token')

def jira_string_filter(input_string, time_zone="UTC"):
    match input_string:
        case str():
            if re.search(".*T.*:.*:.*\+", input_string):
                time_zone = pytz.timezone(time_zone)
                return datetime.strptime(input_string, '%Y-%m-%dT%H:%M:%S.%f%z').astimezone(time_zone)
    return input_string

def flatten_fields(fields_dict, issue_raw, worklog_dict=None, author_timezone="UTC"):
    flat_dict = {}
    for key, value in fields_dict.items():
        if key == "worklogs":
            flat_dict.update(flatten_fields(value, worklog_dict, author_timezone=author_timezone))
            continue

        match value:
            case str():
                try:
                    flat_dict[value] = jira_string_filter(issue_raw[key], author_timezone)
                except(KeyError):
                    flat_dict[value] = ""
            case dict():
                try:
                    flat_dict.update(flatten_fields(value, issue_raw[key], worklog_dict, author_timezone))
                except(KeyError):
                    flat_dict.update(flatten_fields(value, {}, worklog_dict, author_timezone))
    return flat_dict


with open('config.yaml', 'r') as config_file:
    config = yaml.safe_load(config_file)

user = config['system_user']

api_token = keyring.get_password('jira-worklogs.token', user)
user_email = config['jira_instance']['user_email']
jira_server = config['jira_instance']['url']

jira = JIRA(server=jira_server, basic_auth=(user_email, api_token))

# TODO:
#   - make "| xargs open" feature easier

jql_query = config['issue_query']
fields = config['fields']['issue']
search_fields = list(fields['fields'].keys())
jira_max_results = config['jira_instance']['max_results']

all_worklogs = []
list_length = 100
issues_processed = 0

while issues_processed < list_length:
    issues = jira.search_issues(jql_query, fields=search_fields, startAt=issues_processed, maxResults=jira_max_results)
    for issue in issues:
        worklogs = issue.fields.worklog.worklogs

        for worklog in worklogs:
            flat_issue = flatten_fields(fields, issue.raw, worklog.raw, worklog.author.timeZone)
            all_worklogs.append(flat_issue)

    list_length = issues.total
    issues_returned = len(issues)
    issues_processed = issues_processed + issues_returned

data_frame = pandas.DataFrame(all_worklogs)

now = datetime.now()
time_label = now.strftime('%Y%m%d_%H%M%S')
filepath = f'results/worklogs_{time_label}.csv'
data_frame.to_csv(filepath, index=False, date_format='%Y-%m-%d %H:%M:%S %Z')
print(filepath)
