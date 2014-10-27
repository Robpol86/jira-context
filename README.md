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
if len(sys.argv) == 2:
    JIRA.FORCE_USER = sys.argv[1]

print('Connecting to: ' + server)
with JIRA(server=server) as j:
    if j.ABORTED_BY_USER:
        print('Aborted by user.', file=sys.stderr)
        sys.exit(1)
    issues = j.search_issues('assignee = currentUser() AND resolution = Unresolved', maxResults=5)

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
$
```

## Changelog

#### 1.0.0

* Initial release.
