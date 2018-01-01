# Generated by Django 2.0 on 2017-12-20 10:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='judge_job',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.BinaryField()),
            ],
        ),
        migrations.CreateModel(
            name='problem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50)),
                ('time_limit', models.IntegerField(default=100)),
                ('memory_limit', models.IntegerField(default=64)),
                ('statement', models.CharField(max_length=500)),
                ('input_section', models.CharField(max_length=200)),
                ('output_section', models.CharField(max_length=200)),
                ('samples', models.IntegerField(default=1)),
                ('notes', models.CharField(blank=True, max_length=200, null=True)),
                ('added', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='submission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.IntegerField(null=True)),
                ('memory', models.IntegerField(null=True)),
                ('submitted', models.DateField()),
                ('judged', models.DateField(null=True)),
                ('status', models.CharField(choices=[('AC', 'Accepted'), ('TLE', 'Time Limit Exceeded'), ('MLE', 'Memory Limit Exceeded'), ('WA', 'Wrong Answer'), ('RTE', 'Run Time Error')], max_length=50, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='user',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=100, unique=True)),
                ('login', models.CharField(max_length=100, unique=True)),
                ('hash_password', models.CharField(max_length=1100)),
            ],
        ),
        migrations.AddField(
            model_name='submission',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='BracketsOJ.user'),
        ),
        migrations.AddField(
            model_name='judge_job',
            name='submission',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='BracketsOJ.submission'),
        ),
    ]