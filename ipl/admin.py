from django.contrib import admin
from .models import Team, Player, Match, MatchScore, PlayerScorecard, PointsTable, Tournament, PlayingXI, Award

# Register your models here.
admin.site.register(Team)
admin.site.register(Player)
admin.site.register(Match)
admin.site.register(MatchScore)
admin.site.register(PlayerScorecard)
admin.site.register(PointsTable)
admin.site.register(Tournament)
admin.site.register(PlayingXI)
admin.site.register(Award)