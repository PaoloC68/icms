# Generated by Django 2.2.4 on 2019-08-29 10:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0052_importcasevariation'),
    ]

    operations = [
        migrations.AddField(
            model_name='importapplication',
            name='importer_office',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='office_import_applications', to='web.Office'),
        ),
    ]
