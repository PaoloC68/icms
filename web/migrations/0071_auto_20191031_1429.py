# Generated by Django 2.2.4 on 2019-10-31 14:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0070_auto_20191028_1102'),
    ]

    operations = [
        migrations.RenameField(
            model_name='importapplicationtype',
            old_name='licent_type_code',
            new_name='licence_type_code',
        ),
    ]
