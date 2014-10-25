"""Cache JIRA basic authentication sessions to disk for console apps.

https://github.com/Robpol86/jira-context
https://pypi.python.org/pypi/jira-context
"""

from __future__ import print_function
import base64
from getpass import getpass
import json
import os
import sys

import jira.client
from jira.exceptions import JIRAError


def _load_cookies(file_path):
    """Read cached cookies from file.

    Positional arguments:
    file_path -- string representing the file path to where cookie data is to be stored on disk.

    Returns:
    Dict of cookies restored from file. Otherwise returns an empty dict.
    """
    # Check file.
    if not os.path.isfile(file_path) or not os.access(file_path, os.R_OK):
        return dict()

    # Read file.
    with open(file_path, 'rb') as f:
        contents = f.read(1024)
    if not contents:
        return dict()

    # Parse file.
    try:
        decoded = base64.b64decode(contents)
        parsed = json.loads(decoded)
        sanitized = dict((k, v) for k, v in parsed.items())  # TODO
    except (TypeError, ValueError):
        return dict()

    return sanitized


def _save_cookies(file_path, dict_object):
    """Cache cookies dictionary to file.

    Positional arguments:
    file_path -- string representing the file path to where cookie data is to be stored on disk.
    dict_object -- dict containing the current JIRA session via JIRA()._session.cookies.get_dict().
    """
    json_string = json.dumps(dict_object)
    encoded = base64.b64encode(json_string)
    old_mask = os.umask(0077)
    with open(file_path, 'wb') as f:
        f.seek(0)
        f.truncate()
        f.write(encoded)
        f.flush()
        if hasattr(os, 'fdatasync'):
            os.fdatasync(f.fileno())  # Linux only.
    os.umask(old_mask)


class JIRA(jira.client.JIRA):
    """."""

    ABORTED_BY_USER = False
    COOKIE_CACHE_FILE_PATH = os.path.join(os.path.expanduser('~'), '.jira_session_json')
    FORCE_USER = None
    MESSAGE_AUTH_ERROR = 'Error occurred, try again.'
    MESSAGE_AUTH_FAILURE = 'Authentication failed or bad password, try again.'
    PROMPT_PASS = 'JIRA password: '
    PROMPT_USER = 'JIRA username: '

    def __init__(self, prompt=True, *args, **kwargs):
        self.authentication_failed = False
        self.prompt_for_credentials = prompt
        self.__delayed_args = (args, kwargs)
        self.__cached_cookies = _load_cookies(self.COOKIE_CACHE_FILE_PATH)

    def __enter__(self):
        """Entering context, ask user for credentials if cookies fail."""
        if self.ABORTED_BY_USER:
            return self

        # Prompt for credentials until valid ones are given, user aborts, or user presses ctrl+c.
        while True:
            if self.__cached_cookies:
                # No need to prompt for credentials.
                auth_result = self.__authenticate(None)
            elif not self.prompt_for_credentials:
                # Unable to authenticate.
                self.authentication_failed = True
                return self
            else:
                username = self.FORCE_USER or raw_input(self.PROMPT_USER)
                if not username:
                    JIRA.ABORTED_BY_USER = True
                    return self
                password = getpass(self.PROMPT_PASS)
                if not password:
                    JIRA.ABORTED_BY_USER = True
                    return self
                auth_result = self.__authenticate((username, password))

            if auth_result == 'cookies':
                # Attempt to restore cookies failed, cookies have been deleted by __authenticate. Silently retrying.
                continue
            if auth_result == 'success':
                return self
            if auth_result == 'invalid':
                print(self.MESSAGE_AUTH_FAILURE, file=sys.stderr)
            print(self.MESSAGE_AUTH_ERROR, file=sys.stderr)

    def __exit__(self):
        """Caches cookies to disk if they have changed."""
        if self.ABORTED_BY_USER or self.__cached_cookies:
            # Either the session was aborted by the user, or resumed session was used. No new cookies.
            return
        self.__cached_cookies = self._session.cookies.get_dict()
        if not self.__cached_cookies:
            # No cookies to cache.
            return
        _save_cookies(self.COOKIE_CACHE_FILE_PATH, self.__cached_cookies)

    def __authenticate(self, basic_auth):
        """Attempt to authenticate to the JIRA server with either cookies or basic authentication. Handles errors too.

        Positional arguments:
        basic_auth -- tuple to be passed to jira.client.JIRA.__init__() parent class. First string is the username,
            second string is the password.

        Returns:
        Four possible strings. 'error' on unknown/generic errors, 'cookies' on auth failures with cached cookies,
        'invalid' on auth failures with basic_auth username and password, and 'success' on successful authentication.
        """
        try:
            # Call delayed __init__() method from parent class.
            args, kwargs = self.__delayed_args
            super(JIRA, self).__init__(basic_auth=basic_auth, *args, **kwargs)

            # Inject cached cookies.
            for k, v in self.__cached_cookies.items():
                self._session.cookies.set(k, v)

            # Try to get a list of JIRA projects from the server. Might raise JIRAError.
            if self.__cached_cookies and not self.projects():
                # Loaded cached cookies but there are no JIRA projects, something is wrong.
                raise JIRAError(401, 'Expired cookies.', '')

        except JIRAError as e:
            if e.status_code != 401:
                # Some unknown error occurred.
                result = 'error'
            elif self.__cached_cookies:
                # User has not entered a password. Probably invalid cookies, probably first iteration.
                result = 'cookies'
            else:
                # JIRAError raised HTTP 401 and cookies are not cached, invalid password.
                result = 'invalid'
            self.__delete_cookies()
            return result

        return 'success'

    def __delete_cookies(self):
        """Deletes cached cookie file and clears dict from class instance."""
        self.__cached_cookies.clear()
        try:
            os.remove(self.COOKIE_CACHE_FILE_PATH)
        except OSError:
            pass
