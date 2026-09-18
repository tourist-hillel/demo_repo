from typing import Any
import csv
from django.core.management.base import BaseCommand, CommandError, CommandParser
from events.models import Event
from django.contrib.auth import get_user_model
# from django.utils import timezone
from datetime import datetime
from tqdm import tqdm

User = get_user_model()


class Command(BaseCommand):
    help = 'Import events from CSV file'


    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            'csv_file',
            type=str,
            help='Path to CSV file'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Test run without saving'
        )

    def handle(self, *args: Any, **options: Any) -> str | None:
        csv_file = options['csv_file']
        dry_run = options['dry_run']

        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                rows = list(reader)
        except FileNotFoundError:
            raise CommandError(f'File {csv_file} not found!')

        if not rows:
            self.stdout.write(self.style.WARNING('CSV file is empty!'))
            return

        create_count = 0
        errors = []

        with tqdm(total=len(rows), desc='Importing events...', unit='event') as pbar:
            for row in rows:
                try:
                    user = User.objects.get(id=row['user_id'])
                    start_date = datetime.strptime(row.get('start_date'), '%Y-%m-%d')
                    end_date = datetime.strptime(row.get('end_date'), '%Y-%m-%d')

                    event = Event(
                        title = row['title'],
                        description = row['description'],
                        strat_time = start_date,
                        end_date = end_date,
                        is_completed = row['is_completed'].lower() == 'true',
                        user = user
                    )
                    if not dry_run:
                        event.save()
                    create_count += 1
                except (User.DoesNotExist, ValueError) as e:
                    errors.append(f'| Error in row: {row} \nerror: {e}|')
                pbar.update(1)
        self.stdout.write(self.style.SUCCESS(
            f'| Events {create_count}| dry-run: {dry_run}'
        ))
        if errors:
            self.stdout.write(self.style.ERROR('Errors: '))
            for error in errors:
                self.stdout.write(self.style.ERROR(error))