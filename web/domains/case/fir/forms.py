import structlog as logging
from django.forms.widgets import Textarea
from django.utils import timezone

from web.domains.case.fir.models import FurtherInformationRequest
from web.forms import ModelEditForm

logger = logging.getLogger(__name__)


class FurtherInformationRequestForm(ModelEditForm):
    def __init__(self, requested_by, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.requested_by = requested_by

    def save(self, commit=True):
        """
            Set request status/date before save
        """
        fir = super().save(commit=False)
        fir.status = FurtherInformationRequest.OPEN
        fir.requested_by = self.requested_by
        if commit:
            fir.save()
        return fir

    class Meta:
        model = FurtherInformationRequest
        fields = ["request_subject", "email_cc_address_list", "request_detail"]
        labels = {
            "email_cc_address_list": "Request CC Email Addresses",
            "files": "Documents",
            "requested_datetime": "Request Date",
        }

        help_texts = {
            "email_cc_address_list": """
                You may enter a list of email addresses to CC this email to.
                <br>
                Use a semicolon (<strong>;</strong>) to seperate multiple addresses.
                <br>
                <br>
                E.g. <span style="white-space:nowrap;">john@smith.com <strong>;</strong> \
                jane@smith.com</span>"""
        }


class FurtherInformationRequestResponseForm(ModelEditForm):
    def __init__(self, response_by, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.response_by = response_by

    def save(self, commit=True):
        """
            Set response status/date before save
        """
        fir = super().save(commit=False)
        fir.response_datetime = timezone.now()
        fir.status = FurtherInformationRequest.RESPONDED
        fir.response_by = self.response_by
        if commit:
            fir.save()
        return fir

    class Meta:
        model = FurtherInformationRequest
        fields = [
            "response_detail",
        ]
        labels = {
            "response_detail": "Response Details",
        }
        widgets = {
            "response_detail": Textarea({"rows": 5}),
        }
