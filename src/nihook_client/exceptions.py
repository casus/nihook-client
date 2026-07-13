"""
Exceptions raised by nihook-client.

All of them carry a human readable message and an 'exit_code' which the
command line entry points use when they turn an exception back into a
process exit status.
"""


class NihookClientError(Exception):
    """Base class for every error raised by this package."""

    exit_code = 1


class SchemaError(NihookClientError):
    """The input JSON schema cannot be mapped to a NocoDB table."""

    exit_code = -12


class ReservedColumnError(SchemaError):
    """The input JSON schema uses a key that this package reserves for itself."""

    exit_code = -3

    def __init__(self, column_name):
        super().__init__(
            f"special key '{column_name}' used in input JSON -- not allowed, rename there")
        self.column_name = column_name


class UnsupportedTypeError(SchemaError):
    """A key has a type that cannot be represented as a NocoDB column."""

    exit_code = -2

    def __init__(self, key, type_name):
        super().__init__(f"unhandled type '{type_name}' for key '{key}'")
        self.key = key
        self.type_name = type_name


class NocodbError(NihookClientError):
    """The NocoDB API rejected a request.

    'response' holds the decoded JSON body so callers can inspect the details
    beyond the message.
    """

    def __init__(self, message, response=None):
        super().__init__(message)
        self.response = response


def error_message_from_response(res, default="unknown error"):
    """Dig the human readable error message out of a NocoDB JSON response."""

    if not isinstance(res, dict):
        return default

    if 'msg' in res:
        return str(res['msg'])

    if 'message' in res:
        return str(res['message'])

    errors = res.get('errors')
    if errors:
        messages = [str(e.get('message', e)) if isinstance(e, dict) else str(e) for e in errors]
        return "; ".join(messages)

    return default
