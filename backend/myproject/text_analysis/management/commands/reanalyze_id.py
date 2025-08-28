# app/management/commands/reanalyze_by_id.py
from django.core.management.base import BaseCommand, CommandError

from ....text_analysis.views import run_analysis_in_background
from ....text_analysis.models import SavedText


class Command(BaseCommand):
    help = "Re-run text analysis for a specific text ID"

    def add_arguments(self, parser):
        parser.add_argument('text_id', type=int, help='ID of the text to reanalyze')

    def handle(self, *args, **options):
        text_id = options['text_id']
        
        try:
            text = SavedText.objects.get(id=text_id)
        except SavedText.DoesNotExist:
            raise CommandError(f'Text with ID {text_id} does not exist')

        self.stdout.write(f"Reanalyzing text ID: {text_id}")
        
        try:
            run_analysis_in_background(text.id, text.student.id)
            self.stdout.write(self.style.SUCCESS(f"Successfully reanalyzed text {text_id}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to analyze text {text_id}: {e}"))