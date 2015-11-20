__author__ = 'andrew'

import configparser

config = configparser.ConfigParser()
config.read('server.config')

default_col_count = int(config.get('Settings', 'default_col_count', fallback=10))
default_row_count = int(config.get('Settings', 'default_row_count', fallback=10))
starting_cookie_count = int(config.get('Settings', 'starting_cookie_count', fallback=3))
port = int(config.get('Settings', 'port', fallback=9999))

tile_navigable = int(config.get('Settings', 'tile_navigable', fallback=0))
tile_unnavigable = int(config.get('Settings', 'tile_unnavigable', fallback= -1))

encoding='UTF-8'
cookie_speed = int(config.get('Settings', 'cookie_speed', fallback= 2))

walls=int(config.get('Settings', 'walls', fallback= 1))
wallGaps=int(config.get('Settings', 'wallGaps', fallback= 1))