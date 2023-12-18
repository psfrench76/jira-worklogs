## Description
This program is intended for Jira Software Cloud users who want to track Work Logs on issues in aggregate, and
import this data into a spreadsheet for analysis, visualization, etc.

It uses the Jira API for data retrieval, Keyring for token storage, YAML for configuration management, and Pandas for 
CSV conversion.

The fields requested are configurable by the user. All data retrieved is saved to a CSV in the results directory.

In addition to fields on the worklogs, you can also use any issue or parent issue field which is present on the issue
that the worklogs are connected to.

The time this takes to run will be proportionate to the number of issues (not necessarily the number of worklogs) and
the number of queries needed to retrieve the Jira data. If you are experiencing long lag times with large numbers of
issues, you could try increasing the `jira_instance.max_results` setting in config.yaml to increase the search page size.
This will decrease the run time to an extent.

## Quickstart

1. Install dependencies for python (developed in python 3.10)
```shell
pip install keyring
pip install jira
pip install pytz
pip install pandas
pip install yaml
```
2. Set up a Jira API token (see here: https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/)
3. Store the token securely in your system keyring (example below, using the python terminal and the keyring 
package -- be sure to replace the `SYSTEM_USERNAME` and `TOKEN` values
```python
import keyring
keyring.set_password('jira-worklogs.token', 'SYSTEM_USERNAME', 'TOKEN')
```
4. Copy sample-config.yaml to config.yaml:
```shell
cp sample-config.yaml config.yaml
```
5. Open config.yaml in a text editor and edit (at least) these settings. `url` should be the url of your Jira instance,
`user_email` should be the user email address that is tied to your Jira API token, and `system_user` should be the OS
user who owns the token from step 3. 
```yaml
jira_instance:
   url: "https://[myinstance].atlassian.net"
   user_email: "[user]@[mycompany.com]"
...
system_user: "[sysuser]"
```
6. Make any other desired modifications to the field request list in config.yaml, underneath this section:
```yaml
fields:
  issue:
    id: "issue id"
    key: "issue key"
    fields:
      ...
```
Note: This should not be undertaken without a general understanding of YAML, Jira fields and API, Python, etc. The structure of 
the fields requested must directly mirror the structure of the Jira API response 
(see https://developer.atlassian.com/cloud/jira/platform/rest/v2/api-group-issue-search for samples) The key in the 
(key, value) pair is the actual Jira field id, and the value is the column header which will be displayed in the 
resulting CSV. The column headers can be edited without consequence. Fields can be added or removed without breaking, 
as long as the structure remains unchanged and identical to the API. **Caution:** for fields that have a value that is an 
object (such as issuetype, status, etc), in order to use the name, it will need to be identified as a sub-item in 
this list. (see example below)
```yaml
fields:
  duedate: "issue due date"
  issuetype:
    name: "issue type"
```

## Running the program
You can run the program from the command line within the installation directory, using:
```shell
python pull-worklogs.py
```
Or you can automatically open the results in your default csv editor with:
```shell
python pull-worklogs.py | xargs open
```
