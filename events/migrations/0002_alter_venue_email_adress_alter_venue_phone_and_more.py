# Generated by Django 5.0.2 on 2024-02-25 18:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='venue',
            name='email_adress',
            field=models.EmailField(blank=True, max_length=60, verbose_name='Email Adress'),
        ),
        migrations.AlterField(
            model_name='venue',
            name='phone',
            field=models.CharField(blank=True, max_length=20, verbose_name='Contact Phone'),
        ),
        migrations.AlterField(
            model_name='venue',
            name='web',
            field=models.URLField(blank=True, verbose_name='Websie Adress'),
        ),
    ]
