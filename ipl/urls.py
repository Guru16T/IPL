from django.urls import path
from . import views

app_name = "ipl"

urlpatterns = [
    path('', views.home, name="home"),
    path('team/', views.team, name="team"),
    path('add_player/', views.add_player, name="add_player"),
    path('team_players/<int:id>', views.team_players, name="team_players"),
    path('matches/', views.matches, name="matches"),
    path('add_match/', views.add_match, name="add_match"),
    path('match_details/<int:id>/', views.match_details, name="match_details"),
    path('generate_ipl/', views.generate_ipl, name="generate_ipl"),
    path('points_table/', views.points_table, name="points_table"),
    path('qualified_teams/', views.qualify_team, name="qualified_teams"),
    path('winner/', views.winner, name="winner"),
]