# Generated by Django 2.2.4 on 2019-09-10 20:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0064_auto_20190910_1938'),
    ]

    operations = [
        migrations.AlterField(
            model_name='section5authority',
            name='address',
            field=models.CharField(max_length=300, null=True),
        ),
        migrations.AlterField(
            model_name='section5authority',
            name='address_entry_type',
            field=models.CharField(default='MANUAL', max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='section5authority',
            name='end_date',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='section5authority',
            name='start_date',
            field=models.DateField(null=True),
        ),
    ]
