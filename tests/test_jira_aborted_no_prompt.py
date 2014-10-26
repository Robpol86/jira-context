import re

import pytest
from pytest_httpretty import last_request, stub_get

import jira_context
from jira_context import JIRA

_save_cookies = getattr(jira_context, '_save_cookies')
_load_cookies = getattr(jira_context, '_load_cookies')


def test_aborted_before(tmpdir):
    JIRA.ABORTED_BY_USER = True
    JIRA.COOKIE_CACHE_FILE_PATH = str(tmpdir.join('.jira_session_json'))

    with JIRA() as j:
        assert j.ABORTED_BY_USER is True


def test_aborted_during_username(tmpdir):
    jira_context._prompt = lambda m, p: '' if m == raw_input else 'pass'
    JIRA.COOKIE_CACHE_FILE_PATH = str(tmpdir.join('.jira_session_json'))

    with JIRA() as j:
        assert j.ABORTED_BY_USER is True


def test_aborted_during_password(tmpdir):
    jira_context._prompt = lambda m, p: 'user' if m == raw_input else ''
    JIRA.COOKIE_CACHE_FILE_PATH = str(tmpdir.join('.jira_session_json'))

    with JIRA() as j:
        assert j.ABORTED_BY_USER is True


def test_no_prompt_no_cookies(tmpdir):
    JIRA.COOKIE_CACHE_FILE_PATH = str(tmpdir.join('.jira_session_json'))

    with JIRA(prompt_for_credentials=False) as j:
        assert j.ABORTED_BY_USER is False
        assert j.authentication_failed is True
        assert getattr(j, '_JIRA__authenticated_with_cookies') is False
        assert getattr(j, '_JIRA__authenticated_with_password') is False

    assert dict() == _load_cookies(JIRA.COOKIE_CACHE_FILE_PATH)


@pytest.mark.httpretty
def test_no_prompt_bad_cookies(tmpdir):
    JIRA.COOKIE_CACHE_FILE_PATH = str(tmpdir.join('.jira_session_json'))
    _save_cookies(JIRA.COOKIE_CACHE_FILE_PATH, dict(JSESSIONID='ABC123'))

    stub_get(re.compile('.*/serverInfo'), body='{"versionNumbers":[6,4,0]}')
    stub_get(re.compile('.*/session'), body='{}', status=401)

    with JIRA(prompt_for_credentials=False) as j:
        assert 'JSESSIONID=ABC123' == last_request().headers['Cookie']
        assert j.ABORTED_BY_USER is False
        assert j.authentication_failed is True
        assert getattr(j, '_JIRA__authenticated_with_cookies') is False
        assert getattr(j, '_JIRA__authenticated_with_password') is False

    assert dict(JSESSIONID='ABC123') == _load_cookies(JIRA.COOKIE_CACHE_FILE_PATH)


@pytest.mark.httpretty
def test_no_prompt_good_cookies(tmpdir):
    JIRA.COOKIE_CACHE_FILE_PATH = str(tmpdir.join('.jira_session_json'))
    _save_cookies(JIRA.COOKIE_CACHE_FILE_PATH, dict(JSESSIONID='ABC123'))

    stub_get(re.compile('.*/serverInfo'), body='{"versionNumbers":[6,4,0]}')
    stub_get(re.compile('.*/session'), body='{}', status=200)

    with JIRA(prompt_for_credentials=False) as j:
        assert 'JSESSIONID=ABC123' == last_request().headers['Cookie']
        assert j.ABORTED_BY_USER is False
        assert j.authentication_failed is False
        assert getattr(j, '_JIRA__authenticated_with_cookies') is True
        assert getattr(j, '_JIRA__authenticated_with_password') is False

    assert dict(JSESSIONID='ABC123') == _load_cookies(JIRA.COOKIE_CACHE_FILE_PATH)
