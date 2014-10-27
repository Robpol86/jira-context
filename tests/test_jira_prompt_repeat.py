import base64
import re

import httpretty
import pytest

import jira_context
from jira_context import JIRA

_save_cookies = getattr(jira_context, '_save_cookies')
_load_cookies = getattr(jira_context, '_load_cookies')


@pytest.mark.httpretty
def test_bad_cookies_bad_password_x2_good_password_success(tmpdir, capsys):
    JIRA.COOKIE_CACHE_FILE_PATH = str(tmpdir.join('.jira_session_json'))
    _save_cookies(JIRA.COOKIE_CACHE_FILE_PATH, dict(JSESSIONID='ABC000'))

    def first_session_callback(request, _, headers):
        assert 'Authorization' not in request.headers
        assert 'JSESSIONID=ABC000' == request.headers['Cookie']
        return 401, headers, '{}'

    def second_and_third_session_callback(request, _, headers):
        assert 'user:pass' == base64.b64decode(request.headers['Authorization'].split(' ')[-1]).decode('ascii')
        return 401, headers, '{}'

    def fourth_session_callback(request, _, headers):
        assert 'user:pass' == base64.b64decode(request.headers['Authorization'].split(' ')[-1]).decode('ascii')
        headers['Set-Cookie'] = 'JSESSIONID=ABC123; Path=/'
        return 200, headers, '{}'

    responses = [httpretty.Response(body=f) for f in (
        second_and_third_session_callback, second_and_third_session_callback, fourth_session_callback
    )]
    httpretty.register_uri(httpretty.GET, re.compile('.*/serverInfo'), body='{"versionNumbers":[6,4,0]}')
    httpretty.register_uri(httpretty.GET, re.compile('.*/session'), body=first_session_callback)
    httpretty.register_uri(httpretty.POST, re.compile('.*/session'), responses=responses)

    with JIRA() as j:
        assert j.ABORTED_BY_USER is False
        assert j.authentication_failed is False
        assert getattr(j, '_JIRA__authenticated_with_cookies') is False
        assert getattr(j, '_JIRA__authenticated_with_password') is True

    assert dict(JSESSIONID='ABC123') == _load_cookies(JIRA.COOKIE_CACHE_FILE_PATH)
    stdout, stderr = capsys.readouterr()
    assert '' == stdout
    assert ('Authentication failed or bad password, try again.\nAuthentication failed or bad password, try again.\n' ==
            stderr)


@pytest.mark.httpretty
def test_unknown_error_give_up(tmpdir, capsys):
    JIRA.COOKIE_CACHE_FILE_PATH = str(tmpdir.join('.jira_session_json'))
    assert dict() == _load_cookies(JIRA.COOKIE_CACHE_FILE_PATH)

    def session_callback(request, _, headers):
        assert 'user:pass' == base64.b64decode(request.headers['Authorization'].split(' ')[-1]).decode('ascii')
        jira_context._prompt = lambda *_: ''  # Simulate an empty user/pass on the next iteration.
        return 500, headers, '{}'
    httpretty.register_uri(httpretty.GET, re.compile('.*/serverInfo'), body='{"versionNumbers":[6,4,0]}')
    httpretty.register_uri(httpretty.POST, re.compile('.*/session'), body=session_callback)

    with JIRA() as j:
        assert j.ABORTED_BY_USER is True
        assert j.authentication_failed is True
        assert getattr(j, '_JIRA__authenticated_with_cookies') is False
        assert getattr(j, '_JIRA__authenticated_with_password') is False

    assert dict() == _load_cookies(JIRA.COOKIE_CACHE_FILE_PATH)
    stdout, stderr = capsys.readouterr()
    assert '' == stdout
    assert ('Error occurred, try again.\n' == stderr)
