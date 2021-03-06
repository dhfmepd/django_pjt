# Generated by Django 3.1.3 on 2021-03-17 03:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ref_type', models.CharField(max_length=10)),
                ('ref_id', models.IntegerField()),
                ('file_name', models.CharField(max_length=200)),
                ('file_data', models.FileField(upload_to='upload/%Y/%m/%d')),
                ('create_date', models.DateTimeField()),
            ],
        ),
    ]
