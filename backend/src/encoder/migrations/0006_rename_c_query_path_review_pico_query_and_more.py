# Generated by Django 4.2.16 on 2024-10-11 08:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('encoder', '0005_alter_corpus_corpus_first_entry_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='review',
            old_name='c_query_path',
            new_name='pico_query',
        ),
        migrations.RemoveField(
            model_name='review',
            name='i_query_path',
        ),
        migrations.RemoveField(
            model_name='review',
            name='o_query_path',
        ),
        migrations.RemoveField(
            model_name='review',
            name='p_query_path',
        ),
    ]
