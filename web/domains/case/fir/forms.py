from django import forms
from django.forms.widgets import Textarea

from web.domains.case.fir.models import FurtherInformationRequest
from web.forms import ModelDisplayForm, ModelEditForm


class FurtherInformationRequestForm(ModelEditForm):
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
                E.g. <span style="white-space:nowrap;">john@smith.com <strong>;</strong> jane@smith.com</span>"""
        }


class FurtherInformationRequestDisplayForm(FurtherInformationRequestForm, ModelDisplayForm):

    requested_datetime = forms.CharField(
        label=FurtherInformationRequestForm.Meta.labels["requested_datetime"]
    )
    requested_by = forms.CharField()

    def get_top_buttons(self):
        """
        buttons to show on the form's top row
        """
        if self.instance.status == FurtherInformationRequest.DRAFT:
            return ["edit"]

        return []

    def get_bottom_buttons(self):
        """
        buttons to show on the form's bottom row
        """
        if self.instance.status == FurtherInformationRequest.OPEN:
            return ["withdraw"]

        return []

    class Meta(FurtherInformationRequestForm.Meta):
        config = {
            "requested_datetime": {
                "padding": {"right": None},
                "label": {"cols": "three"},
                "input": {"cols": "two"},
            },
            "requested_by": {"label": {"cols": "two"}, "input": {"cols": "two"},},
        }


class FurtherInformationRequestResponseForm(ModelEditForm):
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
