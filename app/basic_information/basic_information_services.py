from ..database_setup import BasicInformation
from .. import db
import logging

logger = logging.getLogger()



class BasicInformationServices:
    def __init__(self):
        pass

    def get_basic_information(self, stock_id):
        basic_information = BasicInformation.query.filter_by(
                id=stock_id).one_or_none()
        return basic_information
