"""Cache JIRA basic authentication sessions to disk for console apps.

Designed for command line programs/scripts as a context manager. When used, the JIRA class attempts to resume a
previously saved session stored on disk (by default in the user's home directory). If the session has expired or fails,
the user will be prompted for their credentials, and upon authentication the session cookie is cached to disk. The main
goal of this library is to avoid having the user repeatedly enter their JIRA credentials every time they use a console
application, either within the same process or when they re-run an application which uses this library.

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

__author__ = '@Robpol86'
__license__ = 'MIT'
__version__ = '1.0.0'

_PY3 = bool(sys.version_info[0] == 3)
INPUT = input if _PY3 else raw_input


def _load_cookies(file_path):
    """Read cached cookies from file. Filters out everything but JSESSIONID.

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
        decoded = base64.b64decode(contents).decode('ascii')
        parsed = json.loads(decoded)
        sanitized = dict((k, v) for k, v in parsed.items() if k == 'JSESSIONID' and v.isalnum())
    except (AttributeError, TypeError, ValueError):
        return dict()

    return sanitized


def _save_cookies(file_path, dict_object):
    """Cache cookies dictionary to file. Filters out everything but JSESSIONID.

    Positional arguments:
    file_path -- string representing the file path to where cookie data is to be stored on disk.
    dict_object -- dict containing the current JIRA session via JIRA()._session.cookies.get_dict().
    """
    # Encode dict_object.
    sanitized = dict((k, v) for k, v in dict_object.items() if k == 'JSESSIONID' and str(v).isalnum())
    json_string = json.dumps(sanitized)
    encoded = base64.b64encode(json_string.encode('ascii'))

    # Remove existing files.
    try:
        os.remove(file_path)
    except OSError:
        pass

    # Write file.
    old_mask = os.umask(0o077)
    with open(file_path, 'wb') as f:
        f.seek(0)
        f.truncate()
        f.write(encoded)
        f.flush()
        if hasattr(os, 'fdatasync'):
            os.fdatasync(f.fileno())  # Linux only.
    os.umask(old_mask)


def _prompt(func, prompt):
    """Prompts user for data. This is for testing."""
    return func(prompt)


