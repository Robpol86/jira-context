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

if len(sys.argv) == 2:
    JIRA.FORCE_USER = sys.argv[1]

with JIRA(server='https://jira.atlassian.com') as j:
    if j.ABORTED_BY_USER:
        print('Aborted by user.', file=sys.stderr)
        sys.exit(1)
    projects = [p.key for p in j.projects()]

for project in projects:
    print(project)
```

```
$ python example.py
JIRA username: does_not_exist
JIRA password:
Authentication failed or bad password, try again.
JIRA username:
Aborted by user.
```

## Changelog

#### 1.0.0

* Initial release.
