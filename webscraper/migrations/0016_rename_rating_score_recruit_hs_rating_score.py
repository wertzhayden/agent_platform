# Generated by Django 5.2.1 on 2025-07-12 13:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('webscraper', '0015_recruit_school_link_recruit_transfer_rating_score_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recruit',
            old_name='rating_score',
            new_name='hs_rating_score',
        ),
    ]
