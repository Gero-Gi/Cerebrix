# Generated by Django 5.1.3 on 2024-12-05 06:49

import encrypted_json_fields.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aimodels', '0004_chatmodel_context_window_alter_chatmodel_created_by_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chatmodel',
            name='secret_config',
            field=encrypted_json_fields.fields.EncryptedJSONField(),
        ),
    ]
