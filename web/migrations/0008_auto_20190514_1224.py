# Generated by Django 2.1.8 on 2019-05-14 12:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0007_auto_20190514_1051'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id',
                 models.AutoField(
                     auto_created=True,
                     primary_key=True,
                     serialize=False,
                     verbose_name='ID')),
                ('postcode_zip_full',
                 models.CharField(blank=True, max_length=30, null=True)),
                ('postcode_zip_compressed',
                 models.CharField(blank=True, max_length=30, null=True)),
                ('address', models.CharField(max_length=4000)),
                ('status',
                 models.CharField(
                     choices=[('DRAFT', 'Draft'), ('OVERSEAS', 'Overseas'),
                              ('VALID', 'Valid')],
                     default='DRAFT',
                     max_length=12)),
                ('created_date', models.DateField(auto_now_add=True)),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='share_contact_details',
            field=models.BooleanField(null=True),
        ),
        migrations.AlterField(
            model_name='outboundemail',
            name='last_requested_date',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='work_address',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='web.Address'),
        ),
    ]
