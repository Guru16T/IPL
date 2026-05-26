from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Team, Player, Match, PointsTable, MatchScore, PlayerScorecard, PlayingXI
from .forms import PlayerForm
from django.http import JsonResponse
import random
from datetime import datetime, timedelta
from django.db.models import Q, Sum
from django.utils import timezone

# Create your views here.
def home(request):
    team = Team.objects.all()
    return render(request, 'home.html', {'teams': team})

def team(request):
    team = Team.objects.all()
    return render(request, 'teams.html', {'teams': team})

def add_player(request):
    team = Team.objects.all()
    form = PlayerForm()

    if request.method == 'POST':
        form = PlayerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()

    return render(request, 'add_player.html', {'teams': team})

def team_players(request, id):
    player = Player.objects.filter(team=id)
    return render(request, 'players.html', {'player': player})

def matches(request):
    matches = Match.objects.all()
    match_score = MatchScore.objects.all()
    return render(request, 'matches.html', {'matches': matches})

def add_match(request):
    team = Team.objects.all()
    return render(request, 'add_match.html', {'team': team})

def match_details(request, id):
    match = Match.objects.get(id=id)

    score = MatchScore.objects.filter(match=match)

    scorecards = PlayerScorecard.objects.filter(match=match)

    team1_Xi = PlayingXI.objects.filter(match=match, team=match.team1)

    team2_Xi = PlayingXI.objects.filter(match=match, team=match.team2)

    context = {
        'match': match,
        'score': score,
        'scorecards': scorecards,
        'team1_Xi': team1_Xi,
        'team2_Xi': team2_Xi
    }

    return render(request, 'match_details.html', context)

# Generated Data

def overs_to_balls(overs_decimal):

    full_overs = int(overs_decimal)

    extra_balls = round(
        (overs_decimal - full_overs) * 10
    )

    return (full_overs * 6) + extra_balls


