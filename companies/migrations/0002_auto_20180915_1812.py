# Generated by Django 2.0 on 2018-09-15 18:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='company',
            options={'verbose_name_plural': 'companies'},
        ),
        migrations.AlterField(
            model_name='company',
            name='name',
            field=models.CharField(blank=True, db_index=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='company',
            name='symbol',
            field=models.CharField(blank=True, db_index=True, max_length=16, null=True),
        ),
        migrations.AlterField(
            model_name='report',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reports', to='companies.Company'),
        ),
    ]
