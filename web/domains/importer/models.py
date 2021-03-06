from django.db import models

from web.domains.office.models import Office
from web.domains.team.models import BaseTeam
from web.domains.user.models import User
from web.models.mixins import Archivable

from .roles import IMPORTER_ROLES


class Importer(Archivable, BaseTeam):

    role_list = IMPORTER_ROLES

    # Regions
    INDIVIDUAL = "INDIVIDUAL"
    ORGANISATION = "ORGANISATION"
    TYPES = ((INDIVIDUAL, "Individual"), (ORGANISATION, "Organisation"))

    # Region Origins
    UK = None
    EUROPE = "E"
    NON_EUROPEAN = "O"
    REGIONS = ((UK, "UK"), (EUROPE, "Europe"), (NON_EUROPEAN, "Non-European"))

    is_active = models.BooleanField(blank=False, null=False, default=True)

    type = models.CharField(max_length=20, choices=TYPES, blank=False, null=False)

    # these are only set for organisations
    name = models.CharField(max_length=4000, blank=True, null=True)
    registered_number = models.CharField(max_length=15, blank=True, null=True)
    eori_number = models.CharField(max_length=20, blank=True, null=True)
    region_origin = models.CharField(max_length=1, choices=REGIONS, blank=True, null=True)

    # only set for individuals
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, blank=True, null=True, related_name="own_importers"
    )

    # set for both
    comments = models.CharField(max_length=4000, blank=True, null=True)
    offices = models.ManyToManyField(Office)

    # Having a main importer means importer is an agent
    main_importer = models.ForeignKey(
        "self", on_delete=models.SET_NULL, blank=True, null=True, related_name="agents"
    )

    def is_agent(self):
        return self.main_importer is not None

    def is_organisation(self):
        return self.type == self.ORGANISATION

    def __str__(self):
        LABEL = ""
        if self.is_agent():
            LABEL = "Importer Agent"
        else:
            LABEL = "Importer"

        if self.id:
            return LABEL + " - " + self.display_name
        else:
            return LABEL

    @property
    def display_name(self):
        if self.is_organisation():
            return self.name
        else:
            return self.user.full_name if self.user else "None"

    @property
    def status(self):
        return "Current" if self.is_active else "Archived"

    @property
    def entity_type(self):
        return dict(Importer.TYPES)[self.type]

    class Meta:
        ordering = (
            "-is_active",
            "name",
        )
