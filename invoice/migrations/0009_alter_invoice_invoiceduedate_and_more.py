# Generated by Django 4.2 on 2023-05-20 19:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("invoice", "0008_invoice_invoiceduedate_invoice_invoicepaiddate_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="invoice",
            name="invoiceDueDate",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="invoice",
            name="invoicePaidDate",
            field=models.DateField(blank=True, null=True),
        ),
    ]
