import structlog as logging
from django.utils.decorators import method_decorator
from viewflow import flow
from viewflow.base import Flow, this

from web.viewflow.nodes import View

from . import models, views

__all__ = ["FurtherInformationRequestFlow"]


logger = logging.getLogger(__name__)


def send_fir_email(activation):
    pass


def send_fir_response_email(activation):
    pass


class FurtherInformationRequestFlow(Flow):
    """
        Further Information Request

        FIRs are used as parallel flows of different flows and depends on the parent process
        for FIR view permissions.

        Parent process must use .mixins.FurtherInformationRequestMixin for the functional
        interface to read necessary permissions for FIR.

    """

    process_template = "web/domains/case/fir/partials/process.html"
    process_class = models.FurtherInformationRequestProcess

    request = flow.StartFunction(this.start_fir).Next(this.notify_contacts)

    notify_contacts = flow.Handler(send_fir_email).Next(this.respond)

    respond = (
        View(views.FurtherInformationRequestResponseView)
        .Team(lambda p: p.parent_process.get_fir_response_team())
        .Next(this.notify_case_officers)
        .Permission(lambda a: a.process.parent_process.get_fir_response_permission())
    )

    notify_case_officers = flow.Handler(send_fir_response_email).Next(this.review)

    review = (
        View(views.FurtherInformationRequestReviewView)
        .Permission(lambda a: a.process.parent_process.get_fir_starter_permission())
        .Next(this.end)
    )

    end = flow.End()

    @method_decorator(flow.flow_start_func)
    def start_fir(self, activation, parent_process, further_information_request):
        logger.debug("Starting fir", parent_process=parent_process)
        activation.prepare()
        activation.process.parent_process = parent_process
        activation.process.further_information_request = further_information_request
        activation.done()
