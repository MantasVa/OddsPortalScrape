import logging
import time
import json
from datetime import datetime

from models import Sport
from domain_mapper import DomainMapper, to_sport_name
from scraper import Scraper
from mongo import Mongo

def configure_logger(): 
    filename = 'sport_data' + str(datetime.now().year) + '0' + str(datetime.now().month) if datetime.now().month < 10 else datetime.now().month
    extension = '.log'

    # Configure the logging module
    logging.basicConfig(
        filename='C:\\Projects\\Tasks\\Logs\\' + filename + extension, 
        level=logging.INFO, 
        format='%(asctime)s  [%(levelname)s] %(message)s [BookOddsScrape]')
    logging.Formatter.converter = time.gmtime
    logging.getLogger().addHandler(logging.StreamHandler())

def get_config():
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)
        return config

def main():
    configure_logger()
    config = get_config()

    # games = Scraper().scrape_oddsportal_historical(sport = to_sport_name(Sport.Basketball), country = 'europe', tournament= 'euroleague', 
     #                                                start_season = '2023-2024', nseasons = 1, current_season = 'yes', max_page = 10)
    
    games = Scraper().scrape_oddsportal_upcoming(sport = to_sport_name(Sport.Basketball), country = 'europe', tournament= 'euroleague')
    
    mongo = Mongo(config)
    teams = mongo.get_teams()
    game_dicts = DomainMapper(teams).map_to_domain(games)
    mongo.insert_many(game_dicts)
    mongo.close()

if __name__ == "__main__":
    main()
    