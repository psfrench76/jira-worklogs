## Quickstart

1. Install the keyring package for python:
```shell
pip install keyring
```
2. Set up a Jira API token (see here: https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/)
3. Store the token securely in your system keyring (example for mac below, using the python terminal and the keyring 
package -- be sure to replace the `SYSTEM_USERNAME` and `TOKEN` values
```python
import keyring
keyring.set_password('jira-worklogs.token', 'SYSTEM_USERNAME', 'TOKEN')
```
4. Copy sample-config.yaml to config.yaml:\
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
Note: This should not be undertaken without a general understanding of YAML, Jira fields, Python, etc. The structure of 
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