def balls_to_decimal_overs(balls):

    return (balls // 6) + (balls % 6) / 10


def generate_ipl(request):

    # Clear all data from Model

    PlayingXI.objects.all().delete()
    PlayerScorecard.objects.all().delete()
    MatchScore.objects.all().delete()
    Match.objects.all().delete()
    PointsTable.objects.all().delete()

    teams = list(Team.objects.all())

    match_count = {
        team.id: 0 for team in teams
    }

    schedule = []

    while True:

        available = [
            t for t in teams
            if match_count[t.id] < 2
        ]

        if len(available) < 2:
            break

        t1, t2 = random.sample(available, 2)

        already_exists = any(
            (a == t1 and b == t2) or
            (a == t2 and b == t1)
            for a, b in schedule
        )

        if already_exists:
            continue

        schedule.append((t1, t2))

        match_count[t1.id] += 1
        match_count[t2.id] += 1

    current_date = datetime(2026, 3, 28)

    # Create Match
    for team1, team2 in schedule:

        weekday = current_date.weekday()

        if weekday in [5, 6]:
            hour = random.choice([15, 19])
        else:
            hour = 19

        match = Match.objects.create(
            team1=team1,
            team2=team2,
            match_date=current_date.replace(
                hour=hour,
                minute=30
            ),
            venue=random.choice([
                team1.home_ground,
                team2.home_ground
            ]),
            status="Completed"
        )

        # Playing XI
        def get_xi(team):

            players = list(
                Player.objects.filter(team=team)
            )

            while True:

                xi = random.sample(players, 11)

                foreign = len([
                    p for p in xi
                    if p.nationality != "Indian"
                ])

                if foreign <= 4:
                    return xi

        xi1 = get_xi(team1)
        xi2 = get_xi(team2)

        # Save Playing XI
        for p in xi1:

            PlayingXI.objects.create(
                match=match,
                team=team1,
                player=p,
                is_captain=(
                    p.player_name == team1.captain
                ),
                is_wicket_keeper=(
                    "Wicket Keeper" in p.role
                )
            )

        for p in xi2:

            PlayingXI.objects.create(
                match=match,
                team=team2,
                player=p,
                is_captain=(
                    p.player_name == team2.captain
                ),
                is_wicket_keeper=(
                    "Wicket Keeper" in p.role
                )
            )

        # TEAM TOTALS

        t1_total_runs = random.randint(70, 250)
        t2_total_runs = random.randint(70, 250)

        t1_wickets = random.randint(2, 10)
        t2_wickets = random.randint(2, 10)

        # TEAM 1 BATTING

        remaining_runs = t1_total_runs

        for index, p in enumerate(xi1):

            if index >= (11 - t1_wickets):

                runs = 0
                balls = random.randint(1, 8)

            else:

                max_runs = min(
                    80,
                    remaining_runs
                )

                runs = random.randint(
                    0,
                    max_runs
                )

                balls = random.randint(
                    5,
                    60
                )

            if index == 10:
                runs = remaining_runs

            remaining_runs -= runs

            if remaining_runs < 0:
                remaining_runs = 0

            PlayerScorecard.objects.create(
                match=match,
                player=p,
                team=team1,
                runs=runs,
                balls=balls,
                fours=random.randint(0, 10),
                sixes=random.randint(0, 6),
                overs=0,
                wickets=0,
                runs_conceded=0
            )

        # TEAM 2 BATTING

        remaining_runs = t2_total_runs

        for index, p in enumerate(xi2):

            if index >= (11 - t2_wickets):

                runs = 0
                balls = random.randint(1, 8)

            else:

                max_runs = min(
                    80,
                    remaining_runs
                )

                runs = random.randint(
                    0,
                    max_runs
                )

                balls = random.randint(
                    5,
                    60
                )

            if index == 10:
                runs = remaining_runs

            remaining_runs -= runs

            if remaining_runs < 0:
                remaining_runs = 0

            PlayerScorecard.objects.create(
                match=match,
                player=p,
                team=team2,
                runs=runs,
                balls=balls,
                fours=random.randint(0, 10),
                sixes=random.randint(0, 6),
                overs=0,
                wickets=0,
                runs_conceded=0
            )

        # TEAM 1 BOWLERS

        wickets_left = t2_wickets

        bowlers1 = [
            p for p in xi1
            if p.role in [
                "Bowler",
                "All Rounder"
            ]
        ]

        for index, p in enumerate(bowlers1):

            scorecard = PlayerScorecard.objects.get(
                match=match,
                player=p
            )

            if index == len(bowlers1) - 1:
                wkts = wickets_left
            else:
                wkts = random.randint(
                    0,
                    min(4, wickets_left)
                )

            wickets_left -= wkts

            scorecard.overs = round(
                random.uniform(1, 4),
                1
            )

            scorecard.wickets = wkts

            scorecard.runs_conceded = random.randint(
                10,
                50
            )

            scorecard.save()

        # TEAM 2 BOWLERS

        wickets_left = t1_wickets

        bowlers2 = [
            p for p in xi2
            if p.role in [
                "Bowler",
                "All Rounder"
            ]
        ]

        for index, p in enumerate(bowlers2):

            scorecard = PlayerScorecard.objects.get(
                match=match,
                player=p
            )

            if index == len(bowlers2) - 1:
                wkts = wickets_left
            else:
                wkts = random.randint(
                    0,
                    min(4, wickets_left)
                )

            wickets_left -= wkts

            scorecard.overs = round(
                random.uniform(1, 4),
                1
            )

            scorecard.wickets = wkts

            scorecard.runs_conceded = random.randint(
                10,
                50
            )

            scorecard.save()

        # MATCH OVERS

        t1_overs = (
            20.0 if t1_wickets < 10
            else round(
                random.uniform(15, 20),
                1
            )
        )

        t2_overs = (
            20.0 if t2_wickets < 10
            else round(
                random.uniform(15, 20),
                1
            )
        )

        # MATCH SCORE

        MatchScore.objects.create(
            match=match,
            batting_team=team1,
            bowling_team=team2,
            innings=1,
            runs=t1_total_runs,
            wickets=t1_wickets,
            overs=t1_overs
        )

        MatchScore.objects.create(
            match=match,
            batting_team=team2,
            bowling_team=team1,
            innings=2,
            runs=t2_total_runs,
            wickets=t2_wickets,
            overs=t2_overs
        )

        
        # WINNER
        
        if t1_total_runs > t2_total_runs:

            match.winner = team1

        elif t2_total_runs > t1_total_runs:

            match.winner = team2

        else:

            match.winner = None

        match.save()

        current_date += timedelta(days=1)

    
    # GENERATE POINTS TABLE
    
    table = []

    for team in teams:

        completed = Match.objects.filter(
            Q(team1=team) |
            Q(team2=team),
            status="Completed"
        )

        matches_played = completed.count()

        wins = completed.filter(
            winner=team
        ).count()

        no_result = completed.filter(
            winner=None
        ).count()

        losses = (
            matches_played -
            wins -
            no_result
        )

        points = (wins * 2) + no_result

        
        # MATCH SCORES
        
        bat_qs = MatchScore.objects.filter(
            batting_team=team
        )

        bowl_qs = MatchScore.objects.filter(
            bowling_team=team
        )

        runs_scored = sum([
            s.runs for s in bat_qs
        ])

        runs_conceded = sum([
            s.runs for s in bowl_qs
        ])
        
        # BALLS
        
        bat_total_balls = sum([
            overs_to_balls(s.overs)
            for s in bat_qs
        ])

        bowl_total_balls = sum([
            overs_to_balls(s.overs)
            for s in bowl_qs
        ])

        bat_true_overs = (
            bat_total_balls / 6
            if bat_total_balls > 0
            else 1
        )

        bowl_true_overs = (
            bowl_total_balls / 6
            if bowl_total_balls > 0
            else 1
        )

        batting_rr = (
            runs_scored / bat_true_overs
        )

        bowling_rr = (
            runs_conceded / bowl_true_overs
        )

        nrr = round(
            batting_rr - bowling_rr,
            3
        )

        table.append({

            "team": team,

            "matches_played": matches_played,

            "wins": wins,

            "losses": losses,

            "no_results": no_result,

            "points": points,

            "runs_scored": runs_scored,

            "overs_faced": round(
                balls_to_decimal_overs(
                    bat_total_balls
                ),
                1
            ),

            "runs_conceded": runs_conceded,

            "overs_bowled": round(
                balls_to_decimal_overs(
                    bowl_total_balls
                ),
                1
            ),

            "net_run_rate": nrr
        })

    
    # SORT TABLE
    
    table = sorted(
        table,
        key=lambda x: (
            x["points"],
            x["net_run_rate"],
            x["wins"]
        ),
        reverse=True
    )

    
    # SAVE TABLE
    
    for row in table:

        PointsTable.objects.create(
            team=row["team"],
            matches_played=row["matches_played"],
            wins=row["wins"],
            losses=row["losses"],
            no_results=row["no_results"],
            points=row["points"],
            runs_scored=row["runs_scored"],
            overs_faced=row["overs_faced"],
            runs_conceded=row["runs_conceded"],
            overs_bowled=row["overs_bowled"],
            net_run_rate=row["net_run_rate"]
        )

    
    # TOP 4 TEAMS
    
    table = PointsTable.objects.order_by(
        "-points",
        "-net_run_rate"
    )[:4]

    
    # CHECK 4 TEAMS AVAILABLE
    
    if len(table) < 4:

        return HttpResponse(
            "Need minimum 4 teams in points table"
        )

    
    # POINTS TABLE ORDER
    
    team1 = table[0].team
    team2 = table[1].team
    team3 = table[2].team
    team4 = table[3].team

    
    # QUALIFIER 1
    # TEAM 1 vs TEAM 2
    
    qualifier1 = Match.objects.create(
        team1=team1,
        team2=team2,
        venue=random.choice([
            team1.home_ground,
            team2.home_ground
        ]),
        match_date=timezone.now(),
        status="Completed",
        stage="Qualifier 1"
    )

    # def get_team_xi(team):
    #     Players = list(
    #         Player.objects.filter(team1=team)
    #     )

    #     while True:
    #         xi = random.sample(Players, 11)

    #         foreign = len([
    #                 p for p in xi
    #                 if p.nationality != "Indian"
    #             ])

    #         if foreign <= 4:
    #             return xi
            
    # xi1 = get_team_xi(team1)
    # xi2 = get_team_xi(team2)

    # for p in xi1:

    #     PlayingXI.objects.create(
    #         match=match,
    #         team=team1,
    #         player=p,
    #         is_captain=(
    #             p.player_name == team1.captain
    #         ),
    #         is_wicket_keeper=(
    #             "Wicket Keeper" in p.role
    #         )
    #     )

    # for p in xi2:

    #     PlayingXI.objects.create(
    #         match=match,
    #         team=team1,
    #         player=p,
    #         is_captain=(
    #             p.player_name == team1.captain
    #         ),
    #         is_wicket_keeper=(
    #             "Wicket Keeper" in p.role
    #         )
    #     )


    q1_team1_score = random.randint(140, 240)
    q1_team2_score = random.randint(140, 240)

    # q1_team1_wicket = random.randint(2, 10)
    # q1_team2_wicket = random.randint(2, 10)

    # remaining_runs = t1_total_runs

    # for index, p in enumerate(xi1):
    #     if index >= (11 - q1_team1_wicket):
    #         runs = 0
    #         balls = random.randint(1, 8)
    #     else:
    #         max_runs(
    #             80,
    #             remaining_runs
    #         )

    #         runs = random.randint(0, max_runs)

    #         balls = random.randint(5, 60)

    #     if index == 10:
    #         runs = remaining_runs

    #     remaining_runs -= runs

    #     if remaining_runs < 0:
    #         remaining_runs = 0

    #     PlayerScorecard.objects.create(
    #             match=match,
    #             player=p,
    #             team=team1,
    #             runs=runs,
    #             balls=balls,
    #             fours=random.randint(0, 10),
    #             sixes=random.randint(0, 6),
    #             overs=0,
    #             wickets=0,
    #             runs_conceded=0
    #         )

    # remaining_runs = q2_team1_score

    # for index, p in enumerate(xi1):
    #     if index >= (11 - q1_team2_wicket):
    #         runs = 0
    #         balls = random.randint(1, 8)
    #     else:
    #         max_runs(
    #             80,
    #             remaining_runs
    #         )

    #         runs = random.randint(0, max_runs)
    #         balls = random.randint(5, 60)

    #     if index == 10:
    #         runs = remaining_runs

    #     remaining_runs -= runs

    #     if remaining_runs > 0:
    #         remaining_runs = 0
        
    #     PlayerScorecard.objects.create(
    #             match=match,
    #             player=p,
    #             team=team2,
    #             runs=runs,
    #             balls=balls,
    #             fours=random.randint(0, 10),
    #             sixes=random.randint(0, 6),
    #             overs=0,
    #             wickets=0,
    #             runs_conceded=0
    #         )

    MatchScore.objects.create(
        match=qualifier1,
        batting_team=team1,
        bowling_team=team2,
        innings=1,
        runs=q1_team1_score,
        wickets=random.randint(2, 10),
        overs=20
    )

    MatchScore.objects.create(
        match=qualifier1,
        batting_team=team2,
        bowling_team=team1,
        innings=2,
        runs=q1_team2_score,
        wickets=random.randint(2, 10),
        overs=20
    )

    if q1_team1_score > q1_team2_score:

        qualifier1_winner = team1
        qualifier1_loser = team2

    else:

        qualifier1_winner = team2
        qualifier1_loser = team1

    qualifier1.winner = qualifier1_winner
    qualifier1.save()

    
    # ELIMINATOR
    # TEAM 3 vs TEAM 4
    
    eliminator = Match.objects.create(
        team1=team3,
        team2=team4,
        venue=random.choice([
            team3.home_ground,
            team4.home_ground
        ]),
        match_date=timezone.now() + timedelta(days=1),
        status="Completed",
        stage="Eliminator"
    )

    elim_team1_score = random.randint(140, 240)
    elim_team2_score = random.randint(140, 240)

    MatchScore.objects.create(
        match=eliminator,
        batting_team=team3,
        bowling_team=team4,
        innings=1,
        runs=elim_team1_score,
        wickets=random.randint(2, 10),
        overs=20
    )

    MatchScore.objects.create(
        match=eliminator,
        batting_team=team4,
        bowling_team=team3,
        innings=2,
        runs=elim_team2_score,
        wickets=random.randint(2, 10),
        overs=20
    )

    if elim_team1_score > elim_team2_score:

        eliminator_winner = team3

    else:

        eliminator_winner = team4

    eliminator.winner = eliminator_winner
    eliminator.save()

    
    # QUALIFIER 2
    # Q1 LOSER vs ELIMINATOR WINNER
    
    qualifier2 = Match.objects.create(
        team1=qualifier1_loser,
        team2=eliminator_winner,
        venue=random.choice([
            qualifier1_loser.home_ground,
            eliminator_winner.home_ground
        ]),
        match_date=timezone.now() + timedelta(days=2),
        status="Completed",
        stage="Qualifier 2"
    )

    q2_team1_score = random.randint(140, 240)
    q2_team2_score = random.randint(140, 240)

    MatchScore.objects.create(
        match=qualifier2,
        batting_team=qualifier1_loser,
        bowling_team=eliminator_winner,
        innings=1,
        runs=q2_team1_score,
        wickets=random.randint(2, 10),
        overs=20
    )

    MatchScore.objects.create(
        match=qualifier2,
        batting_team=eliminator_winner,
        bowling_team=qualifier1_loser,
        innings=2,
        runs=q2_team2_score,
        wickets=random.randint(2, 10),
        overs=20
    )

    if q2_team1_score > q2_team2_score:

        qualifier2_winner = qualifier1_loser

    else:

        qualifier2_winner = eliminator_winner

    qualifier2.winner = qualifier2_winner
    qualifier2.save()

    
    # FINAL
    # Q1 WINNER vs Q2 WINNER
    
    final = Match.objects.create(
        team1=qualifier1_winner,
        team2=qualifier2_winner,
        venue=random.choice([
            qualifier1_winner.home_ground,
            qualifier2_winner.home_ground
        ]),
        match_date=timezone.now() + timedelta(days=3),
        status="Completed",
        stage="Final"
    )

    final_team1_score = random.randint(140, 240)
    final_team2_score = random.randint(140, 240)

    MatchScore.objects.create(
        match=final,
        batting_team=qualifier1_winner,
        bowling_team=qualifier2_winner,
        innings=1,
        runs=final_team1_score,
        wickets=random.randint(2, 10),
        overs=20
    )

    MatchScore.objects.create(
        match=final,
        batting_team=qualifier2_winner,
        bowling_team=qualifier1_winner,
        innings=2,
        runs=final_team2_score,
        wickets=random.randint(2, 10),
        overs=20
    )

    if final_team1_score > final_team2_score:

        champion = qualifier1_winner

    else:

        champion = qualifier2_winner

    final.winner = champion
    final.save()

    return redirect('ipl:matches')

def points_table(request):

    table = PointsTable.objects.all()

    return render(
        request,
        "points_table.html",
        {
            "table": table
        }
    )

def qualify_team(request):

    qualifier1 = Match.objects.get(
        stage="Qualifier 1"
    )

    eliminator = Match.objects.get(
        stage="Eliminator"
    )

    qualifier2 = Match.objects.get(
        stage="Qualifier 2"
    )

    final = Match.objects.get(
        stage="Final"
    )

    context = {
        "qualifier1": qualifier1,
        "eliminator": eliminator,
        "qualifier2": qualifier2,
        "final": final,
    }

    return render(
        request,
        "qualify.html",
        context
    )

def winner(request):
    final = Match.objects.get(stage="Final")

    return render(request, "winner.html", {'final': final})