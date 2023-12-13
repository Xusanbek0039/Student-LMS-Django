# Generated by Django 4.0.8 on 2023-12-12 23:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='level',
            field=models.CharField(choices=[('Bakalavr', 'Balakavr diplomi'), ('Magistr', 'Magistr diplomi')], max_length=25, null=True),
        ),
        migrations.AlterField(
            model_name='course',
            name='semester',
            field=models.CharField(choices=[('First', 'Birinchi'), ('Second', 'Ikkinchi'), ('Third', 'Uchinchi')], max_length=200),
        ),
    ]