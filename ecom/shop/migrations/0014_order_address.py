# Generated by Django 4.0.5 on 2022-06-12 19:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0013_rename_street_address_address_city'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='address',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='buy_address', to='shop.address'),
            preserve_default=False,
        ),
    ]