from django.db import models
from django.contrib.auth.models import (AbstractUser, Group)
from viewflow.models import Process
from .managers import AccessRequestQuerySet, ProcessQuerySet
from .mixins import Archivable


class Address(models.Model):
    DRAFT = "DRAFT"
    OVERSEAS = "OVERSEAS"
    VALID = "VALID"

    STATUSES = ((DRAFT, "Draft"), (OVERSEAS, "Overseas"), (VALID, "Valid"))
    """Address for users and organisations"""
    postcode_zip_full = models.CharField(max_length=30, blank=True, null=True)
    postcode_zip_compressed = models.CharField(
        max_length=30, blank=True, null=True)
    address = models.CharField(max_length=4000, blank=False, null=False)
    status = models.CharField(
        max_length=12,
        choices=STATUSES,
        blank=False,
        null=False,
        default=DRAFT)
    created_date = models.DateField(auto_now_add=True, blank=False, null=False)


class User(AbstractUser):
    title = models.CharField(max_length=20, blank=False, null=True)
    preferred_first_name = models.CharField(
        max_length=4000, blank=True, null=True)
    middle_initials = models.CharField(max_length=40, blank=True, null=True)
    organisation = models.CharField(max_length=4000, blank=False, null=True)
    department = models.CharField(max_length=4000, blank=False, null=True)
    job_title = models.CharField(max_length=320, blank=False, null=True)
    location_at_address = models.CharField(
        max_length=4000, blank=True, null=True)
    work_address = models.CharField(max_length=300, blank=False, null=True)
    date_of_birth = models.DateField(blank=False, null=True)
    security_question = models.CharField(
        max_length=4000, blank=False, null=True)
    security_answer = models.CharField(max_length=4000, blank=False, null=True)
    register_complete = models.BooleanField(
        blank=False, null=False, default=False)
    share_contact_details = models.BooleanField(
        blank=False, null=False, default=False)

    # work_address = models.ForeignKey(
    #     Address, on_delete=models.SET_NULL, blank=False, null=True)

    class Display:
        display = [('title', 'first_name', 'last_name'),
                   ('organisation', 'email'), 'work_address']
        labels = ['Name', 'Job Details', 'Oragnisation Address']
        select = True


class Role(Group):
    group = models.OneToOneField(
        Group,
        on_delete=models.CASCADE,
        parent_link=True,
        related_name='roles')
    description = models.CharField(max_length=4000, blank=True, null=True)
    # Display order on the screen
    role_order = models.IntegerField(blank=False, null=False)

    def has_member(self, user):
        return user in self.user_set.all()

    @property
    def short_name(self):
        return self.name.split(':')[1]

    class Meta:
        ordering = ('role_order', )


class BaseTeam(models.Model):
    roles = models.ManyToManyField(Role)
    members = models.ManyToManyField(User)
    addresses = models.ManyToManyField(Address)

    class Meta:
        abstract = True


class Team(BaseTeam):
    name = models.CharField(max_length=1000, blank=False, null=False)
    description = models.CharField(max_length=4000, blank=True, null=True)

    class Meta:
        ordering = ('name', )

    class Display:
        display = ['name']
        labels = ['Name']
        edit = True


class Constabulary(Archivable, BaseTeam):
    EAST_MIDLANDS = 'EM'
    EASTERN = 'ER'
    ISLE_OF_MAN = 'IM'
    LONDON = 'LO'
    NORTH_EAST = 'NE'
    NORTH_WEST = 'NW'
    ROYAL_ULSTER = 'RU'
    SCOTLAND = 'SC'
    SOUTH_EAST = 'SE'
    SOUTH_WEST = 'SW'
    WEST_MIDLANDS = 'WM'

    REGIONS = ((EAST_MIDLANDS, 'East Midlands'), (EASTERN, 'Eastern'),
               (ISLE_OF_MAN, 'Isle of Man'), (
                   LONDON,
                   'London',
               ), (NORTH_EAST, 'North East'), (NORTH_WEST, 'North WEST'),
               (ROYAL_ULSTER, 'Royal Ulster'), (SCOTLAND, 'Scotland'),
               (SOUTH_EAST, 'South East'), (SOUTH_WEST,
                                            'South West'), (WEST_MIDLANDS,
                                                            'West Midlands'))

    name = models.CharField(max_length=50, blank=False, null=False)
    region = models.CharField(
        max_length=3, choices=REGIONS, blank=False, null=False)
    email = models.EmailField(max_length=254, blank=False, null=False)
    is_active = models.BooleanField(blank=False, null=False, default=False)

    @property
    def region_verbose(self):
        return dict(Constabulary.REGIONS)[self.region]

    class Display:
        display = ['name', 'region_verbose', 'email']
        labels = ['Constabulary Name', 'Constabulary Region', 'Email Address']
        edit = True
        archive = True


