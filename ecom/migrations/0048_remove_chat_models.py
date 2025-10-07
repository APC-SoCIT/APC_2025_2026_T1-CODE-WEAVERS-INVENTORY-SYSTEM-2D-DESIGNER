# Generated manually to remove chat models

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ecom', '0047_chatmessage_admin_user_chatsession_admin_joined_at_and_more'),
    ]

    operations = [
        # Drop ChatMessage table first (due to foreign key dependency)
        migrations.RunSQL(
            "DROP TABLE IF EXISTS ecom_chatmessage;",
            reverse_sql="-- Cannot reverse this migration"
        ),
        
        # Drop ChatSession table
        migrations.RunSQL(
            "DROP TABLE IF EXISTS ecom_chatsession;",
            reverse_sql="-- Cannot reverse this migration"
        ),
    ]