# Generated by Django 2.2.4 on 2019-08-20 14:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0039_auto_20190820_1119'),
    ]

    operations = [
        migrations.CreateModel(
            name='Section5Authority',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('reference', models.CharField(max_length=50, null=True)),
                ('postcode', models.CharField(blank=True, max_length=30, null=True)),
                ('address', models.CharField(max_length=300)),
                ('address_entry_type', models.CharField(default='MANUAL', max_length=10)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('further_details', models.CharField(blank=True, max_length=4000, null=True)),
                ('importer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='section5_authorities', to='web.Importer')),
                ('issuing_constabulary', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='web.Constabulary')),
                ('linked_offices', models.ManyToManyField(to='web.Office')),
            ],
        ),
        migrations.CreateModel(
            name='FirearmsAuthority',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('reference', models.CharField(max_length=50, null=True)),
                ('certificate_type', models.CharField(choices=[('DEACTIVATED', 'Deactivation Certificate'), ('FIREARMS', 'Firearms Certificate'), ('RFD', 'Registered Firearms Dealer Certificate'), ('SHOTGUN', 'Shotgun Certificate')], max_length=20)),
                ('postcode', models.CharField(blank=True, max_length=30, null=True)),
                ('address', models.CharField(max_length=300)),
                ('address_entry_type', models.CharField(default='MANUAL', max_length=10)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('further_details', models.CharField(blank=True, max_length=4000, null=True)),
                ('importer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='firearms_authorities', to='web.Importer')),
                ('issuing_constabulary', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='web.Constabulary')),
                ('linked_offices', models.ManyToManyField(to='web.Office')),
            ],
        ),
    ]
