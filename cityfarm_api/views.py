from rest_framework import views as rest_views

class APIView(rest_views.APIView):
    """
    :class:`~rest_framework.views.APIView subclass that modifies :meth:`initial`
    to call :meth:`check`. This lets subclasses define additional checks to be
    performed on each request that don't fit cleanly into any of the standard
    categories: authentication, permissions, and throttles.
    """
    def initial(self, *args, **kwargs):
        super().initial(*args, **kwargs)
        self.check()

    def check(self):
        """ There are no additional checks by default """
        pass
