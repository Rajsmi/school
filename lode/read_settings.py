import configparser

config = configparser.ConfigParser()

config.read('settings.ini')
FIELD = config["GAMEFIELD"]["FIELDS"]
SIZE = config["GAMEFIELD"]["SIZE"]
COLORS = {key: value for key, value in config.items("FIELDS_COLORS")}
