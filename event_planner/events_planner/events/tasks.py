import os
import json
import logging
from celery import shared_task
from django.conf import settings
from django.utils import timezone
from events.models import Event
from django.db.models.query import QuerySet

logger = logging.getLogger(__name__)


def prepare_event_context(event_data):
    def fill_context(event_obj: Event):
        context = {
            'event_id': event_obj.pk,
            'title': event_obj.title,
            'start_time': str(event_obj.strat_time),
            'end_date': str(event_obj.end_date),
            'created_at': str(event_obj.created_at),
            'user': str(event_obj.user),
            'is_completed': event_obj.is_completed
        }
        return context

    event_context = None
    if isinstance(event_data, QuerySet):
        event_context = [fill_context(event) for event in event_data]
    if isinstance(event_data, Event):
        event_context = fill_context(event_data)
    return event_context or {}


@shared_task
def log_new_event(event_id):
    logger.info(f'[Log New Event] recieved task with event_id: {event_id}')
    try:
        event = Event.objects.get(id=event_id)
        logger.info(f'[Log New Event] Event found: {event.title} by user {event.user}')
        context = prepare_event_context(event)
        logger.info(f'[Log New Event] Context for task recieved: {str(context)}', exc_info=True)
        output_path = os.path.join(settings.MEDIA_ROOT, 'statistics', f'event_{event_id}.json')
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as event_log_file:
            json.dump(context, event_log_file, indent=4, ensure_ascii=False)
        logger.info(f'Log New Event] Successfully saved {event_id} details to {output_path}')
    except Event.DoesNotExist:
        logger.warning(f'[Log New Event] Event {event_id} does not exists')
        pass
    except Exception as e:
        logger.error(f'[Log New Event] Error: {e}', exc_info=True)
        raise

@shared_task
def events_report():
    events = Event.objects.all()
    completed = events.filter(is_completed=True)
    not_completed = events.filter(is_completed=False)

    report_context = {
        'totla_events': events.count(),
        'completed': {
            'total': completed.count(),
            'events': prepare_event_context(completed)
        },
        'not_completed': {
            'total': not_completed.count(),
            'events': prepare_event_context(not_completed)
        }
    }
    output_path = os.path.join(settings.MEDIA_ROOT, 'statistics', f'event_{timezone.now().isoformat()}.json')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open('output_path', 'w', encoding='utf-8') as event_log_file:
        json.dump(events, event_log_file, indent=4, ensure_ascii=False)
