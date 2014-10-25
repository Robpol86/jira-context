from httmock import all_requests, HTTMock

import jira_context
from jira_context import JIRA

_save_cookies = getattr(jira_context, '_save_cookies')


def test_aborted(tmpdir):
    JIRA.ABORTED_BY_USER = True
    JIRA.COOKIE_CACHE_FILE_PATH = str(tmpdir.join('.jira_session_json'))

    with JIRA() as j:
        assert j.ABORTED_BY_USER is True


def test_no_prompt_no_cookies(tmpdir):
    JIRA.ABORTED_BY_USER = False
    JIRA.COOKIE_CACHE_FILE_PATH = str(tmpdir.join('.jira_session_json'))

    with JIRA(prompt_for_credentials=False) as j:
        assert j.ABORTED_BY_USER is False
        assert j.authentication_failed is True


def test_no_prompt_bad_cookies(tmpdir):
    JIRA.ABORTED_BY_USER = False
    JIRA.COOKIE_CACHE_FILE_PATH = str(tmpdir.join('.jira_session_json'))
    _save_cookies(JIRA.COOKIE_CACHE_FILE_PATH, dict(JSESSIONID='ABC123'))

    @all_requests
    def response_content(url, _):
        if url.path.endswith('/serverInfo'):
            reply = dict(status_code=200, content='{"versionNumbers":[6,4,0]}')
        elif url.path.endswith('/project'):
            reply = dict(status_code=401, content='')
        else:
            raise RuntimeError
        return reply

    with HTTMock(response_content):
        with JIRA(prompt_for_credentials=False) as j:
            assert j.ABORTED_BY_USER is False
            assert j.authentication_failed is True


def test_no_prompt_good_cookies_no_projects(tmpdir):
    JIRA.ABORTED_BY_USER = False
    JIRA.COOKIE_CACHE_FILE_PATH = str(tmpdir.join('.jira_session_json'))
    _save_cookies(JIRA.COOKIE_CACHE_FILE_PATH, dict(JSESSIONID='ABC123'))

    @all_requests
    def response_content(url, _):
        if url.path.endswith('/serverInfo'):
            reply = dict(status_code=200, content='{"versionNumbers":[6,4,0]}')
        elif url.path.endswith('/project'):
            reply = dict(status_code=200, content='{}')
        else:
            raise RuntimeError
        return reply

    with HTTMock(response_content):
        with JIRA(prompt_for_credentials=False) as j:
            assert j.ABORTED_BY_USER is False
            assert j.authentication_failed is True


def test_no_prompt_good_cookies_yes_projects(tmpdir):
    JIRA.ABORTED_BY_USER = False
    JIRA.COOKIE_CACHE_FILE_PATH = str(tmpdir.join('.jira_session_json'))
    _save_cookies(JIRA.COOKIE_CACHE_FILE_PATH, dict(JSESSIONID='ABC123'))

    @all_requests
    def response_content(url, _):
        if url.path.endswith('/serverInfo'):
            reply = dict(status_code=200, content='{"versionNumbers":[6,4,0]}')
        elif url.path.endswith('/project'):
            reply = dict(status_code=200, content='[{"name": "Clover", "key": "CLOV", "id": "11772"}]')
        else:
            raise RuntimeError
        return reply

    with HTTMock(response_content):
        with JIRA(prompt_for_credentials=False) as j:
            assert j.ABORTED_BY_USER is False
            assert j.authentication_failed is False
