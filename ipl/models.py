from django.db import models

# Create your models here.
class Team(models.Model):
    team_name = models.CharField(max_length=100)
    logo = models.ImageField(null=False, upload_to='ipl/images')
    bg_img = models.ImageField(null=True, upload_to='ipl/images')
    captain = models.CharField(max_length=100)
    home_ground = models.CharField(max_length=100)
    coach = models.CharField(max_length=100)

    def __str__(self):
        return self.team_name

class Player(models.Model):

    ROLE_CHOICES = (
        ('Batter', 'Batter'),
        ('Bowler', 'Bowler'),
        ('All Rounder', 'All Rounder'),
        ('Wicket Keeper, Batter', 'Wicket Keeper, Batter'),
    )

    player_name = models.CharField(max_length=100)
    age = models.IntegerField()
    role = models.CharField(max_length=100, choices=ROLE_CHOICES)
    nationality = models.CharField(max_length=100)
    profile = models.ImageField(upload_to='ipl/images')
    is_playing = models.BooleanField(default=False)

    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='players'
    )

    def __str__(self):
        return self.player_name
    
class Match(models.Model):

    STATUS_CHOICES = (
        ('Upcoming', 'Upcoming'),
        ('Live', 'Live'),
        ('Completed', 'Completed'),
    )

    STAGE_CHOICES = (
        ('League', 'League'),
        ('Qualifier 1', 'Qualifier 1'),
        ('Eliminator', 'Eliminator'),
        ('Qualifier 2', 'Qualifier 2'),
        ('Final', 'Final'),
    )

    team1 = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='home_matches'
    )

    team2 = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='away_matches'
    )

    match_date = models.DateTimeField()

    venue = models.CharField(max_length=100)

    winner = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='won_matches'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Upcoming'
    )

    stage = models.CharField(
        max_length=30,
        choices=STAGE_CHOICES,
        default='League'
    )

    def __str__(self):
        return f"{self.team1} vs {self.team2}"

class MatchScore(models.Model):

    match = models.ForeignKey(
        Match,
        on_delete=models.CASCADE,
        related_name='scores'
    )

    batting_team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='batting_scores'
    )

    bowling_team = models.ForeignKey(
        
        Team,
        on_delete=models.CASCADE,
        related_name='bowling_scores'
    )

    innings = models.IntegerField()

    runs = models.IntegerField()

    wickets = models.IntegerField()

    overs = models.FloatField()

    def __str__(self):
        return f"{self.batting_team} - {self.runs}/{self.wickets}"

class PlayerScorecard(models.Model):

    match = models.ForeignKey(
        Match,
        on_delete=models.CASCADE,
        related_name='player_scorecards'
    )

    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name='scorecards'
    )

    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='team_scorecards'
    )

    # Batting Stats
    runs = models.IntegerField(default=0)

    balls = models.IntegerField(default=0)

    fours = models.IntegerField(default=0)

    sixes = models.IntegerField(default=0)

    dismissal_type = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    # Bowling Stats
    overs = models.FloatField(default=0)

    wickets = models.IntegerField(default=0)

    runs_conceded = models.IntegerField(default=0)

    maidens = models.IntegerField(default=0)

    catches = models.IntegerField(default=0)

    run_outs = models.IntegerField(default=0)

    stumpings = models.IntegerField(default=0)

    def strike_rate(self):

        if self.balls > 0:
            return round((self.runs / self.balls) * 100, 2)

        return 0

    def economy(self):

        if self.overs > 0:
            return round(self.runs_conceded / self.overs, 2)

        return 0

    def __str__(self):
        return f"{self.player} - {self.match}"
    

class PointsTable(models.Model):

    team = models.OneToOneField(
        Team,
        on_delete=models.CASCADE,
        related_name='points_table'
    )

    matches_played = models.IntegerField(default=0)

    wins = models.IntegerField(default=0)

    losses = models.IntegerField(default=0)

    no_results = models.IntegerField(default=0)

    points = models.IntegerField(default=0)

    runs_scored = models.IntegerField(default=0)

    overs_faced = models.FloatField(default=0)

    runs_conceded = models.IntegerField(default=0)

    overs_bowled = models.FloatField(default=0)

    net_run_rate = models.FloatField(default=0)

    def calculate_nrr(self):

        if self.overs_faced > 0 and self.overs_bowled > 0:

            run_rate_for = self.runs_scored / self.overs_faced
            run_rate_against = self.runs_conceded / self.overs_bowled

            self.net_run_rate = round(run_rate_for - run_rate_against, 3)

        else:
            self.net_run_rate = 0

    def __str__(self):
        return self.team.team_name

class Tournament(models.Model):

    season = models.CharField(max_length=100)

    start_date = models.DateField()

    end_date = models.DateField()

    winner = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tournament_wins'
    )

    runner_up = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='runner_up_finishes'
    )

    def __str__(self):
        return self.season
    
class PlayingXI(models.Model):

    match = models.ForeignKey(
        Match,
        on_delete=models.CASCADE,
        related_name='playing_xi'
    )

    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE
    )

    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE
    )

    is_captain = models.BooleanField(default=False)

    is_wicket_keeper = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.player} - {self.match}"
    
class Award(models.Model):

    AWARD_CHOICES = (
        ('Orange Cap', 'Orange Cap'),
        ('Purple Cap', 'Purple Cap'),
        ('MVP', 'MVP'),
        ('Emerging Player', 'Emerging Player'),
    )

    tournament = models.ForeignKey(
        Tournament,
        on_delete=models.CASCADE
    )

    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE
    )

    award_name = models.CharField(
        max_length=100,
        choices=AWARD_CHOICES
    )

    def __str__(self):
        return f"{self.award_name} - {self.player}"