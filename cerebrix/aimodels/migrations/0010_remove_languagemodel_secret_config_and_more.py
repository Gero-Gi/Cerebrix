# Generated by Django 5.1.4 on 2024-12-17 16:54

import encrypted_json_fields.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aimodels', '0009_embeddingmodel'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='languagemodel',
            name='secret_config',
        ),
        migrations.AlterField(
            model_name='languagemodel',
            name='config',
            field=encrypted_json_fields.fields.EncryptedJSONField(),
        ),
    ]
