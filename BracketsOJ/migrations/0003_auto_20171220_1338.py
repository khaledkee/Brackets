# Generated by Django 2.0 on 2017-12-20 13:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('BracketsOJ', '0002_auto_20171220_1145'),
    ]

    operations = [
        migrations.AlterField(
            model_name='problem',
            name='contest',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='BracketsOJ.contest'),
        ),
    ]
