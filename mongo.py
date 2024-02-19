import logging
from pymongo import MongoClient, database
from typing import List
from datetime import datetime

from models import Game, Team
from domain_mapper import to_game, to_team

logger = logging.getLogger(__name__)

class Mongo(object):

    def __init__(self, config):
        self.client = MongoClient(config['ConnectionString'])
        self.database = self.client.get_database(config['Database'])
        self.book_odds_collection = self.database.get_collection(config['BookOddsCollection'])
        self.basketball_teams_collection = self.database.get_collection(config['BasketballTeamsCollection'])

    def get_teams(self) -> List[Team]:
        teams = self.basketball_teams_collection.find({})
        return [ to_team(t_dict) for t_dict in teams ]

    def get_game_odds(self) -> List[Game]:
        games = self.book_odds_collection.find({})
        return [ to_game(g_dict) for g_dict in games ]

    def insert_many(self, games: List[dict[str, any]]) -> database:
        for game in games:
            existing = self.book_odds_collection.find_one({'sport': game['sport'], 'tournament': game['tournament'], 'season': game['season'], 
                                                'home': game['home'], 'away': game['away'], 'game_date': game['game_date']})
            if existing != None and game_odds_same(game['odds'], existing['odds']) == False:
                existing['odds'] = game['odds']
                existing['updated_at'] = datetime.utcnow()
                result = self.book_odds_collection.update_one({"_id": existing["_id"]}, {"$set": {"odds": game["odds"], "updated_at": datetime.utcnow()}})
                logger.info("Updated game {} with result {}".format(existing, result))
            elif existing == None:
                result = self.book_odds_collection.insert_one(game)
                logger.debug("Inserted game {} with id {}".format(game, result.inserted_id))

    def update_one(self, id, game: dict[str, any]) -> database:
        result = self.book_odds_collection.update_one({"_id": id}, {"$set": {"odds": game["odds"], "updated_at": datetime.utcnow()}})
        logger.debug("Updated IDs: {}".format(result.upserted_id))

    def insert_one(self, games: dict[str, any]) -> database:
        result = self.book_odds_collection.insert_one(games)
        logger.debug("Inserted IDs: {}".format(result.inserted_id))

    # call like mongo.delete({'season': 'E2024'})
    def delete(self, filter) -> database:
        if filter:
            self.book_odds_collection.delete_many(filter)

    def close(self):
        self.client.close()


def game_odds_same(list1, list2):
    # Check if the lengths of the lists are the same
    if len(list1) != len(list2):
        return False

    # Compare values of corresponding objects
    for obj1, obj2 in zip(list1, list2):
        if obj1['name'] != obj2['name'] or obj1['home'] != obj2['home'] or obj1['away'] != obj2['away']:
            return False

    # If all corresponding objects have the same values, return True
    return True


