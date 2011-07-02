from werkzeug.utils import get_content_type


class DeferredResponseInitMixin(object):
    """Add a method for reinitializing response instances."""

    def using(self, response=None, status=None, headers=None,
              mimetype=None, content_type=None, direct_passthrough=None):
        """Convenience method that works like :meth:`__init__` for responses
        that have already been created. Particularly useful as a complement
        to the rendering machinery, for example ``return render('json',
        error='authentication required').using(status=401)``."""

        if headers is not None:
            self.headers.extend(headers)

        if content_type is None:
            if mimetype is not None:
                mimetype = get_content_type(mimetype, self.charset)
            content_type = mimetype
        if content_type is not None:
            self.headers['Content-Type'] = content_type

        if status is not None:
            if isinstance(status, (int, long)):
                self.status_code = status
            else:
                self.status = status

        if direct_passthrough is not None:
            self.direct_passthrough = direct_passthrough

        if response is not None:
            if isinstance(response, basestring):
                self.data = response
            else:
                self.response = response

        return self


from ramverk.inventory import members
__all__ = members[__name__]
