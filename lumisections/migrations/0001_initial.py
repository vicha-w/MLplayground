# Generated by Django 3.2.8 on 2021-11-23 11:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('runs', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Lumisection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ls_number', models.IntegerField()),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('run', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='runs.run')),
            ],
        ),
        migrations.AddConstraint(
            model_name='lumisection',
            constraint=models.UniqueConstraint(fields=('run', 'ls_number'), name='unique run/ls combination'),
        ),
    ]