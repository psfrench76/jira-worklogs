from jira import JIRA
import keyring
import getpass

# Authentication and instance details should be stored in system password manager (keychain for mac)
# jira-worklogs.token, jira-worklogs.email, and jira-worklogs.url are the service names
# the username for all three should be equivalent to the system username

user = getpass.getuser()
api_token = keyring.get_password('jira-worklogs.token', user)
user_email = keyring.get_password('jira-worklogs.email', user)
jira_server = keyring.get_password('jira-worklogs.url', user)

jira = JIRA(server=jira_server, basic_auth=(user_email, api_token))

# Temporary stuff

issue = jira.issue('OLP-543')
jql_query = 'key = OLP-543'
issues = jira.search_issues(jql_query)

print(issue.fields.summary)
print(issues)