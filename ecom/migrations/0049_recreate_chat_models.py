# Generated manually to recreate chat models

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ecom', '0048_remove_chat_models'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_id', models.CharField(max_length=100, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('handover_status', models.CharField(choices=[('bot', 'Bot Handling'), ('requested', 'Admin Help Requested'), ('admin', 'Admin Handling'), ('resolved', 'Resolved')], default='bot', max_length=20)),
                ('handover_requested_at', models.DateTimeField(blank=True, null=True)),
                ('admin_joined_at', models.DateTimeField(blank=True, null=True)),
                ('handover_reason', models.TextField(blank=True, null=True)),
                ('admin_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='handled_chats', to=settings.AUTH_USER_MODEL)),
                ('customer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='ecom.customer')),
            ],
        ),
        migrations.CreateModel(
            name='ChatMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message_type', models.CharField(choices=[('user', 'User Message'), ('bot', 'Bot Response'), ('admin', 'Admin Response'), ('system', 'System Message')], max_length=10)),
                ('content', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('is_helpful', models.BooleanField(blank=True, null=True)),
                ('admin_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='admin_messages', to=settings.AUTH_USER_MODEL)),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='ecom.chatsession')),
            ],
            options={
                'ordering': ['timestamp'],
            },
        ),
    ]