class PhoneNumber(models.Model):
    WORK = "WORK"
    FAX = "FAX"
    MOBILE = "MOBILE"
    HOME = "HOME"
    MINICOM = "MINICOM"
    TYPES = ((WORK, 'Work'), (FAX, 'Fax'), (MOBILE, 'Mobile'), (HOME, 'Home'),
             (MINICOM, 'Minicom'))
    phone = models.CharField(max_length=60, blank=False, null=False)
    type = models.CharField(
        max_length=30, choices=TYPES, blank=False, null=False, default=WORK)
    comment = models.CharField(max_length=4000, blank=True, null=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='phone_numbers')


class Email(models.Model):
    WORK = "WORK"
    HOME = "HOME"
    TYPES = ((WORK, 'Work'), (HOME, 'Home'))
    email = models.EmailField(max_length=254, blank=False, null=False)
    type = models.CharField(
        max_length=30, choices=TYPES, blank=False, null=False, default=WORK)
    portal_notifications = models.BooleanField(
        blank=False, null=False, default=False)
    comment = models.CharField(max_length=4000, blank=True, null=True)

    class Meta:
        abstract = True


class AlternativeEmail(Email):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='alternative_emails')


class PersonalEmail(Email):
    is_primary = models.BooleanField(blank=False, null=False, default=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='personal_emails')


class AccessRequest(models.Model):

    IMPORTER = "IMPORTER"
    IMPORTER_AGENT = "IMPORTER_AGENT"
    EXPORTER = "EXPORTER"
    EXPORTER_AGENT = "EXPORTER_AGENT"

    REQUEST_TYPES = (
        (IMPORTER, 'Request access to act as an Importer'),
        (IMPORTER_AGENT, 'Request access to act as an Agent for an Importer'),
        (EXPORTER, 'Request access to act as an Exporter'),
        (EXPORTER_AGENT, 'Request access to act as an Agent for an Exporter'),
    )

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='access_requests')
    request_type = models.CharField(
        max_length=30, choices=REQUEST_TYPES, blank=False, null=False)
    organisation_name = models.CharField(
        max_length=100, blank=False, null=False)
    organisation_address = models.CharField(
        max_length=500, blank=False, null=False)
    description = models.CharField(max_length=1000, blank=False, null=False)
    agent_name = models.CharField(max_length=100, blank=False, null=False)
    agent_address = models.CharField(max_length=500, blank=False, null=False)
    objects = AccessRequestQuerySet.as_manager()

    def request_type_verbose(self):
        return dict(AccessRequest.REQUEST_TYPES)[self.request_type]

    def request_type_short(self):
        if self.request_type in [self.IMPORTER, self.IMPORTER_AGENT]:
            return "Import Access Request"
        else:
            return "Exporter Access Request"


class AccessRequestProcess(Process):
    access_request = models.ForeignKey(AccessRequest, on_delete=models.CASCADE)
    objects = ProcessQuerySet.as_manager()


