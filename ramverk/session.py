import errno
import os

from werkzeug.contrib.securecookie import SecureCookie
from werkzeug.utils                import cached_property
from ramverk.rendering             import json


class SecureJSONCookie(SecureCookie):
    """A :class:`~werkzeug.contrib.securecookie.SecureCookie` serialized as
    JSON which is safer than pickle."""

    serialization_method = json


class EnvironmentSessionMixin(object):
    """Environment mixin adding a signed session cookie."""

    @cached_property
    def session(self):
        """A :class:`SecureJSONCookie` signed with the configured
        :attr:`~SessionMixin.settings.secret_key`."""
        return SecureJSONCookie.load_cookie(
            self.request, secret_key=self.application.settings.secret_key)


class SessionMixin(object):
    """Application mixin for automatic saving of the
    :attr:`~EnvironmentSessionMixin.session` as needed."""

    def respond(self):
        response = super(SessionMixin, self).respond()
        self.local.session.save_cookie(response)
        return response


class SecretKey(object):
    """Lazily read `filename` for a secret key, writing `bytes` random
    bytes to it if it doesn't exist."""

    def __init__(self, filename, bytes=256):
        self.filename, self.bytes = filename, bytes

    def __str__(self):
        try:
            return self.key
        except AttributeError:
            try:
                with open(self.filename, 'rb') as stream:
                    self.key = stream.read()
            except IOError as e:
                if e.errno != errno.ENOENT:
                    raise
                self.key = os.urandom(self.bytes)
                with open(self.filename, 'wb') as stream:
                    stream.write(self.key)
            return self.key
