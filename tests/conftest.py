import pytest

import jira_context
from jira_context import JIRA


@pytest.fixture(autouse=True)
def reset_jira():
    jira_context._prompt = lambda f, p: 'user' if f == raw_input else 'pass'

    JIRA.ABORTED_BY_USER = False
    JIRA.COOKIE_CACHE_FILE_PATH = None
    JIRA.FORCE_USER = None
    JIRA.MESSAGE_AUTH_ERROR = 'Error occurred, try again.'
    JIRA.MESSAGE_AUTH_FAILURE = 'Authentication failed or bad password, try again.'
    JIRA.PROMPT_PASS = 'JIRA password: '
    JIRA.PROMPT_USER = 'JIRA username: '
    JIRA.USER_CAN_ABORT = True

    JIRA.DEFAULT_OPTIONS['server'] = 'http://localhost/jira'
