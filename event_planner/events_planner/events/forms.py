from django import forms
from django.utils import timezone
from events.models import Event


class EventSearchForm(forms.Form):
    title = forms.CharField(
        label='Search by title',
        max_length=120,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter the event title',
            'class': 'form-control'
        })
    )


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'strat_time', 'end_date']
        widgets = {
            'strat_time': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'min': timezone.now().strftime('%Y-%m-%dT%H:%M')
            }),
            'end_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'min': timezone.now().strftime('%Y-%m-%dT%H:%M')
            }),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.id:
            self.fields['strat_time'].widget.attrs.update({
                'type': 'datetime-local',
                'min': self.instance.strat_time.strftime('%Y-%m-%dT%H:%M'),
                'max': self.instance.strat_time.strftime('%Y-%m-%dT%H:%M'),
            })

            self.fields['end_date'].widget.attrs.update({
                'type': 'datetime-local',
                'min': self.instance.strat_time.strftime('%Y-%m-%dT%H:%M'),
                # 'max': self.instance.strat_time.strftime('%Y-%m-%dT%H:%M')
            })

            if self.instance.strat_time < timezone.now():
                self.fields['strat_time'].widget.attrs['readonly'] = 'readonly'

            if self.instance.end_date < timezone.now():
                self.fields['end_date'].widget.attrs['readonly'] = 'readonly'

    def clean_title(self):
        title = self.cleaned_data.get('title', '')
        if not self.instance.id:
            if len(title) < 3:
                raise forms.ValidationError('The title should be at least 3 char in length')
        if self.user and Event.objects.filter(user=self.user, title=title).exclude(id=self.instance.id).exists():
            raise forms.ValidationError('Event with same title already exists')

        return title

    def clean_strat_time(self):
        start_time = self.cleaned_data.get('strat_time')
        if not self.instance.id or self.instance.id and start_time != self.instance.strat_time:
            if start_time < timezone.now():
                raise forms.ValidationError('Start date cannot be in the past')
        return start_time

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('strat_time')
        end_date = cleaned_data.get('end_date')
        if start_date and end_date:
            if end_date <= start_date:
                raise forms.ValidationError('End date cannot be set beyond the start date')
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.user = self.user
        if commit:
            instance.save()
        return instance
