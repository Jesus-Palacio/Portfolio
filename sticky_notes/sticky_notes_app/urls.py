from django.urls import path
from . import views

urlpatterns = [

    path('', views.note_list, name='note_list'),
    path('create/', views.note_create, name='note_create'),
    path('update/<int:pk>/', views.note_update, name='note_update'),
    path('delete/<int:pk>/', views.note_delete, name='note_delete'),
    path('update-position/', views.update_position, name='update_position'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
