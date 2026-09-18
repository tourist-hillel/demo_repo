import hashlib
from typing import Any
from django.http import HttpResponse
from django.db import models, transaction
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class FormMixn:
    form = ...

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = self.form(self.request.GET or None)
        return context


class CacheViewMixin:
    cache_timeout = 60 * 5
    cache_timeout_authenticated = 60
    cache_key_prefix = 'view'

    def get_cahce_key(self):
        path = self.request.get_full_path()
        user_part = f'user:{self.request.user.pk}' if self.request.user.is_authenticated else 'anon'
        raw = f'{self.cache_key_prefix}:{self.__class__.__name__}:{user_part}:{path}'
        return hashlib.md5(raw.encode()).hexdigest()

    def get_timeout(self):
        if self.request.user.is_authenticated:
            return self.cache_timeout_authenticated
        return self.cache_timeout

    def dispatch(self, request, *args, **kwargs):
        if self.request.method != 'GET':
            return super().dispatch(request, *args, **kwargs)

        from django.core.cache import cache
        key = self.get_cahce_key()
        cached = cache.get(key)
        if cached is not None:
            return cached

        response = super().dispatch(request, *args, **kwargs)
        if hasattr(response, 'render') and callable(response.render):
            response.render()

        if hasattr(response, 'status_code') and response.status_code == 200:
            cached_response = HttpResponse(
                content=response.content,
                status=response.status_code,
                content_type=response.get('Content-Type', 'text/html')
            )
            cache.set(key, cached_response, self.get_timeout())

        return response

class AliveManager(models.Manager):
    def get_queryset(self) -> models.QuerySet:
        return super().get_queryset().filter(is_deleted=False)

class SoftDeleteWithCascadeMixin(models.Model):
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    class Meta:
        abstract = True

    objects = models.Manager()
    alive = AliveManager()

    def soft_delete(self, user=None, cascade=True) -> tuple[int, dict[str, int]]:
        if self.is_deleted:
            return self.pk, {f'{self._meta.app_label}.{self.__class__.__name__}': self.pk}

        with transaction.atomic():
            self.is_deleted = True
            self.deleted_at = timezone.now()
            self.deleted_by = user
            self.save(update_fields=['is_deleted', 'deleted_at', 'deleted_by'])

            if cascade:
                self._cascade_soft_delete(user)

        return self.pk, {f'{self._meta.app_label}.{self.__class__.__name__}': self.pk}

    def soft_restore(self, cascade=True):
        if not self.is_deleted:
            return

        with transaction.atomic():
            self.is_deleted = False
            self.deleted_at = None
            self.deleted_by = None
            self.save(update_fields=['is_deleted', 'deleted_at', 'deleted_by'])

            if cascade:
                self._cascade_soft_restore()

    def _cascade_soft_delete(self, user):
        for rel in self._meta.related_objects:
            if rel.one_to_many or rel.one_to_one:
                related = getattr(self, rel.get_accessor_name())
                if hasattr(related, 'all'):
                    for obj in related.all():
                        if hasattr(obj, 'soft_delete'):
                            obj.soft_delete(user=user, cascade=True)

    def _cascade_soft_restore(self):
        for rel in self._meta.related_objects:
            if rel.one_to_many or rel.one_to_one:
                related = getattr(self, rel.get_accessor_name())
                if hasattr(related, 'all'):
                    for obj in related.all():
                        if hasattr(obj, 'soft_delete'):
                            obj.soft_restore(cascade=True)

    def delete(self, soft=False, user=None, *args, **kwargs) -> tuple[int, dict[str, int]]:
        if soft:
            return self.soft_delete(user)
        return super().delete(*args, **kwargs)
