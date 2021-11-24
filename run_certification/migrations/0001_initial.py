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
            name='RunCertification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('pca_1', models.FloatField(null=True)),
                ('pca_2', models.FloatField(null=True)),
                ('run', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='runs.run')),
            ],
        ),
    ]