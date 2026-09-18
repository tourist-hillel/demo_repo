from django.urls import path
from user_account.views import ManageUserPermissionsView

urlpatterns = [
    path('manage/<int:user_id>/', ManageUserPermissionsView.as_view(), name='manage_permissions'),
]