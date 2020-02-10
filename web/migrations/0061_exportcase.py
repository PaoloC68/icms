# Generated by Django 2.2.4 on 2019-09-02 14:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0060_auto_20190902_1308'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExportCase',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('IN_PROGRESS', 'In Progress'), ('SUBMITTED', 'Submitted'), ('PROCESSING', 'Processing'), ('COMPLETED', 'Completed'), ('WITHDRAWN', 'Withdrawn'), ('STOPPED', 'Stopped'), ('REVOKED', 'Revoked'), ('VARIATION', 'Case Variation'), ('DELETED', 'Deleted')], max_length=30)),
                ('reference', models.CharField(blank=True, max_length=50, null=True)),
                ('variation_no', models.IntegerField(default=0)),
                ('decision', models.CharField(blank=True, choices=[('REFUSE', 'Refuse'), ('APPROVE', 'Approve')], max_length=10, null=True)),
                ('refuse_reason', models.CharField(blank=True, max_length=4000, null=True)),
                ('last_update_datetime', models.DateTimeField(auto_now=True)),
                ('application', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='case', to='web.ExportApplication')),
                ('last_updated_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='updated_export_cases', to='web.User')),
            ],
        ),
    ]
