from datetime import datetime
from enum import Enum

class Sport(Enum):
    Unknown = 0
    Basketball = 1
    Soccer = 2
    Esports = 3
    Darts = 4
    AmericanFootball = 5
    Voleyball = 6
    Baseball = 7
    RugbyUnion = 8
    RugbyLeague = 9
    Handball = 10
    Hockey = 11

class ScrapeType(Enum):
    Unknown = 0
    Historical = 1
    CurrentSeasonHistorical = 2
    Upcoming = 3

class BookOdds:
    def __init__(self, name: str, home: float, away: float) -> None:
        self.name = name
        self.home = home
        self.away = away

class Team:
    def __init__(self, name: str, alias: str, code: str, external_name: str = None) -> None:
        self.name = name
        self.alias = alias
        self.code = code    
        self.external_name = external_name

class Game:
    def __init__(self, sport: Sport, tournament: str, home: str, away: str, date: datetime, season: str, 
                 home_score: int, away_score: int, odds: list[BookOdds], link: str, id = None) -> None:
        self.sport = sport
        self.tournament = tournament
        self.home = home
        self.away = away
        self.date = date
        self.season = season
        self.home_score = home_score
        self.away_score = away_score
        self.odds = odds
        self.link = link
        self.id = id

    def __str__(self):
        return f"{self.home} {self.home_score}:{self.away_score} {self.away} {self.date} {self.season}"