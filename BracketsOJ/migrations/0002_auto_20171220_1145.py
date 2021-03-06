# Generated by Django 2.0 on 2017-12-20 11:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('BracketsOJ', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='contest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('start_date', models.DateField()),
            ],
        ),
        migrations.AddField(
            model_name='problem',
            name='contest',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='BracketsOJ.contest'),
        ),
        migrations.AddField(
            model_name='submission',
            name='contest',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='BracketsOJ.contest'),
        ),
    ]
