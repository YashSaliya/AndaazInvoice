# Generated by Django 4.2 on 2023-05-01 13:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("invoice", "0004_rename_address_maincompany_address1_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="invoice",
            name="dueDate",
            field=models.DateField(blank=True),
        ),
    ]