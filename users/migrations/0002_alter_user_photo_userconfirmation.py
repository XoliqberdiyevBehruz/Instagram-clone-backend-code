# Generated by Django 5.0.4 on 2024-04-06 17:46

import django.core.validators
import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='users_profile_photo/', validators=[django.core.validators.FileExtensionValidator(['png', 'jpg', 'jpeg'])]),
        ),
        migrations.CreateModel(
            name='UserConfirmation',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('updated_time', models.DateTimeField(auto_now=True)),
                ('code', models.CharField(max_length=4)),
                ('verify_type', models.CharField(choices=[('via_email', 'via_email'), ('via_phone', 'via_phone')], max_length=31)),
                ('expiration_time', models.DateTimeField(null=True)),
                ('is_confired', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='verify_codes')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
