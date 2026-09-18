from django.urls import path
from events.views import (
    events_list,
    event_detail,
    EventsList,
    create_event,
    event_edit,
    TestView,
)
from events.s3_views import upload_files_to_s3, s3_files_list

urlpatterns = [
    path('', events_list, name='events_list'),
    path('<int:event_id>/', event_detail, name='event_detail'),
    path('list_cbv', EventsList.as_view(), name='events_list_cbv'),
    path('create/', create_event, name='create_event'),
    path('edit/<int:event_id>/', event_edit, name='event_edit'),
    path('test_view/', TestView.as_view(), name='test_view'),
    path('s3-upload/', upload_files_to_s3, name='s3_upload'),
    path('s3-files-list/', s3_files_list, name='s3_files_list')
]
