from django.urls import include, path

from web.viewflow.viewset import FlowViewSet

from .flows import FurtherInformationRequestFlow

futher_information_request_urls = FlowViewSet(FurtherInformationRequestFlow).urls

app_name = "fir"

urlpatterns = [
    path("", include(futher_information_request_urls)),
]
