# Generated by Django 5.1.4 on 2024-12-20 12:03

import encrypted_json_fields.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aimodels', '0011_embeddingmodel_size'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='embeddingmodel',
            name='secret_config',
        ),
        migrations.AlterField(
            model_name='embeddingmodel',
            name='config',
            field=encrypted_json_fields.fields.EncryptedJSONField(blank=True, null=True),
        ),
    ]
