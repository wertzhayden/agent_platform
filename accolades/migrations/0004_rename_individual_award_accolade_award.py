# Generated by Django 5.2.1 on 2025-07-16 23:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accolades', '0003_accolade_individual_award_alter_accolade_team'),
    ]

    operations = [
        migrations.RenameField(
            model_name='accolade',
            old_name='individual_award',
            new_name='award',
        ),
    ]
