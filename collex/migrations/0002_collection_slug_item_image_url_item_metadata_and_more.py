# Generated by Django 4.0.6 on 2022-07-22 19:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collex', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='collection',
            name='slug',
            field=models.SlugField(blank=True, max_length=255, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='item',
            name='image_url',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='item',
            name='metadata',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='item',
            name='tokenUri',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='collection',
            name='abi',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='images/'),
        ),
    ]
