# Generated by Django 3.1.4 on 2021-01-04 08:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='courses',
            name='images',
            field=models.ImageField(null=True, upload_to='courses/'),
        ),
    ]