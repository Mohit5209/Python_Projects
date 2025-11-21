import datetime
import logging
import os
from logging.handlers import RotatingFileHandler
from src.constants.constants import Constants as c


class Logger(object):
    """
    This class responsible to Logger Object to write application log
    """

    def __check_log_exists(self, root_path, timestamp):
        year_folder_path = os.path.join(root_path, str(timestamp.year))
        month_name_in_str = datetime.datetime.strptime(str(timestamp.month), "%m").strftime("%b")
        month_folder_path = os.path.join(year_folder_path, month_name_in_str)
        day_folder_path = os.path.join(month_folder_path, str(timestamp.day))
        mode = c.ALL_PERMISSION

        if not os.path.exists(root_path):
            try:
                os.mkdir(root_path, mode)
            except FileExistsError as err:
                print("Root folder path already exists {}".format(err))
        if not os.path.exists(year_folder_path):
            try:
                os.mkdir(year_folder_path, mode)
            except FileExistsError as err:
                print("Year folder path already exists {}".format(err))
        if not os.path.exists(month_folder_path):
            try:
                os.mkdir(month_folder_path, mode)
            except FileExistsError as err:
                print("Month folder path already exists {}".format(err))
        if not os.path.exists(day_folder_path):
            try:
                os.mkdir(day_folder_path, mode)
            except FileExistsError as err:
                print("Day folder path already exists {}".format(err))
    
        logger_file_path = os.path.join(day_folder_path, c.LOG_FILE_NAME.format(timestamp.date()))
        return logger_file_path

    @staticmethod
    def get_logger():
        """
            This method returns a logger object and configures logging as per
            Parameters defined in configuration file
        Return:
            logger: It returns logger object.
        """
        logger = None
        try:
            logger = logging.getLogger(__name__)
            if not logger.handlers:
                current_timestamp = datetime.datetime.now()
                root_path = os.path.join(c.ROOT_DIR_PATH, c.LOGGER_ROOT_FOLDER_NAME)
                logging_file_path = Logger().__check_log_exists(root_path, current_timestamp)
                logging.basicConfig(format='%(asctime)s {%(pathname)s:%(lineno)d} - %(levelname)s - %(message)s',
                                    level=logging.DEBUG, handlers=[RotatingFileHandler(filename=logging_file_path,
                                                                                       maxBytes=c.MAX_BYTES,
                                                                                       backupCount=c.BACKUP_COUNT,
                                                                                       encoding="utf-8")])

        except Exception as error:
            logger.error(error)
            raise Exception()
        return logger
