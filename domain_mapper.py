from typing import List
from datetime import datetime
import logging

from models import Game, Sport, Team, BookOdds

EUROLEAGUE_TOURNAMENT = 'euroleague'

logger = logging.getLogger(__name__)

def to_sport(sport: str) -> Sport:
        match sport.lower():
            case "basketball":
                return Sport.Basketball
            case "soccer":
                return Sport.Soccer
            case "esports":
                return Sport.Esports
            case "darts":
                return Sport.Darts    
            case "american-football":
                return Sport.AmericanFootball  
            case "volleyball":
                return Sport.Voleyball 
            case "baseball":
                return Sport.Baseball 
            case "rugby-union":
                return Sport.RugbyUnion   
            case "rugby-league":
                return Sport.RugbyLeague  
            case "handball":
                return Sport.Handball  
            case "hockey":
                return Sport.Hockey                        
            case _:
                return Sport.Unknown
            
def to_sport_name(sport: Sport) -> str:
        match sport:
            case Sport.Basketball:
                return "basketball"
            case Sport.Soccer:
                return "soccer"
            case Sport.Esports:
                return "esports"
            case Sport.Darts:
                return "darts"    
            case Sport.AmericanFootball:
                return "american-football" 
            case Sport.Voleyball:
                return "volleyball"
            case Sport.Baseball:
                return "baseball"
            case Sport.RugbyUnion:
                return "rugby-union"
            case Sport.RugbyLeague:
                return "rugby-league"
            case Sport.Handball:
                return "handball"
            case Sport.Hockey:
                return "hockey"                     
            case _:
                return "unknown"  
          
class DomainMapper(object):

    def __init__(self, teams: List[Team]):
        self.teams = teams

    def to_season(self, sport: Sport, tournament: str, season: str) -> str:
        match (sport, tournament, season):
            case (Sport.Basketball, EUROLEAGUE_TOURNAMENT, ''):
                return get_current_euroleague_season()
            case (Sport.Basketball, EUROLEAGUE_TOURNAMENT, _):
                return season if season[0] == 'E' and len(season) == 5 else 'E' + season[0:4]
            case _:
                return season

    def map_to_domain(self, games: List[Game]) -> List[dict[str, any]]:
        list_game_dicts = []
        for game in games:
            game_dict = self.map_game(game)

            if game.sport == Sport.Basketball and game.tournament == EUROLEAGUE_TOURNAMENT:
                game_dict = self.map_euroleague_game(game, game_dict)

            list_game_dicts.append(game_dict)
        
        return list_game_dicts

    def map_game(self, game: Game) -> dict[str, any]:
        game_dict = { 'sport': to_sport_name(game.sport), 'tournament': game.tournament, 'home': game.home, 'away': game.away, 'game_date': game.date, 'season': game.season,
                'odds': [{'name': odd.name, 'home': odd.home, 'away': odd.away} for odd in game.odds], 'inserted_at': datetime.utcnow() }

        if game.home_score != None:
            game_dict['home_score'] = game.home_score
        
        if game.away_score != None:
            game_dict['away_score'] = game.away_score

        return game_dict
                
    def map_euroleague_game(self, game: Game, game_dict: dict[str, any]) -> dict[str, any]:
        game_dict['season'] = self.to_season(game.sport, game.tournament, game.season)
        game_dict['link'] = game.link

        for team in self.teams:
            if team.alias == None or team.name == None:
                continue

            if game.home == None or game.away == None:
                logger.warning("Skipping game with no home or away value {} from link {}".format(game, game.link))

            home = game.home.lower()
            away = game.away.lower()

            if team.alias.lower() == home or team.name.lower() == home or (team.external_name != None and team.external_name.lower() == home) or (team.external_name != None and team.external_name.lower() + " " + team.alias.lower() == home):
                game_dict['home_code'] = team.code
            elif team.alias.lower() == away or team.name.lower() == away or (team.external_name != None and team.external_name.lower() == away) or (team.external_name != None and team.external_name.lower() + " " + team.alias.lower() == away):
                game_dict['away_code'] = team.code

        if game_dict.get('home_code') is None:
            print("Could not map home team " + game.home)

        if game_dict.get('away_code') == None:
            print("Could not map away team " + game.away)
        return game_dict
    
def to_team(team: dict[str, any]) -> Team:
    return Team(team['name'], team['alias'], team['_id'], team.get('externalName', None))

def to_game(game: dict[str, any]) -> Game:
    odds = [ to_odd(odd_dict) for odd_dict in game.get('odds') ]
    game = Game(to_sport(game.get('sport', '')), game.get('tournament'), game.get('home'), game.get('away'), 
                game.get('game_date'), game.get('season'), game.get('home_score', None), game.get('away_score', None), odds, game.get('link', None), game.get('_id'))
    return game

def to_odd(odd: dict[str, any]) -> BookOdds:
    return BookOdds(odd.get('name'), odd.get('home'), odd.get('away'))

def get_current_euroleague_season() -> str:
    return 'E{}'.format(datetime.utcnow().year - 1) if datetime.utcnow().month <= 6 else 'E{}'.format(datetime.utcnow().year)