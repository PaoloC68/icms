#!/usr/bin/env python
# -*- coding: utf-8 -*-
import structlog as logging
from django.conf import settings
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View
from s3chunkuploader.file_handler import s3_client

from web.domains.case.access.models import (
    AccessRequest,
    ImporterAccessRequestProcess,
    FurtherInformationRequest,
)
from web.domains.file.models import File
from web.domains.template.models import Template
from web.utils import FilevalidationService, url_path_join
from web.utils.s3upload import InvalidFileException, S3UploadService
from web.utils.virus import ClamAV, InfectedFileException
from web.views.mixins import PostActionMixin

from .forms import FurtherInformationRequestDisplayForm, FurtherInformationRequestForm

logger = logging.getLogger(__name__)


class FurtherInformationRequestView(PostActionMixin, View):
    """
    Access Request Further Information Request

    This view class handles all actions that can be performed on a FIR
    """

    template_name = "web/access-request/access-request-fir-list.html"
    FIR_TEMPLATE_CODE = "IAR_RFI_EMAIL"

    def get(self, request, process_id):
        """
        Lists all FIRs associated to the access request

        Params:
            process_id - Access Request id
        """
        return render(request, self.template_name, self.get_context_data(process_id))

    def edit(self, request, process_id, *args, **kwargs):
        """
        Edits the FIR selected by the user.
        The selected FIR comes from the id property in the request body

        Params:
            process_id - Access Request id
        """

        data = request.POST if request.POST else None
        if not data or "id" not in data:
            return HttpResponseBadRequest("Invalid body received")

        fir_id = int(data["id"])

        return render(
            request, self.template_name, self.get_context_data(process_id, selected_fir=fir_id)
        )

    def set_fir_status(self, id, status):
        """
        Helper function to set and save a FIR status

        returns the changed FIR
        """
        model = FurtherInformationRequest.objects.get(pk=id)
        model.status = status
        model.save()

        return model

    def withdraw(self, request, process_id):
        """
        Marks the FIR as withdrawn

        Params:
            process_id - Access Request id
        """
        self.set_fir_status(request.POST["id"], FurtherInformationRequest.DRAFT)
        return redirect("access:fir", process_id=process_id)

    def send(self, request, process_id):
        """
        Marks the FIR as open
        @todo: send the actual email

        Params:
            process_id - Access Request id
        """
        self.set_fir_status(request.POST["id"], FurtherInformationRequest.OPEN)
        return redirect("access:fir", process_id=process_id)

    def delete(self, request, process_id):
        """
        Marks the FIR as deleted and sets it as inactive

        Params:
            process_id - Access Request id
        """
        model = self.set_fir_status(request.POST["id"], FurtherInformationRequest.DELETED)
        model.is_active = False
        model.save()

        return redirect("access:fir", process_id=process_id)

    @csrf_exempt
    def save(self, request, process_id, *args, **kwargs):
        """
        Saves the FIR being editted by the user

        user is redirected to list view if no file actions are performed, otherwise user is redirected
        to edit view

        Params:
            process_id - Access Request id
        """

        model = FurtherInformationRequest.objects.get(pk=request.POST["id"])
        form = FurtherInformationRequestForm(data=request.POST, instance=model)

        if not form.is_valid():
            return render(
                request,
                self.template_name,
                self.get_context_data(process_id, selected_fir=model.id, form=form),
            )

        form.save()

        if "uploaded_file" in request.FILES:
            self.upload(request, process_id)
            return self.edit(request, process_id)

        if "delete_file_id" in request.POST:
            self.delete_file(request.POST["delete_file_id"])
            return self.edit(request, process_id)

        if "restore_file_id" in request.POST:
            self.restore_file(request.POST["restore_file_id"])
            return self.edit(request, process_id)

        return redirect("access:fir", process_id=process_id)

    def new(self, request, process_id):
        """
        Creates a new FIR and associates it with the current access request then display the FIR form
        so the user can edit data

        Params:
            process_id - Access Request id
        """
        access_request = AccessRequest.objects.get(pk=process_id)
        try:
            template = Template.objects.get(template_code=self.FIR_TEMPLATE_CODE, is_active=True)
        except Exception as e:
            logger.warn(
                'could not fetch templat with code "%s" - reason %s'
                % (self.FIR_TEMPLATE_CODE, str(e))
            )
            template = Template()

        instance = FurtherInformationRequest()
        instance.requested_by = request.user
        instance.request_detail = template.get_content(
            {
                "CURRENT_USER_NAME": self.request.user.full_name,
                "REQUESTER_NAME": access_request.submitted_by.full_name,
            }
        )
        instance.save()

        access_request.further_information_requests.add(instance)

        return render(
            request, self.template_name, self.get_context_data(process_id, selected_fir=instance.id)
        )

    def upload(self, request, process_id):
        data = request.POST if request.POST else None
        if not data or "id" not in data:
            return HttpResponseBadRequest("Invalid body received")

        uploaded_file = request.FILES["uploaded_file"]

        try:
            file_size = 0
            file_path = ""
            error_message = ""

            upload_service = S3UploadService(
                s3_client=s3_client(),
                virus_scanner=ClamAV(
                    settings.CLAM_AV_USERNAME, settings.CLAM_AV_PASSWORD, settings.CLAM_AV_URL
                ),
                file_validator=FilevalidationService(),
            )

            file_path = upload_service.process_uploaded_file(
                settings.AWS_STORAGE_BUCKET_NAME,
                uploaded_file,
                url_path_join(settings.PATH_STORAGE_FIR, data["id"]),
            )

            file_size = uploaded_file.size

        except (InvalidFileException, InfectedFileException) as e:
            error_message = str(e)
        except Exception:
            error_message = "Unknown error uploading file"

        file_model = File()
        file_model.filename = uploaded_file.original_name
        file_model.content_type = uploaded_file.content_type
        file_model.browser_content_type = uploaded_file.content_type
        file_model.description = ""
        file_model.file_size = file_size
        file_model.path = file_path
        file_model.error_message = error_message
        file_model.created_by = request.user
        file_model.save()

        fir = FurtherInformationRequest.objects.get(pk=request.POST["id"])
        fir.files.add(file_model)
        fir.save()

    def delete_file(self, file_id):
        file_model = File.objects.get(pk=file_id)
        file_model.is_active = False
        file_model.save()

    def restore_file(self, file_id):
        file_model = File.objects.get(pk=file_id)
        file_model.is_active = True
        file_model.save()

    def create_display_or_edit_form(self, fir, selected_fir, form):
        """
        This function either returns an Further Information Request (FIR) form, or a read only version of it.

        By default returns a read only version of the FIR form (for display puposes).

        If `fir.id` is is the same as `selected_fir` then a "editable" version of the form is returned

        Params:
            fir - FurtherInformationRequest model
            selected_fir - id of the FIR the user is editing (or None)
            form - the form the user has submitted (or None, if present the form is returned instead of creating a new one)
        """
        if selected_fir and fir.id == selected_fir:
            return form if form else FurtherInformationRequestForm(instance=fir)

        return FurtherInformationRequestDisplayForm(
            instance=fir,
            initial={
                "requested_datetime": fir.date_created_formatted().upper(),
                "requested_by": fir.requested_by.full_name,
            },
        )

    def get_context_data(self, process_id, selected_fir=None, form=None, *args, **kwargs):
        """
        Helper function to generate context data to be sent to views

        Params:
            process_id - Access Request id
            selected_fir - id of the FIR the user is editing (or None)
            form - the form the user has submitted (or None, if present the form is returned instead of creating a new one)
        """
        process = ImporterAccessRequestProcess.objects.get(pk=process_id)
        items = (
            process.access_request.further_information_requests.exclude(
                status=FurtherInformationRequest.DELETED
            )
            .order_by("pk")
            .reverse()
        )

        return {
            "fir_list": [
                self.create_display_or_edit_form(fir, selected_fir, form) for fir in items
            ],
            "activation": {  # keeping the same format as viewflow, so sidebar works seamlessly
                "process": process,
            },
        }
