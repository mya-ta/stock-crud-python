# Generated by Django 5.1.3 on 2024-11-29 03:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='sku',
            field=models.CharField(default='none', max_length=255),
        ),
    ]
