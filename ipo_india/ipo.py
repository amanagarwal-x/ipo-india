from typing import List, Union
from datetime import datetime
from pydantic import BaseModel

class Ipo(BaseModel):
    name: str
    open_date: datetime
    close_date: datetime
    ipo_price: Union[float, int, str]
    gmp: Union[float, int, str]
    
    qib : Union[float, str] = ''
    nii : Union[float, str] = ''
    ret : Union[float, str] = ''
    total : Union[float, str] = ''
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def __get_ipo_properties(self) -> dict:
        '''
        Get all the properties of the Ipo object
        '''
        properties = {}
        for attr in vars(self):
            properties[attr] = vars(self)[attr]
        return properties
    
    def readable(self) -> str:
        '''
        Get a readable version of the Ipo object
        '''
        readable_ipo = ''
        properties = self.__get_ipo_properties()
        for property, value in properties.items():
            if value:
                # Convert snake case of the keys to readable format
                readable_key = property.replace('_', ' ').title()
                if property in ['gmp', 'qib', 'nii', 'ret']:
                    readable_key = readable_key.upper()
                if property in ['open_date', 'close_date']:
                    value = self.__datetime_to_readable_date(value)
                if property == 'name':
                    readable_ipo += f'**{value}**\n'
                else:
                    readable_ipo += f'{readable_key}: {value}\n'
        return readable_ipo
    
    def __datetime_to_readable_date(self, datetime_obj: datetime) -> str:
        '''
        Convert datetime object to date string
        '''
        return datetime_obj.strftime('%d %b %Y')

    def __str__(self) -> str:
        return self.readable()
