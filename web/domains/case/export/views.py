import structlog as logging

from django.db import transaction
from django.shortcuts import redirect
from django.urls import reverse_lazy

from web.views import ModelCreateView
from web.viewflow.mixins import SimpleStartFlowMixin

from .forms import NewExportApplicationForm
from .models import ExportApplication, ExportApplicationType, CertificateOfManufactureApplication

from viewflow.flow.views import UpdateProcessView

from . import forms

logger = logging.get_logger(__name__)

permissions = "web.IMP_CERT_EDIT_APPLICATION"


class PrepareCertManufactureView(UpdateProcessView):
    template_name = "web/domains/case/export/prepare-com.html"
    form_class = forms.CertManufactureForm

    def post(self, request, *args, **kwargs):
        # TODO: what logic to put here
        # case = self.activation.process.case
        # case.status = models.ExportApplication.COMPLETED

        return super().post(request, *args, **kwargs)

    def get_form(self):
        if self.request.POST:
            form = self.form_class(
                self.request, data=self.request.POST, instance=self.get_object().export_application
            )
        else:
            form = self.form_class(self.request, instance=self.get_object().export_application)

        return form

    # TODO: there's another page we need to go to
    # def get_success_url(self):
    #     return reverse("workbasket")


class ExportApplicationCreateView(SimpleStartFlowMixin, ModelCreateView):
    template_name = "web/domains/case/export/create.html"
    model = ExportApplication
    success_url = reverse_lazy("home")
    cancel_url = reverse_lazy("home")
    form_class = NewExportApplicationForm
    page_title = "Create Certificate Application"
    permission_required = permissions

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = context.get("form")

        if form:
            app_type = form["application_type"].data

            if app_type == str(ExportApplicationType.CERT_MANUFACTURE):
                msg = """Certificates of Manufacture are applicable only to
                pesticides that are for export only and not on free sale on the
                domestic market."""
            elif app_type == str(ExportApplicationType.CERT_FREE_SALE):
                msg = """If you are supplying the product to a client in the
                UK/EU then you do not require a certificate. Your client will
                need to apply for a certificate if they subsequently export it
                to one of their clients outside of the EU."""
            else:
                msg = None

            context["cert_msg"] = msg

        # FIXME: this is weird
        context["activation"] = self.activation

        return context

    def get_form(self):
        if hasattr(self, "form"):
            return self.form

        if self.request.POST:
            self.form = NewExportApplicationForm(self.request, data=self.request.POST)
        else:
            self.form = NewExportApplicationForm(self.request)

        return self.form

    # TODO: check if we need this function
    def post(self, request, *args, **kwargs):
        # see web/static/web/js/main.js::initialize
        if request.POST and request.POST.get("change", None):
            return super().get(request, *args, **kwargs)

        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        with transaction.atomic():
            data = form.cleaned_data

            if data["application_type"].pk == ExportApplicationType.CERT_FREE_SALE:
                # TODO: implement
                raise Exception("Not implemented")
                # model_class = ...
            elif data["application_type"].pk == ExportApplicationType.CERT_MANUFACTURE:
                model_class = CertificateOfManufactureApplication

            appl = model_class(
                application_type=data["application_type"],
                exporter=data["exporter"],
                exporter_office=data["exporter_office"],
                created_by=self.request.user,
                last_updated_by=self.request.user,
                submitted_by=self.request.user,
            )
            appl.save()

            self.activation.process.export_application = appl

            return redirect(self.get_success_url())
