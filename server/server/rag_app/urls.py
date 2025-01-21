from django.urls import path, include
from . import views

urlpatterns = [
    path('upload/', views.upload_documents, name="manageDocuments"),
    path('chat/', views.chatDocuments, name="chatDocument")
]

