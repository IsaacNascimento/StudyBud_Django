# Generated by Django 4.0.6 on 2022-08-02 22:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0004_room_participants'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='message',
            options={'ordering': ['-update', '-created']},
        ),
    ]
