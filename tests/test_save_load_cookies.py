import os

import pytest

import jira_context

_load_cookies = getattr(jira_context, '_load_cookies')
_save_cookies = getattr(jira_context, '_save_cookies')

FINAL_TEST_ANSWERS = (
    (dict(), dict()),
    (dict(JSESSIONID=1), dict()),
    (dict(a=1, JSESSIONID='1'), dict(JSESSIONID='1')),
    (dict(JSESSIONID='\0'), dict()),
    (dict(JSESSIONID='<html>'), dict()),
    (dict(JSESSIONID='ABC123;'), dict()),
    (dict(JSESSIONID='ABC123\\'), dict()),
    (dict(JSESSIONID='ABC123'), dict(JSESSIONID='ABC123')),
    ({'JSESSIONID': 'ABC123', 'crowd.token_key': 'DEF456\\'}, dict(JSESSIONID='ABC123')),
    ({'JSESSIONID': 'ABC123', 'crowd.token_key': 'DEF456'}, {'JSESSIONID': 'ABC123', 'crowd.token_key': 'DEF456'}),
)


def test_new_file(tmpdir):
    file_path = str(tmpdir.join('.jira_session_json'))
    assert not os.path.exists(file_path)
    assert dict() == _load_cookies(file_path)
    assert not os.path.exists(file_path)

    dict_object = dict(JSESSIONID='ABCDEF123456789')
    _save_cookies(file_path, dict_object)

    assert os.path.exists(file_path)
    assert dict(JSESSIONID='ABCDEF123456789') == _load_cookies(file_path)
    assert oct(os.stat(file_path).st_mode & 0o777) in ('0600', '0o600')


def test_existing_file(tmpdir):
    tmpdir_file = tmpdir.join('.jira_session_json')
    tmpdir_file.write_binary(os.urandom(10240))
    file_path = str(tmpdir_file)

    assert os.path.exists(file_path)
    assert oct(os.stat(file_path).st_mode & 0o777) not in ('0600', '0o600')
    assert dict() == _load_cookies(file_path)
    assert os.path.exists(file_path)

    dict_object = dict(JSESSIONID='ABCDEF123456789')
    _save_cookies(file_path, dict_object)

    assert os.path.exists(file_path)
    assert dict(JSESSIONID='ABCDEF123456789') == _load_cookies(file_path)
    assert oct(os.stat(file_path).st_mode & 0o777) in ('0600', '0o600')


def test_existing_empty_file(tmpdir):
    tmpdir_file = tmpdir.join('.jira_session_json')
    tmpdir_file.write('')
    file_path = str(tmpdir_file)

    assert os.path.exists(file_path)
    assert oct(os.stat(file_path).st_mode & 0o777) not in ('0600', '0o600')
    assert dict() == _load_cookies(file_path)
    assert os.path.exists(file_path)

    dict_object = dict(JSESSIONID='ABCDEF123456789')
    _save_cookies(file_path, dict_object)

    assert os.path.exists(file_path)
    assert dict(JSESSIONID='ABCDEF123456789') == _load_cookies(file_path)
    assert oct(os.stat(file_path).st_mode & 0o777) in ('0600', '0o600')


@pytest.mark.parametrize('input_dict,output_dict', FINAL_TEST_ANSWERS)
def test_dangerous_file(tmpdir, input_dict, output_dict):
    file_path = str(tmpdir.join('.jira_session_json'))
    _save_cookies(file_path, input_dict)
    assert output_dict == _load_cookies(file_path)
    assert oct(os.stat(file_path).st_mode & 0o777) in ('0600', '0o600')
