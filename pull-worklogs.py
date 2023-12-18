#!/usr/bin/env python3

from jira import JIRA
import keyring
import getpass
from datetime import datetime
import pandas
import pytz

# Authentication and instance details should be stored in system password manager (keychain for mac)
# jira-worklogs.token, jira-worklogs.email, and jira-worklogs.url are the service names
# the username for all three should be equivalent to the system username

user = getpass.getuser()
api_token = keyring.get_password('jira-worklogs.token', user)
user_email = keyring.get_password('jira-worklogs.email', user)
jira_server = keyring.get_password('jira-worklogs.url', user)

jira = JIRA(server=jira_server, basic_auth=(user_email, api_token))

# TODO:
#   - define "relevant issues"
#   - design JQL query to pull "relevant issues"
#   - consider efficiency/batching/query limits/etc for large queries (since we'll be doing that)
#   - make "| xargs open" feature easier

jql_query = 'key = OLP-543 OR key = OLP-546'
issues = jira.search_issues(jql_query)

all_worklogs = []

for issue in issues:
    worklogs = issue.fields.worklog.worklogs
    for worklog in worklogs:
        author = worklog.author
        user_local_tz = pytz.timezone(author.timeZone)

        time_started = datetime.strptime(worklog.started, '%Y-%m-%dT%H:%M:%S.%f%z').astimezone(user_local_tz)
        time_created = datetime.strptime(worklog.created, '%Y-%m-%dT%H:%M:%S.%f%z').astimezone(user_local_tz)

        all_worklogs.append({
            "id": worklog.id,
            "created": time_created,
            "started": time_started,
            "timeSpentSeconds": worklog.timeSpentSeconds,
            "comment": worklog.comment,
            "author.emailAddress": author.emailAddress,
            "author.displayName": author.displayName,
            "issue.id": issue.id,
            "issue.type": issue.fields.issuetype,
            "issue.key": issue.key,
            "issue.summary": issue.fields.summary,
            "issue.currentStatus": issue.fields.status
        })

data_frame = pandas.DataFrame(all_worklogs)

now = datetime.now()
time_label = now.strftime('%Y%m%d_%H%M%S')
filepath = f'results/worklogs_{time_label}.csv'
data_frame.to_csv(filepath, index=False, date_format='%Y-%m-%d %H:%M:%S %Z')
print(filepath)
