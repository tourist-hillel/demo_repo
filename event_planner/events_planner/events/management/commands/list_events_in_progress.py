from typing import Any

from django.core.management.base import BaseCommand
from events.models import Event


class Command(BaseCommand):
    help = 'List all events in progress'

    def handle(self, *args: Any, **options: Any) -> str | None:
        in_progress_events = Event.objects.filter(is_completed=False)

        if not in_progress_events:
            self.stdout.write(self.style.WARNING('No events in progress'))
            return

        self.stdout.write(self.style.SUCCESS('In progress events: '))
        for event in in_progress_events:
            self.stdout.write(f'- {event.title} | Deadline: {event.end_date.strftime('%Y-%m-%d %H:%M')} | Assigned user: {event.user}')
