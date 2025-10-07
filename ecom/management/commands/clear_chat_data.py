from django.core.management.base import BaseCommand
from ecom.models import ChatbotKnowledge

class Command(BaseCommand):
    help = 'Clear chatbot knowledge data from the database (chat sessions no longer supported)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm deletion of chatbot knowledge data',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    'This will delete ALL chatbot knowledge entries from the database.\n'
                    'Note: Chat sessions and messages are no longer supported.\n'
                    'Use --confirm flag to proceed with deletion.'
                )
            )
            return

        # Count records before deletion
        knowledge_count = ChatbotKnowledge.objects.count()

        self.stdout.write(
            f'Found {knowledge_count} chatbot knowledge entries.'
        )

        # Delete chatbot knowledge
        ChatbotKnowledge.objects.all().delete()
        self.stdout.write(
            self.style.SUCCESS(f'Deleted {knowledge_count} chatbot knowledge entries')
        )

        self.stdout.write(
            self.style.SUCCESS('Successfully cleared chatbot knowledge data from the database!')
        )