from werkzeug.utils import get_content_type


class ResponseUsingMixin(object):
    """Add deferred setup for response objects."""

    def using(self, response=None,
                    status=None,
                    headers=None,
                    mimetype=None,
                    content_type=None,
                    direct_passthrough=None):
        """Convenience method that works like ``__init__`` on
        already-created instances. Useful with things that return response
        objects, for example ``return render(template).using(status=202)``."""

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
