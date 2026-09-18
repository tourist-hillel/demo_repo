from django.db import models
# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from events.mixins import SoftDeleteWithCascadeMixin

User = get_user_model()

class Event(SoftDeleteWithCascadeMixin):
    title = models.CharField(max_length=120, verbose_name='Event name')
    description = models.TextField(blank=True, verbose_name='Description')
    strat_time = models.DateTimeField(verbose_name='Start date n time')
    end_date = models.DateTimeField(verbose_name='End date n time')
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Responsible person')
    is_completed = models.BooleanField(default=False, verbose_name='Is completed')

    def __str__(self) -> str:
        return f'{self.title}'

    class Meta:
        verbose_name = 'Event'
        verbose_name_plural = 'Events'


class EventActions:
    CREATED = 'created'
    UPDATED = 'updated'
    COMPLETED = 'completed'

class ModelLog(models.Model):
    action = models.CharField(max_length=50, default=EventActions.CREATED, verbose_name='Action')
    model = models.CharField(max_length=100, verbose_name='Django model')
    object_id = models.IntegerField(verbose_name='Object ID')
    log_date = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f'{self.action}: {self.model}-{self.object_id}({self.log_date.strftime('%Y-%m-%d %H:%S')})'
