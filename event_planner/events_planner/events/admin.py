from typing import Any

from django.contrib import admin
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html
from events.models import Event, ModelLog

admin.site.register(ModelLog)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = [
        'title_link',
        'user',
        'duration',
        'is_completed',
        'created_at'
    ]
    list_display_links = ['title_link']
    list_filter = [
        'is_completed',
        'user'
    ]


    fieldsets = [
        ('General Info', {
            'fields': ['title', 'description']
        }),
        ('Time', {
            'fields': ['strat_time', 'end_date'],
            'classes': ('wide', )
        }),
        ('Status', {
            'fields': ['is_completed']
        }),
        ('Metadata', {
            'fields': ['user', 'created_at', 'is_deleted', 'deleted_at', 'deleted_by'],
            'classes': ('collapse',)
        }),
    ]

    readonly_fields = ['created_at', 'is_deleted', 'deleted_at', 'deleted_by']
    search_fields = ['title', 'description', 'user__username', 'user__email']
    list_editable = ['is_completed']
    actions = ['mark_completed', 'mark_not_complited', 'duplicate_events']


    def title_link(self, obj):
        try:
            color = "green" if obj.is_completed else "orange"
            obj_link = reverse(f'admin:{obj._meta.app_label}_{obj._meta.model_name}_change', args=[obj.pk])
            return format_html(
                '<a href={}><b style="color:{}">{}</b></a>',
                obj_link,
                color,
                obj.title
            )
        except Exception as e:
            return format_html('<span style="color:red">Error</span>')
        # return obj.title

    title_link.short_description = 'Event title'


    def duration(self, obj):
        if obj.strat_time and obj.end_date:
            delta = obj.end_date - obj.strat_time
            hours = delta.days * 24 + delta.seconds // 3600
            minutes = (delta.seconds % 3600) // 60
            return f'{hours}h {minutes}m'
        return '-'
    duration.short_description = 'Duration'

    @admin.action(description='Mark as a completed')
    def mark_completed(self, request, queryset):
        queryset.update(is_completed=True)

    @admin.action(description='Mark as not completed')
    def mark_not_complited(self, request, queryset):
        queryset.update(is_completed=False)

    @admin.action(description='Deplicate events')
    def duplicate_events(self, request, queryset):
        for event in queryset:
            event.pk = None
            event.created_at = timezone.now()
            event.save()
