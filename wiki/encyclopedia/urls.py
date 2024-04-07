from django.urls import path

from . import views

urlpatterns = [
    path('search', views.searchword, name='search'),
    path("", views.index, name="index"),
    path("newpage", views.newPage, name="newPage"),   
    path("random", views.random_page, name="random"),
    path("delete/", views.delete_wiki, name="wikidel"),
    path("<str:name>", views.wikirender, name="wikirender"), 
    path("<str:name>/edit", views.Editpage, name="editpage")
]
    
