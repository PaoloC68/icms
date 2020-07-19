class FurtherInformationProcessMixin(object):
    """
        A process mixin to be used by processes that needs parallel Further Information
        Requests


        See: web/domains/case/access/models.py for example usage with
        Importer/Exporter Access Request
    """

    def get_fir_response_permission(self):
        """
            Returns permission required to respond to a Further Information Request
        """
        raise NotImplementedError

    def get_fir_response_team(self):
        """
            Returns the team FIR is to be requested from

            Team in addition with response permission protects FIR response task
        """
        raise NotImplementedError

    def get_fir_starter_permission(self):
        """
            Returns permission required to start/review/close fir
        """
        raise NotImplementedError
