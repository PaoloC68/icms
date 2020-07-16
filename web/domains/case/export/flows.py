import structlog as logging

from viewflow import flow
from viewflow.base import Flow, this

from web.viewflow.nodes import View

from . import models
from . import views

logger = logging.getLogger(__name__)


# FIXME: split this in two, separate flows for different export cases?
# FIXME: add programmatic start as well, have ExportApplicationCreateView
#        forward to the right one
class ExportApplicationFlow(Flow):
    process_template = "web/domains/case/export/partials/process.html"
    process_class = models.ExportApplicationProcess

    request = flow.Start(views.ExportApplicationCreateView).Next(this.prepare_application)

    prepare_application = (
        View(views.PrepareCertManufactureView).Assign(this.request.owner)
        # .Permission(IMP_CASE_OFFICER) # TODO: choose permissions
        # TODO: choose team
        .Next(this.end)
    )

    end = flow.End()
