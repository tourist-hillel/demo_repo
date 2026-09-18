from typing import Any

from django.core.management.base import BaseCommand, CommandError, CommandParser
from events.models import Event
from django.contrib.auth import get_user_model
from faker import Faker

User = get_user_model()
LIST = 'list'
CREATE = 'create'
DELETE = 'delete'
COMPLETE = 'complete'

ALLOWED_COMMANDS = [
    LIST,
    CREATE,
    DELETE,
    COMPLETE
]

class Command(BaseCommand):
    help = f'Event manager with subcommands: {", ".join(ALLOWED_COMMANDS)}'

    def add_arguments(self, parser: CommandParser) -> None:
        subparser = parser.add_subparsers(dest='subcommand', required=True)

        list_parser = subparser.add_parser(
            LIST,
            help='List all events'
        )
        list_parser.add_argument(
            '--not-completed',
            action='store_true'
        )
        list_parser.add_argument(
            '--completed',
            action='store_true'
        )

        create_parser = subparser.add_parser(
            CREATE,
            help='Create a new Event obj'
        )
        create_parser.add_argument(
            'user_id',
            type=int,
            help='User ID'
        )
        create_parser.add_argument(
            '--count',
            type=int,
            help='Count of Event obj to create'
        )

        delete_parser = subparser.add_parser(
            DELETE,
            help='Delete event'
        )
        delete_parser.add_argument(
            'event_ids',
            type=int,
            nargs='+',
            help='ID\'s of Event obj to delete'
        )
        delete_parser.add_argument(
            '--id-from',
            type=int,
            help='Start of id\'s range'
        )
        delete_parser.add_argument(
            '--id-to',
            type=int,
            help='End of id\'s range'
        )

        complete_parser = subparser.add_parser(
            COMPLETE,
            help='Complete event'
        )
        complete_parser.add_argument(
            'event_ids',
            type=int,
            nargs='+',
            help='ID\'s of Event obj to complete'
        )

    def handle(self, *args: Any, **options: Any) -> str | None:
        subcommand = options.get('subcommand')

        if subcommand not in ALLOWED_COMMANDS:
            raise CommandError('Invalid subcommand')

        if subcommand == LIST:
            self._handle_list(options)
        elif subcommand == CREATE:
            self._handle_create(options)
        elif subcommand == DELETE:
            self._handle_delete(options)
        elif subcommand == COMPLETE:
            self._handle_completed(options)

    def _handle_list(self, options):
        events = Event.objects.all()

        not_completed_flag = options.get('not_completed')
        completed_flag = options.get('completed')
        if all([not_completed_flag, completed_flag]):
            raise CommandError('Cannot use both --not-completed and --completed at the same time')

        if not_completed_flag:
            events = events.filter(is_completed=False)
        if completed_flag:
            events = events.filter(is_completed=True)

        if not events:
            self.stdout.write(self.style.WARNING('No events found'))
            return

        self.stdout.write(self.style.SUCCESS('List of events: '))
        for event in events:
            self.stdout.write(self.style.SUCCESS(
                f'- {event.title} | Deadline: {event.end_date.strftime('%Y-%m-%d %H:%M')} | Assigned user: {event.user}'
            ))

    def _handle_create(self, options):
        try:
            user = User.objects.get(id=options['user_id'])
        except (User.DoesNotExist, ValueError) as e:
            raise CommandError(f'The following error caused: {e}')

        count = options.get('count') or 1
        fake = Faker()

        for _ in range(count):
            Event.objects.create(
                title = fake.sentence(nb_words=5)[:-1],
                description = fake.paragraph(),
                strat_time = fake.date_this_century(),
                end_date=fake.date_this_century(),
                user = user,
                is_completed = fake.boolean(chance_of_getting_true=25)
            )

        self.stdout.write(self.style.SUCCESS(
            f'Created {count} events for user {user}'
        ))

    def _handle_delete(self, options):
        event_ids = options.get('event_ids')
        id_from = options.get('id_from') or 0
        id_to = options.get('id_to') or 0
        if id_to == 0:
            max_id = Event.objects.last()
            id_to = max_id.id if max_id else 1

        if id_from and id_to and id_to == id_from:
            raise CommandError('For delete single Event use positional --event_ids enstead')

        if id_to < id_from:
            raise CommandError('id_from cannot be gerater than id_to')
        
        delete_count = 0

        for event_id in event_ids:
            self._delet_event(event_id)
            delete_count += 1

        for event_id in range(id_from, id_to+1):
            self._delet_event(event_id)
            delete_count += 1

        if delete_count == 0:
            raise CommandError('No events were deleted!')

    def _delet_event(self, event_id):
        try:
            event = Event.objects.get(id=event_id)
            title = event.title
            event.delete()
            self.stdout.write(self.style.SUCCESS(
                f'Deleted Event with ID {event_id}: {title}'
            ))
        except Event.DoesNotExist:
            self.stdout.write(self.style.WARNING(
                f'Event with ID={event_id} not found! Skipped!'
            ))

    def _handle_completed(self, options):
        event_ids = options.get('event_ids')

        for event_id in event_ids:
            try:
                event = Event.objects.get(id=event_id)
                event.is_completed = True
                event.save()
                self.stdout.write(self.style.SUCCESS(
                    f'Completed Event with ID {event_id}: {event.title}'
                ))
            except Event.DoesNotExist:
                self.stdout.write(self.style.WARNING(
                    f'Event with ID={event_id} not found! Skipped!'
                ))
