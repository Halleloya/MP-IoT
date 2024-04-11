import configparser

config = configparser.ConfigParser()
config.read('config/config.ini')
config_dict = dict()

for section in config.sections():
    config_dict.update({(section + "_" + k): v for k, v in config[section].items()})

config_dict["UPLOAD_FOLDER"] = "upload"
