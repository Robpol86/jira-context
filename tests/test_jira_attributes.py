import base64
import re

import httpretty
import pytest

import jira_context
from jira_context import INPUT, JIRA

_save_cookies = getattr(jira_context, '_save_cookies')
_load_cookies = getattr(jira_context, '_load_cookies')


@pytest.mark.httpretty
def test_force_user(tmpdir):
    jira_context._prompt = lambda f, p: (0 / 0) if f == INPUT else 'pass'  # ZeroDivisionError if prompted for user.
    JIRA.COOKIE_CACHE_FILE_PATH = str(tmpdir.join('.jira_session_json'))
    JIRA.FORCE_USER = 'test_account'
    assert dict() == _load_cookies(JIRA.COOKIE_CACHE_FILE_PATH)

    def session_callback(request, _, headers):
        assert 'test_account:pass' == base64.b64decode(request.headers['Authorization'].split(' ')[-1]).decode('ascii')
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


@pytest.mark.httpretty
def test_user_can_abort_username(tmpdir):
    jira_context._prompt = lambda f, p: '' if f == INPUT else 'pass'
    JIRA.COOKIE_CACHE_FILE_PATH = str(tmpdir.join('.jira_session_json'))
    JIRA.USER_CAN_ABORT = False
    assert dict() == _load_cookies(JIRA.COOKIE_CACHE_FILE_PATH)

    def session_callback(request, _, headers):
        assert ':pass' == base64.b64decode(request.headers['Authorization'].split(' ')[-1]).decode('ascii')
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


@pytest.mark.httpretty
def test_user_can_abort_password(tmpdir):
    jira_context._prompt = lambda f, p: 'user' if f == INPUT else ''
    JIRA.COOKIE_CACHE_FILE_PATH = str(tmpdir.join('.jira_session_json'))
    JIRA.USER_CAN_ABORT = False
    assert dict() == _load_cookies(JIRA.COOKIE_CACHE_FILE_PATH)

    def session_callback(request, _, headers):
        assert 'user:' == base64.b64decode(request.headers['Authorization'].split(' ')[-1]).decode('ascii')
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
