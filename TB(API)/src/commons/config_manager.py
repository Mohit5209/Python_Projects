import configparser
import os

from src.constants.constants import Constants
from src.exceptions.FileFolder_exception import *


class ConfigManager:
    """
    This class opens the configuration file and
    reads all the configuration provided inside it
    """

    def __new__(self):
        if not hasattr(self, 'instance'):
            file_name = Constants.CONFIG_FILE_PATH
            self.parser = configparser.ConfigParser()
            self.parser.optionxform = str
            self.config = self.parser  
            if os.path.exists(file_name):
                self.config.read(file_name, encoding=Constants.UTF_8_ENCODING)
            else:
                raise FileNotFoundException('No Config file found!')

            self.instance = super(ConfigManager, self).__new__(self)

        return self.config


class ReadConfigFile:
    """
    This class reads specific configurations based on user requirement
    """

    objConfig = ''

    def __init__(self):
        self.obj_config = ConfigManager()

    def get_env_config(self, param):
        """

        Arguments:
            param -- Parameter to retrieve from Default Env

        Returns:
            Parameter value
        """
        env_config = self.obj_config[Constants.DEFAULT_ENVIRONMENT]
        return env_config[param]

    def get_value_config(self, section, param):
        """

        Arguments:
            section -- Environment to retrieve value from
            param -- Parameter to retrieve from Env

        Returns:
            Parameter value
        """
        env_config = self.obj_config[section]
        return env_config[param]


cfg = ReadConfigFile()
