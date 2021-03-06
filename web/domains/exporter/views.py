from django.urls import reverse_lazy

from web.domains.team.mixins import ContactsManagementMixin
from web.views import ModelCreateView, ModelDetailView, ModelFilterView, ModelUpdateView
from web.views.actions import Archive, Edit, Unarchive

from .forms import ExporterEditForm, ExporterFilter
from .models import Exporter

permissions = "web.IMP_MAINTAIN_ALL"


class ExporterListView(ModelFilterView):
    template_name = "web/domains/exporter/list.html"
    filterset_class = ExporterFilter
    model = Exporter
    permission_required = permissions
    page_title = "Maintain Exporters"

    class Display:
        fields = ["name"]
        fields_config = {"name": {"header": "Exporter Name"}}
        actions = [Archive(), Unarchive(), Edit()]


class ExporterEditView(ContactsManagementMixin, ModelUpdateView):
    template_name = "web/domains/exporter/edit.html"
    form_class = ExporterEditForm
    success_url = reverse_lazy("exporter-list")
    cancel_url = success_url
    model = Exporter
    permission_required = permissions


class ExporterCreateView(ModelCreateView):
    template_name = "web/domains/exporter/create.html"
    form_class = ExporterEditForm
    success_url = reverse_lazy("exporter-list")
    cancel_url = success_url
    model = Exporter
    permission_required = permissions
    page_title = "Create Exporter"


class ExporterDetailView(ModelDetailView):
    template_name = "web/domains/exporter/view.html"
    form_class = ExporterEditForm
    cancel_url = reverse_lazy("exporter-list")
    model = Exporter
    permission_required = permissions
