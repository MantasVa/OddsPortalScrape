import json

from mongo import Mongo
from domain_mapper import DomainMapper, to_sport_name

def get_config():
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)
        return config
    

config = get_config()
mongo = Mongo(config)
odds = mongo.get_game_odds()
teams = mongo.get_teams()

for odd in odds:
    if len(odd.odds) > 0 and isinstance(odd.odds[0].home, str):
        odd.odds = list(filter(lambda book_odds: book_odds.home != "-" and book_odds.away != "-", odd.odds))
        for book in odd.odds:
            if book.home != "-" and book.away != "-":
                book.home = float(book.home)
                book.away = float(book.away)
        game_upd = DomainMapper(teams).map_to_domain([odd])[0]
        mongo.update_one(odd.id, game_upd)