class JIRA(jira.client.JIRA):
    """jira.client.JIRA subclass, basically makes the original JIRA library context-aware.

    Authentication happens not during instantiation but when the context is entered (using the `with` statement). Cookie
    caching only happens on context exit (after the `with` code block) if authentication was successful and a new cookie
    was returned by the JIRA server.

    Class variables (persists until the application terminates):
    ABORTED_BY_USER -- False by default. Set to True if USER_CAN_ABORT is True and the user enters a blank username or
        password. If this variable is ever set to True, this class will never authenticate (both cookie or password
        methods).
    COOKIE_CACHE_FILE_PATH -- file path to the cache file used to store the base64 encoded session cookie.
    FORCE_USER -- if set to a string, user won't be prompted for their username. Value of this variable will be used
        instead.
    USER_CAN_ABORT -- by default if a user enters a blank username or password, it is understood that they do not want
        to authenticate to the JIRA server. Set this to False to send blank user/passwords to the JIRA server which will
        inevitably result in an authentication error, causing the program to prompt the user for their credentials
        again.

    Instance variables:
    prompt_for_credentials -- by default user will be prompted for credentials if cached cookies fail. If False the user
        won't be prompted for credentials. If cached cookies are valid then the program may be able to authenticate if
        they are not invalid. If cached cookies are not available or are invalid/expired and this is True, user will not
        be authenticated and `authentication_failed` will be set to True. This variable is useful to set during
        instantiation when used within a thread.
    authentication_failed -- will be set to True if authentication was not successful and user is not prompted for
        credentials.
    """

    ABORTED_BY_USER = False
    COOKIE_CACHE_FILE_PATH = os.path.join(os.path.expanduser('~'), '.jira_session_json')
    FORCE_USER = None
    MESSAGE_AUTH_ERROR = 'Error occurred, try again.'
    MESSAGE_AUTH_FAILURE = 'Authentication failed or bad password, try again.'
    PROMPT_PASS = 'JIRA password: '
    PROMPT_USER = 'JIRA username: '
    USER_CAN_ABORT = True

    def __init__(self, prompt_for_credentials=True, *args, **kwargs):
        self.authentication_failed = False
        self.prompt_for_credentials = prompt_for_credentials
        self.__authenticated_with_cookies = False  # True if cached cookies were used to authenticate successfully.
        self.__authenticated_with_password = False  # True if cached cookies were not used to authenticate successfully.
        self.__cached_cookies = _load_cookies(self.COOKIE_CACHE_FILE_PATH)
        self.__delayed_args = (args, kwargs)

    def __enter__(self):
        """Entering context, ask user for credentials if cookies fail."""
        if self.ABORTED_BY_USER:
            return self

        # Prompt for credentials until valid ones are given, user aborts, or user presses ctrl+c.
        while True:
            if self.__cached_cookies:
                # No need to prompt for credentials.
                authenticated = self.__authenticate()
            elif not self.prompt_for_credentials:
                # Unable to authenticate.
                self.authentication_failed = True
                return self
            else:
                username = self.FORCE_USER or _prompt(INPUT, self.PROMPT_USER)
                if not username and self.USER_CAN_ABORT:
                    JIRA.ABORTED_BY_USER = True
                    return self
                password = _prompt(getpass, self.PROMPT_PASS)
                if not password and self.USER_CAN_ABORT:
                    JIRA.ABORTED_BY_USER = True
                    return self
                authenticated = self.__authenticate((username, password))

            if authenticated:
                return self

    def __exit__(self, *_):
        """Caches cookies to disk if they have changed."""
        if self.ABORTED_BY_USER or self.authentication_failed:
            # Unable to authenticate, not saving cookies.
            return
        if self.__authenticated_with_cookies or not self.__cached_cookies:
            # Previous session resumed from cached cookies or no cookies to cache, not saving cookies.
            return
        _save_cookies(self.COOKIE_CACHE_FILE_PATH, self.__cached_cookies)

    def __authenticate(self, basic_auth=None):
        """Attempt to authenticate to the JIRA server with either cookies or basic authentication. Handles errors too.

        If self.prompt_for_credentials is True, prints error messages to stderr.

        Keyword arguments:
        basic_auth -- tuple to be passed to jira.client.JIRA.__init__() parent class. First string is the username,
            second string is the password. None if using cookie authentication.

        Returns:
        True if successfully authenticated, False otherwise.
        """
        try:
            # Call delayed __init__() method from parent class.
            args, kwargs = self.__delayed_args
            super(JIRA, self).__init__(basic_auth=basic_auth, *args, **kwargs)

            # Inject cached cookies.
            for k, v in self.__cached_cookies.items():
                self._session.cookies.set(k, v)

            # Validate cookies or credentials. May raise JIRAError.
            self.session()

        except JIRAError as e:
            if e.status_code != 401:
                # Some unknown error occurred.
                if self.prompt_for_credentials and self.MESSAGE_AUTH_ERROR:
                    print(self.MESSAGE_AUTH_ERROR, file=sys.stderr)
            elif self.__cached_cookies:
                # User has not entered a password. Probably invalid cookies, probably first iteration.
                pass
            else:
                # JIRAError raised HTTP 401 and cookies are not cached, invalid password.
                if self.prompt_for_credentials and self.MESSAGE_AUTH_FAILURE:
                    print(self.MESSAGE_AUTH_FAILURE, file=sys.stderr)
            self.authentication_failed = True
            self.__cached_cookies = dict()
            self.__authenticated_with_cookies = False
            self.__authenticated_with_password = False
            return False

        # Authentication was successful if this is reached.
        self.authentication_failed = False
        self.__cached_cookies = self._session.cookies.get_dict() if basic_auth else self.__cached_cookies
        self.__authenticated_with_cookies = not bool(basic_auth)
        self.__authenticated_with_password = bool(basic_auth)
        return True
