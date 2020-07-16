from django.urls import path, include
from web.viewflow.viewset import FlowViewSet

from . import flows

export_case_urls = FlowViewSet(flows.ExportApplicationFlow).urls

app_name = "export"

urlpatterns = [
    path("", include(export_case_urls)),
]
