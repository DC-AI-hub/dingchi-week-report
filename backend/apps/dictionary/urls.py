from django.urls import path

from . import views

app_name = "dictionary"

urlpatterns = [
    path("<str:dict_type>/", views.dictionary_items_view, name="items"),
]
