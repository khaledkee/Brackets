# Generated by Django 2.0 on 2018-01-02 13:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BracketsOJ', '0016_remove_userinfo_rate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='problem',
            name='statement',
            field=models.CharField(max_length=1500),
        ),
    ]