class OutboundEmail(models.Model):
    FAILED = 'FAILED'
    SENT = 'SENT'
    PENDING = 'PENDING'
    NOT_SENT = 'NOT_SENT'

    STATUSES = (
        (FAILED, 'Failed'),
        (SENT, 'Sent'),
        (PENDING, 'Pending'),
        (NOT_SENT, 'Not Sent'),
    )

    status = models.CharField(
        max_length=20,
        choices=STATUSES,
        blank=False,
        null=False,
        default=PENDING)
    last_requested_date = models.DateTimeField(
        auto_now_add=True, blank=False, null=False)
    format = models.CharField(
        max_length=20, blank=False, null=False, default='Email')
    to_name = models.CharField(max_length=170, null=True)
    to_email = models.CharField(max_length=254, null=False)
    subject = models.CharField(max_length=4000, null=True)

    @property
    def attachments_count(self):
        return self.attachments.count()

    class Meta:
        ordering = ('-last_requested_date', )

    class Display:
        display = [
            'id', 'status', 'last_requested_date', 'format', 'to_email',
            'subject', 'attachments_count'
        ]
        labels = [
            'Mail Id', 'Status', 'Last Requested / Sent Date', 'Format',
            'To Email', 'Subject', 'Num. of Attachments'
        ]


class EmailAttachment(models.Model):
    mail = models.ForeignKey(
        OutboundEmail, on_delete=models.CASCADE, related_name='attachments')
    filename = models.CharField(max_length=200, blank=True, null=True)
    mimetype = models.CharField(max_length=200, null=False)
    text_attachment = models.TextField(null=True)


class Template(Archivable, models.Model):

    # Template types
    ENDORSEMENT = 'ENDORSEMENT'
    LETTER_TEMPLATE = 'LETTER_TEMPLATE'
    EMAIL_TEMPLATE = 'EMAIL_TEMPLATE'
    CFS_TRANSLATION = 'CFS_TRANSLATION'
    DECLARATION = 'DECLARATION'

    TYPES = (
        (ENDORSEMENT, 'Endorsement'),
        (LETTER_TEMPLATE, 'Letter template'),
        (EMAIL_TEMPLATE, 'Email template'),
        (CFS_TRANSLATION, 'CFS translation'),
        (DECLARATION, 'Declaration'),
    )

    # Application domain
    CERTIFICATE_APPLICATION = "CA"
    IMPORT_APPLICATION = "IMA"
    ACCESS_REQUEST = "IAR"

    DOMAINS = (
        (CERTIFICATE_APPLICATION, "Certificate Applications"),
        (IMPORT_APPLICATION, "Import Applications"),
        (ACCESS_REQUEST, "Access Requests"),
    )

    start_datetime = models.DateTimeField(blank=False, null=False)
    end_datetime = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(blank=False, null=False, default=False)
    template_name = models.CharField(max_length=100, blank=False, null=False)
    template_code = models.CharField(max_length=50, blank=True, null=True)
    template_type = models.CharField(
        max_length=20, choices=TYPES, blank=False, null=False)
    application_domain = models.CharField(
        max_length=20, choices=DOMAINS, blank=False, null=False)
    template_title = models.CharField(max_length=4000, blank=False, null=True)
    template_content = models.TextField(blank=False, null=True)

    @property
    def template_status(self):
        return 'Active' if self.is_active else 'Archived'

    @property
    def template_type_verbose(self):
        return dict(Template.TYPES)[self.template_type]

    @property
    def application_domain_verbose(self):
        return dict(Template.DOMAINS)[self.application_domain]

    class Meta:
        ordering = ('-is_active', )

    # Default display fields on the listing page of the model
    class Display:
        display = [
            'template_name', 'application_domain_verbose',
            'template_type_verbose', 'template_status'
        ]
        labels = [
            'Template Name', 'Application Domain', 'Template Type',
            'Template Status'
        ]
        #  Display actions
        edit = True
        view = True
        archive = True


class Unit(models.Model):
    unit_type = models.CharField(max_length=20, blank=False, null=False)
    description = models.CharField(max_length=100, blank=False, null=False)
    short_description = models.CharField(
        max_length=30, blank=False, null=False)
    hmrc_code = models.IntegerField(blank=False, null=False)

    def __str__(self):
        return self.description


