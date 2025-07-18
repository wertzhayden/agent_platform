# Generated by Django 5.2.1 on 2025-07-14 22:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0003_rename_player_ourlads_link_player_ourlads_link_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Accolade',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('year', models.IntegerField()),
                ('name_of_award', models.TextField(blank=True, null=True)),
                ('team', models.IntegerField(blank=True, null=True)),
                ('source', models.TextField(blank=True, null=True)),
                ('conference', models.TextField(blank=True, null=True)),
                ('player', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='accolades', to='core.player')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
