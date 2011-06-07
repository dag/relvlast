class TemplatingMixin(object):
    """Add common functionality for templating to an application."""

    def create_template_context(self, overrides):
        """Create a context mapping to render a template
        in, including `overrides`. Override to add globals. Includes
        `request`, `url` and `path` from the application, and the
        application as `app`, by default."""
        context = dict(app=self,
                       request=self.request,
                       url=self.url,
                       path=self.path)
        context.update(overrides)
        return context
