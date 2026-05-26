from django import forms
from .models import Player


class PlayerForm(forms.ModelForm):

    class Meta:
        model = Player
        fields = [
            "player_name",
            "age",
            "role",
            "nationality",
            "profile",
            "team"
        ]