# Generated by Django 4.0.6 on 2022-08-01 23:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collex', '0004_remove_color__lab'),
    ]

    operations = [
        migrations.AddField(
            model_name='itemcolor',
            name='amount',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]