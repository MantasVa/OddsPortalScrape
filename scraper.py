from selenium import webdriver
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
from datetime import datetime
from bs4 import BeautifulSoup
import logging

from models import Game, BookOdds, ScrapeType
from domain_mapper import to_sport

logger = logging.getLogger(__name__)

class Scraper(object):
    """
    A class to scrape game results from oddsportal.com website
    """
    
    def __init__(self):
        self.base_url = 'https://www.oddsportal.com'
        self.wait_on_page_load = 3
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('headless')
        self.options.add_argument("--log-level=3")
        self.driver = webdriver.Chrome(options=self.options)
        # exception when no driver created

    SPORTS = [ 'soccer', 'basketball', 'esports', 'darts', 'tennis', 'baseball', 'rugby-union', 'rugby-league', 'american-football', 'hockey', 'volleyball', 'handball' ]
    SPORTS_TYPE_A = [ 'baseball','esports','basketball','darts', 'american-football', 'volleyball' ]
    SPORTS_TYPE_B = [ 'tennis' ]
    SPORTS_TYPE_C = [ 'soccer', 'rugby-union', 'rugby-league', 'handball' ]
    SPORTS_TYPE_D = [ 'hockey' ]

    def scrape_oddsportal_historical(self, sport = 'football', country = 'france', tournament = 'ligue-1', start_season = '2019-2020', nseasons = 1, 
                                     current_season = 'yes', max_page = 25) -> []:
        ''' Scrapes defined sport tournament historical games in specified seasons from oddsportal.com website '''
        games = []

        if sport not in self.SPORTS :
            logger.warning('Please choose a sport among the following list : \n {} \n'.format(self.SPORTS))
            return games
        elif sport == 'tennis' :
            logger.warning('Please indicate the format of tournament for tennis (3 sets or 5 sets) : \n ')
            return games
            
        if sport in self.SPORTS_TYPE_A:
            games = self.scrape_historical_seasons_typeA(start_season, sport, country, tournament, nseasons, current_season, max_page)
        elif sport in self.SPORTS_TYPE_B:
            logger.warning("Sport {} not supported yet".format(sport))
        elif sport in self.SPORTS_TYPE_C:
            logger.warning("Sport {} not supported yet".format(sport))
        elif sport in self.SPORTS_TYPE_D:
            logger.warning("Sport {} not supported yet".format(sport))
        
        self.close_browser()
        return games
    
    def scrape_oddsportal_upcoming(self, sport = 'football', country = 'france', tournament = 'ligue-1') -> []:
        ''' Scrapes defined sport tournament upcoming games from oddsportal.com website '''
        games = []

        if sport not in self.SPORTS :
            logger.warning('Please choose a sport among the following list : \n {} \n'.format(self.SPORTS))
            return games
        elif sport == 'tennis' :
            logger.warning('Please indicate the format of tournament for tennis (3 sets or 5 sets) : \n ')
            return games
            
        if sport in self.SPORTS_TYPE_A:
            games = self.scrape_upcoming_games_TypeA(sport, country, tournament)
        elif sport in self.SPORTS_TYPE_B:
            logger.warning("Sport {} not supported yet".format(sport))
        elif sport in self.SPORTS_TYPE_C:
            logger.warning("Sport {} not supported yet".format(sport))
        elif sport in self.SPORTS_TYPE_D:
            logger.warning("Sport {} not supported yet".format(sport))
        
        self.close_browser()
        return games

    def scrape_upcoming_games_TypeA(self, sport, country, tournament) -> []:
        return self.scrape_page_typeA(sport, country, tournament, ScrapeType.Upcoming)

    def scrape_historical_seasons_typeA(self, Season, sport, country, tournament, nseason, current_season = 'yes', max_page = 25) -> []:
        # Scrapes the number of seasons in given tournament
        long_season = (len(Season) > 6) # indicates whether Season is in format '2010-2011' or '2011' depends on the tournament) 
        Season = int(Season[0:4])
        games = []
        for _ in range(nseason):
            SEASON1 = '{}'.format(Season)
            if long_season:
                SEASON1 = '{}-{}'.format(Season, Season+1)
            logger.info('We start to collect season {}'.format(SEASON1))
            games += self.scrape_season_typeA(sport, country, tournament, ScrapeType.Historical, SEASON1, max_page)
            logger.info('We finished to collect season {} !'.format(SEASON1))
            Season+=1

        if current_season == 'yes' : 
            SEASON1 = '{}'.format(Season)
            if long_season:
                SEASON1 = '{}-{}'.format(Season, Season+1)
            logger.info('We start to collect current season')
            games += self.scrape_season_typeA(sport, country, tournament, ScrapeType.CurrentSeasonHistorical, SEASON1, max_page)
            logger.info('We finished to collect current season !')

        return games

    def scrape_season_typeA(self, sport, country, tournament, scrapeType: ScrapeType, season = '', max_page = 25) -> []:
        # Scrape all the pages of game data in particular season
        games = []
        for page in range(1, max_page + 1):
            logger.info('We start to scrape the page n°{}'.format(page))
            data = self.scrape_page_typeA(sport, country, tournament, scrapeType, season, page)
            games = games + [y for y in data if y != None]

        return games

    def scrape_page_typeA(self, sport: str, country: str, tournament: str, scrapeType: ScrapeType, season: str = '', page = 1) -> []:
        #Scrape particular page
        games = []

        if scrapeType == ScrapeType.Upcoming:
            self.driver.get(self.base_url + '/{}/{}/{}/'.format(sport, country, tournament))
        elif scrapeType == ScrapeType.CurrentSeasonHistorical:
            self.driver.get(self.base_url + '/{}/{}/{}/results/#/page/{}'.format(sport, country, tournament, page))
        elif scrapeType == ScrapeType.Historical:
            self.driver.get(self.base_url + '/{}/{}/{}-{}/results/#/page/{}'.format(sport, country, tournament, season, page))
        else:
            logger.error("Scrape type not specified - {} for sport {} and tournament {}", scrapeType, sport, tournament)
            return games

        self.scroll_to_the_bottom()
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        eventRows = soup.select('.eventRow')

        games = []
        for row in eventRows:
            link_div = row.find('a', class_='cursor-pointer')
            game_link = link_div.get('href')

            inside_divs = link_div.find('div').find_all('div', recursive=False)
            odd_home = inside_divs[1].find('p').text
            odd_away = inside_divs[2].find('p').text

            if odd_home != "-" or odd_away != "-":
                game = self.scrape_game_type_A(game_link, sport, tournament, scrapeType, season)
                if game != None:
                    games += [ game ]
            else:
                logger.warning("Game skipped due to no odds at location {}".format(self.base_url + game_link))
        
        return(games) 

    def scrape_game_type_A(self, link: str, sport: str, tournament: str, scrapeType: ScrapeType, season: str, retries: int = 0, wait_time = 1) -> Game:
        self.driver.get(self.base_url + link)

        home_team = self.get_text('//*[@id="app"]/div/div[1]/div/main/div[2]/div[2]/div//span')
        away_team = self.get_text('//*[@id="app"]/div/div[1]/div/main/div[2]/div[2]/div[1]/div[3]//span')

        # Upcoming games do not have scores yet (duh)
        home_score, away_score = None, None

        if scrapeType != ScrapeType.Upcoming:
            home_score = self.get_text('//*[@id="app"]/div/div[1]/div/main/div[2]/div[2]/div/div/div//div[contains(@class, "w-full")]')
            away_score = self.get_text('//*[@id="app"]/div/div[1]/div/main/div[2]/div[2]/div[1]/div[3]/div[2]/div')

        date_portion_1 = self.get_text('//div[contains(@class, "event-start-time")]/following-sibling::p[2]')
        date_portion_2 = self.get_text('//div[contains(@class, "event-start-time")]/following-sibling::p[3]')

        date_str = None if date_portion_1 == None or date_portion_2 == None else date_portion_1 + date_portion_2
        date_format = '%d %b %Y,%H:%M'
        date_time =  None if date_str == None else datetime.strptime(date_str, date_format)

            # Now we collect all bookmaker
        book_odds = []
        for j in range(1,30): # only first 10 bookmakers displayed
            book = self.get_text('//div[contains(@class, "text-xs")][{}]/div[@provider-name="0"]/a[2]/p'.format(j)) # bookmaker name
            odd_home = self.get_text('//div[contains(@class, "text-xs")][{}]/div[2]//p'.format(j)) # home odd
            odd_away = self.get_text('//div[contains(@class, "text-xs")][{}]/div[3]//p'.format(j)) # away odd

            if (book != None):
                book_odds = book_odds + [BookOdds(book, odd_home, odd_away)]

        if len(book_odds) > 0:
            logger.info("Game scraped {}:{} at {}".format(home_team, away_team, date_time))
            return Game(to_sport(sport), tournament, home_team, away_team, date_time, season, home_score, away_score, book_odds, self.base_url + link)
        elif retries < 10:
            # Retry policy, increase delay time and cut out once 10 retries are reached
            logger.warning("Game unable to be scraped, could not locate books Retrying.")
            self.scrape_game_type_A(link, sport, tournament, scrapeType, season, retries + 1, wait_time * 2)
        else:
            logger.warning("Game {}:{} at {} was unable to be scraped at location {}. Skipping.".format(home_team, away_team, date_time, self.base_url + link))
            return None    

    def get_text(self, target):
        if self.try_get_text(target) != False :
            return self.driver.find_element(By.XPATH, target).text
        
    def try_get_text(self, target):
        try:
            self.driver.find_element(By.XPATH, target).text
        except:
            return False
        
    def scroll_to_the_bottom(self):
        """A method for scrolling the page."""

        # Get scroll height.
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        while True:

            # Scroll down to the bottom.
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load the page.
            time.sleep(2)

            # Calculate new scroll height and compare with last scroll height.
            new_height = self.driver.execute_script("return document.body.scrollHeight")

            if new_height == last_height:

                break

            last_height = new_height

    def close_browser(self):
        time.sleep(5)
        try:
            self.driver.quit()
            logger.debug('Browser closed')
        except WebDriverException:
            logger.error('WebDriverException on closing browser - maybe closed?')