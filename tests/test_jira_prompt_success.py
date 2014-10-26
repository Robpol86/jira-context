from __future__ import print_function
import base64
import re

import httpretty
import pytest

import jira_context
from jira_context import JIRA

_save_cookies = getattr(jira_context, '_save_cookies')
_load_cookies = getattr(jira_context, '_load_cookies')


def _prompt(func, prompt):
    print(prompt)
    return 'user' if func == raw_input else 'pass'


@pytest.mark.httpretty
def test_no_cookies(tmpdir, capsys):
    jira_context._prompt = _prompt
    JIRA.ABORTED_BY_USER = False
    JIRA.COOKIE_CACHE_FILE_PATH = str(tmpdir.join('.jira_session_json'))
    assert dict() == _load_cookies(JIRA.COOKIE_CACHE_FILE_PATH)

    def session_callback(request, _, headers):
        assert 'user:pass' == base64.b64decode(request.headers['Authorization'].split(' ')[-1])
        headers['Set-Cookie'] = 'JSESSIONID=ABC123; Path=/'
        return 200, headers, '{}'
    httpretty.register_uri(httpretty.GET, re.compile('.*/serverInfo'), body='{"versionNumbers":[6,4,0]}')
    httpretty.register_uri(httpretty.POST, re.compile('.*/session'), body=session_callback)

    with JIRA() as j:
        assert j.ABORTED_BY_USER is False
        assert j.authentication_failed is False
        assert getattr(j, '_JIRA__authenticated_with_cookies') is False
        assert getattr(j, '_JIRA__authenticated_with_password') is True

    assert dict(JSESSIONID='ABC123') == _load_cookies(JIRA.COOKIE_CACHE_FILE_PATH)
    stdout, stderr = capsys.readouterr()
    assert 'JIRA username: \nJIRA password: \n' == stdout
    assert '' == stderr
