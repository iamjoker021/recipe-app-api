# Generated by Django 4.1.2 on 2022-10-23 08:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_ingredient'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='ingrdients',
            field=models.ManyToManyField(to='core.ingredient'),
        ),
    ]
