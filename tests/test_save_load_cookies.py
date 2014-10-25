import os

import jira_context

_load_cookies = getattr(jira_context, '_load_cookies')
_save_cookies = getattr(jira_context, '_save_cookies')


def test_new_file(tmpdir):
    jira_context.JIRA.COOKIE_CACHE_FILE_PATH = str(tmpdir.join('.jira_session_json'))
    assert not os.path.exists(jira_context.JIRA.COOKIE_CACHE_FILE_PATH)
    assert dict() == _load_cookies(jira_context.JIRA.COOKIE_CACHE_FILE_PATH)
    assert not os.path.exists(jira_context.JIRA.COOKIE_CACHE_FILE_PATH)

    dict_object = dict(a=1, JSESSIONID='ABCDEF123456789')
    _save_cookies(jira_context.JIRA.COOKIE_CACHE_FILE_PATH, dict_object)

    assert os.path.exists(jira_context.JIRA.COOKIE_CACHE_FILE_PATH)
    assert dict(JSESSIONID='ABCDEF123456789') == _load_cookies(jira_context.JIRA.COOKIE_CACHE_FILE_PATH)
    assert '0600' == oct(os.stat(jira_context.JIRA.COOKIE_CACHE_FILE_PATH).st_mode & 0777)


def test_existing_file(tmpdir):
    tmpdir_file = tmpdir.join('.jira_session_json')
    tmpdir_file.write_binary(os.urandom(10240))
    jira_context.JIRA.COOKIE_CACHE_FILE_PATH = str(tmpdir_file)

    assert os.path.exists(jira_context.JIRA.COOKIE_CACHE_FILE_PATH)
    assert '0600' != oct(os.stat(jira_context.JIRA.COOKIE_CACHE_FILE_PATH).st_mode & 0777)
    assert dict() == _load_cookies(jira_context.JIRA.COOKIE_CACHE_FILE_PATH)
    assert os.path.exists(jira_context.JIRA.COOKIE_CACHE_FILE_PATH)

    dict_object = dict(a=1, JSESSIONID='ABCDEF123456789')
    _save_cookies(jira_context.JIRA.COOKIE_CACHE_FILE_PATH, dict_object)

    assert os.path.exists(jira_context.JIRA.COOKIE_CACHE_FILE_PATH)
    assert dict(JSESSIONID='ABCDEF123456789') == _load_cookies(jira_context.JIRA.COOKIE_CACHE_FILE_PATH)
    assert '0600' == oct(os.stat(jira_context.JIRA.COOKIE_CACHE_FILE_PATH).st_mode & 0777)
