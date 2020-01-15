# Generated by Django 3.0 on 2020-01-14 18:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import multiselectfield.db.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='FootballPlayer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sport', models.CharField(default='fotboll', max_length=50)),
                ('username', models.CharField(max_length=50, unique=True)),
                ('positions', multiselectfield.db.fields.MultiSelectField(choices=[('målvakt', 'Målvakt'), ('försvarare', 'Försvarare'), ('vänsterback', 'Vänsterback'), ('högerback', 'Högerback'), ('mittback', 'Mittback'), ('mittfältare', 'Mittfältare'), ('vänstermittfältare', 'Vänstermittfältare'), ('högermittfältare', 'Högermittfältare'), ('centralmittfältare', 'Centralmittfältare'), ('anfallare', 'Anfallare')], max_length=255)),
                ('foot', models.CharField(choices=[('höger', 'Höger'), ('vänster', 'Vänster'), ('dubbelfotad', 'Dubbelfotad')], max_length=255)),
                ('experience', models.CharField(choices=[('ungdomsfotboll', 'Ungdomsfotboll'), ('korpen', 'Korpen'), ('division 8', 'Division 8'), ('division 7', 'Division 7'), ('division 6', 'Division 6'), ('division 5', 'Division 5'), ('division 4', 'Division 4'), ('division 3', 'Division 3'), ('division 2', 'Division 2'), ('division 1', 'Division 1'), ('superettan', 'Superettan'), ('allsvenskan', 'Allsvenskan')], max_length=255)),
                ('special_ability', models.CharField(choices=[('snabb', 'Snabb'), ('uthållig', 'Uthållig'), ('allround', 'Allround'), ('positionering', 'Positionering'), ('huvudspel', 'Huvudspel'), ('ledargestalt', 'Ledargestalt'), ('snabba reflexer', 'Snabba Reflexer'), ('skott', 'Skott'), ('spelförståelse', 'Spelförståelse'), ('inlägg', 'Inlägg'), ('långbollar', 'Långbollar'), ('frisparkar', 'Frisparkar'), ('dribbla', 'Dribbla'), ('tackla', 'Tackla')], max_length=255)),
                ('is_available', models.BooleanField(default=False)),
                ('image', models.ImageField(blank=True, default='images/players/football/default_football_player.jpg', null=True, upload_to='images/players/football/')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='football_player', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='FootballHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_year', models.PositiveSmallIntegerField()),
                ('end_year', models.PositiveSmallIntegerField()),
                ('team_name', models.CharField(max_length=25)),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='history_entries', to='players.FootballPlayer')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
