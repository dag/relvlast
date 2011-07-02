members = dict(

    application =
        """
        BaseApplication
        """,

    compiling =
        """
        CompilerMixinBase
        EnvironmentCompilerMixin
        """,

    environment =
        """
        BaseEnvironment
        """,

    fullstack =
        """
        Application
        Environment
        Request
        Response
        TemplateContext
        """,

    genshi =
        """
        CompactHTMLTemplate
        CompactTemplate
        GenshiMixin
        GenshiRenderer
        HTMLTemplate
        """,

    local =
        """
        Proxy
        UnboundContextError
        current
        get_current
        stack
        """,

    logbook =
        """
        LogbookHandlerMixin
        LogbookLoggerMixin
        """,

    paver =
        """
        routes
        serve
        shell
        """,

    rendering =
        """
        BaseTemplateContext
        JSONMixin
        RenderingEnvironmentMixin
        RenderingMixinBase
        TemplatingMixinBase
        """,

    routing =
        """
        AbstractEndpoint
        MethodDispatch
        URLHelpersMixin
        URLMapAdapterMixin
        URLMapMixin
        connect
        delete
        get
        head
        options
        patch
        post
        put
        route
        router
        trace
        """,

    scss =
        """
        SCSSMixin
        """,

    session =
        """
        SecretKey
        SecureJSONCookie
        SessionMixin
        """,

    transaction =
        """
        TransactionMixin
        TransactionalMixinBase
        """,

    utils =
        """
        Bunch
        Configurable
        EagerCachedProperties
        InitFromArgs
        ReprAttributes
        args
        has
        super
        """,

    venusian =
        """
        VenusianMixin
        configurator
        decorator
        """,

    wrappers =
        """
        DeferredResponseInitMixin
        """,

    wsgi =
        """
        SharedDataMixin
        middleware
        mixin
        """,

    zodb =
        """
        ZODBConnectionMixin
        ZODBStorageMixin
        """,
    )


from werkzeug.datastructures import ImmutableList
members = dict(('ramverk.' + module, ImmutableList(names.split()))
               for (module, names) in members.iteritems())