class Commodity(Archivable, models.Model):
    TEXTILES = 'TEXTILES'
    IRON_STEEL = 'IRON_STEEL'
    FIREARMS_AMMO = 'FIREARMS_AMMO'
    WOOD = 'WOOD'
    VEHICLES = 'VEHICLES'
    WOOD_CHARCOAL = 'WOOD_CHARCOAL'
    PRECIOUS_METAL_STONE = 'PRECIOUS_METAL_STONE'
    OIL_PETROCHEMICALS = 'OIL_PETROCHEMICALS'

    TYPES = ((TEXTILES, 'Textiles'), (IRON_STEEL, 'Iron, Steel and Aluminium'),
             (FIREARMS_AMMO, 'Firearms and Ammunition'), (WOOD, 'Wood'),
             (VEHICLES, 'Vehicles'), (WOOD_CHARCOAL, 'Wood Charcoal'),
             (PRECIOUS_METAL_STONE,
              'Precious Metals and Stones'), (OIL_PETROCHEMICALS,
                                              'Oil and Petrochemicals'))

    is_active = models.BooleanField(blank=False, null=False, default=False)
    start_datetime = models.DateTimeField(
        auto_now_add=True, blank=False, null=False)
    end_datetime = models.DateTimeField(blank=True, null=True)
    commodity_code = models.CharField(max_length=10, blank=False, null=False)
    commodity_type = models.CharField(
        max_length=20, choices=TYPES, blank=False, null=False)
    validity_start_date = models.DateField(blank=False, null=True)
    validity_end_date = models.DateField(blank=True, null=True)
    quantity_threshold = models.IntegerField(blank=True, null=True)
    sigl_product_type = models.CharField(max_length=3, blank=True, null=True)

    @property
    def commodity_type_verbose(self):
        return dict(Commodity.TYPES)[self.commodity_type]

    class Meta:
        ordering = ('commodity_code', )

    class Display:
        display = [
            'commodity_code', 'commodity_type_verbose',
            ('validity_start_date', 'validity_end_date')
        ]
        labels = ['Commodity Code', 'Commodity Type', 'Validity']
        view = False
        edit = True
        archive = True


class CommodityGroup(Archivable, models.Model):
    AUTO = 'AUTO'
    CATEGORY = 'CATEGORY'

    TYPES = ((AUTO, 'Auto'), (CATEGORY, ('Category')))

    is_active = models.BooleanField(blank=False, null=False, default=False)
    start_datetime = models.DateTimeField(blank=False, null=False)
    end_datetime = models.DateTimeField(blank=True, null=True)
    group_type = models.CharField(
        max_length=20, choices=TYPES, blank=False, null=False, default=AUTO)
    group_code = models.CharField(max_length=25, blank=False, null=False)
    group_name = models.CharField(max_length=100, blank=True, null=True)
    group_description = models.CharField(
        max_length=4000, blank=True, null=True)
    commodity_type = models.CharField(
        max_length=20, choices=Commodity.TYPES, blank=True, null=True)
    unit = models.ForeignKey(
        Unit, on_delete=models.SET_NULL, blank=True, null=True)
    commodities = models.ManyToManyField(Commodity, blank=True)

    @property
    def group_type_verbose(self):
        return dict(CommodityGroup.TYPES)[self.group_type]

    @property
    def commodity_type_verbose(self):
        return dict(Commodity.TYPES)[self.commodity_type]

    class Display:
        display = [
            'group_type_verbose', 'commodity_type_verbose', 'group_code',
            'group_description'
        ]
        labels = [
            'Commodity Code', 'Commodity Type', 'Group Code/ Group Name',
            'Descripption/ Commodities'
        ]
        view = False
        edit = True
        archive = True


class Country(models.Model):
    SOVEREIGN_TERRITORY = 'SOVEREIGN_TERRITORY'
    SYSTEM = 'SYSTEM'

    TYPES = ((SOVEREIGN_TERRITORY, 'Sovereign Territory'), (SYSTEM, 'System'))

    name = models.CharField(max_length=4000, blank=False, null=False)
    is_active = models.BooleanField(blank=False, null=False, default=False)
    type = models.CharField(
        max_length=30, choices=TYPES, blank=False, null=False)
    commission_code = models.CharField(max_length=20, blank=False, null=False)
    hmrc_code = models.CharField(max_length=20, blank=False, null=False)

    class Meta:
        ordering = ('name',)


class CountryGroup(models.Model):
    name = models.CharField(max_length=4000, blank=False, null=False)
    comments = models.CharField(max_length=4000, blank=True, null=True)
    countries = models.ManyToManyField(Country, blank=True,
                                       related_name='country_groups')

    class Meta:
        ordering = ('name',)
