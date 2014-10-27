# jira-context

Do you have command line applications which interact with JIRA servers? Do your users have to enter their credentials
every time they run your applications? Are you unable to use OAuth because your command line application is open sourced
or you have no way of securing the consumer secret?

Hi, Robpol86 here for jira-context. The easy way to prompt for credentials and cache session cookies on your clients'
workstations.

`jira-context` is supported on Python 2.6, 2.7, 3.3, and 3.4.

[![Build Status](https://travis-ci.org/Robpol86/jira-context.svg?branch=master)]
(https://travis-ci.org/Robpol86/jira-context)
[![Coverage Status](https://img.shields.io/coveralls/Robpol86/jira-context.svg)]
(https://coveralls.io/r/Robpol86/jira-context)
[![Latest Version](https://pypip.in/version/jira-context/badge.png)]
(https://pypi.python.org/pypi/jira-context/)
[![Downloads](https://pypip.in/download/jira-context/badge.png)]
(https://pypi.python.org/pypi/jira-context/)
[![Download format](https://pypip.in/format/jira-context/badge.png)]
(https://pypi.python.org/pypi/jira-context/)
[![License](https://pypip.in/license/jira-context/badge.png)]
(https://pypi.python.org/pypi/jira-context/)

## Quickstart

Install:
```bash
pip install jira-context
```

## Usage

```python
# example.py
from __future__ import print_function
import sys
from jira_context import JIRA

server = 'https://jira.company.local'
query = 'assignee = currentUser() AND resolution = Unresolved'
if len(sys.argv) == 2:
    JIRA.FORCE_USER = sys.argv[1]

print('Connecting to: ' + server)
with JIRA(server=server) as j:
    if j.ABORTED_BY_USER:
        print('Aborted by user.', file=sys.stderr)
        sys.exit(1)
    issues = j.search_issues(query, maxResults=5)

for issue in issues:
    print(issue.key, issue.fields.summary)
```

```
$ python example.py
Connecting to: https://jira.company.local
JIRA username: does_not_exist
JIRA password:
Authentication failed or bad password, try again.
JIRA username:
Aborted by user.
$ python example.py $USER
Connecting to: https://jira.company.local
JIRA password:
FAKE-659 service solahart hp 082113812149
FAKE-620 Need new version to be compatible in Jira 6.3.1
FAKE-525 Half page become blank when Activity Stream gadget view as Wallboard
FAKE-468 create page and with custom fields
FAKE-022 As a burndown gadget I should support GH 6.0+
$ python example.py
Connecting to: https://jira.company.local
FAKE-659 service solahart hp 082113812149
FAKE-620 Need new version to be compatible in Jira 6.3.1
FAKE-525 Half page become blank when Activity Stream gadget view as Wallboard
FAKE-468 create page and with custom fields
FAKE-022 As a burndown gadget I should support GH 6.0+
```

## Class Attributes

### Persisted

These attributes/variables are persisted throughout the lifetime of the currently running process. If you've got two
`with` blocks and `ABORTED_BY_USER` becomes True in the first one, the second block will skip authentication.

Name | Description/Notes
:--- | :----------------
`ABORTED_BY_USER` | False by default. Becomes True if `USER_CAN_ABORT` is True and the user enters a blank username or password.
`COOKIE_CACHE_FILE_PATH` | File path to the cache file used to store the base64 encoded session cookie.
`FORCE_USER` | If set to a string, user won't be prompted for their username.
`USER_CAN_ABORT` | Set to False if you don't want the user to continue without a JIRA session if they enter a blank user/pass.

### Instance

These attributes are persisted only in the current JIRA() instance.

Name | Description/Notes
:--- | :----------------
`prompt_for_credentials` | Instantiate with False if you don't want the user prompted for credentials (useful in threads).
`authentication_failed` | Becomes True if `prompt_for_credentials` is False and cached cookies were invalid/missing.

## Changelog

#### 1.0.0

* Initial release.
