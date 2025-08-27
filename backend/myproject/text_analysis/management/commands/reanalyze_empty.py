# app/management/commands/reanalyze_empty.py
from django.core.management.base import BaseCommand

from ....text_analysis.views import run_analysis_in_background

from ....text_analysis.models import SavedText


class Command(BaseCommand):
    help = "Re-run text analysis for entries with empty analysis_result"

    def handle(self, *_args, **_options):
        texts = SavedText.objects.filter(report_data__isnull=True) | SavedText.objects.filter(report_data="")

        self.stdout.write(f"Found {texts.count()} texts with empty analysis_result.")

        for text in texts:
            self.stdout.write(str(text.id))
            try:
                run_analysis_in_background(text.id, text.student.id)
                self.stdout.write(self.style.SUCCESS(f"Updated text {text.pk}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed to analyze text {text.pk}: {e}"))
