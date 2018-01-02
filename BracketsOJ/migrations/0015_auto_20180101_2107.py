# Generated by Django 2.0 on 2018-01-01 21:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BracketsOJ', '0014_auto_20171228_0831'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submission',
            name='status',
            field=models.CharField(blank=True, choices=[('AC', 'Accepted'), ('TL', 'Time Limit Exceeded'), ('ML', 'Memory Limit Exceeded'), ('WA', 'Wrong Answer'), ('RTE', 'Run Time Error'), ('QU', 'In queue'), ('CE', 'Syntax error'), ('FJ', 'Failed to judge')], max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='userinfo',
            name='rate',
            field=models.IntegerField(default=0),
        ),
    ]