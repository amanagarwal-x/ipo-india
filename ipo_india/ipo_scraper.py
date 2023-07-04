import requests
from bs4 import BeautifulSoup
from datetime import datetime
from pytz import timezone
import logging
import sys
from typing import Union

logging.basicConfig(filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO,
                    stream=sys.stdout)

class TopShareBrokersIPO:
    GMP_URL = "https://www.topsharebrokers.com/report/live-ipo-gmp/331/"
    SUBSCRIPTION_URL = "https://www.topsharebrokers.com/report/ipo-subscription-live/333/"
    
    @classmethod
    def _get_ipos_with_gmp(cls):
        rows = cls.__get_report_data_table(cls.GMP_URL).find_all('tr')

        ipo_names = [row.find_all('td')[0].text for row in rows if row.find_all('td')]
        ipo_open_dates = []
        ipo_close_dates = []
        gmps = []
        ipo_prices = []
        for row in rows:
            if row.find_all('td'):
                try:
                    open_date = row.find_all('td')[-4].text
                    open_date = cls.__parse_ipo_date(open_date)
                    ipo_open_dates.append(open_date)
                except:
                    ipo_open_dates.append("")
                try:
                    close_date = row.find_all('td')[-3].text
                    close_date = cls.__parse_ipo_date(close_date)
                    ipo_close_dates.append(close_date)
                except:
                    ipo_close_dates.append("")
                try:
                    gmps.append(row.find_all('td')[1].text)
                except:
                    gmps.append("")
                try:
                    ipo_prices.append(row.find_all('td')[-6].text)
                except:
                    ipo_prices.append("")
    
        ipos = {}
        for name, open_date, close_date, gmp, ipo_price in zip(ipo_names, ipo_open_dates, ipo_close_dates, gmps, ipo_prices):
            if name and open_date and close_date:
                ipos[name] = {'open_date': open_date, 'close_date': close_date, 'gmp': gmp, 'ipo_price': ipo_price}
        return ipos
    
    @classmethod
    def _get_ipos_with_subscription(cls):
        table = cls.__get_report_data_table(cls.SUBSCRIPTION_URL)
        rows = table.find_all('tr')
        
        name_column_table_index = cls._find_column_index(table, 'name')
        name_column_table_index = cls._find_column_index(table, 'ipo') if not name_column_table_index else name_column_table_index
        qib_column_table_index = cls._find_column_index(table, 'qib')
        nii_column_table_index = cls._find_column_index(table, 'nii')
        ret_column_table_index = cls._find_column_index(table, 'rii')
        total_column_table_index = cls._find_column_index(table, 'total')
        
        ipo_names = []
        qib_subscriptions = []
        nii_subscriptions = []
        ret_subscriptions = []
        total_subscriptions = []
        for row in rows:
            if row.find_all('td'):
                try:
                    ipo_names.append(row.find_all('td')[name_column_table_index].text)
                except Exception as e:
                    ipo_names.append(f"Exception {e}")
                try:
                    qib_subscriptions.append(row.find_all('td')[qib_column_table_index].text)
                except:
                    qib_subscriptions.append("")
                try:
                    nii_subscriptions.append(row.find_all('td')[nii_column_table_index].text)
                except:
                    nii_subscriptions.append("")
                try:
                    ret_subscriptions.append(row.find_all('td')[ret_column_table_index].text)
                except:
                    ret_subscriptions.append("")
                try:
                    total_subscriptions.append(row.find_all('td')[total_column_table_index].text)
                except:
                    total_subscriptions.append("")

        ipo_subscriptions = {}
        for name, qib, nii, ret, total in zip(ipo_names, qib_subscriptions, nii_subscriptions, ret_subscriptions, total_subscriptions):
            if name and qib and nii and ret and total:
                ipo_subscriptions[name] = {'qib': qib, 'nii': nii, 'ret': ret, 'total': total}
        return ipo_subscriptions
    
    @staticmethod
    def _find_column_index(table, column_name: str) -> Union[None, int]:
        column_index = None
        for index, column in enumerate(table.find_all('th')):
            if column_name in column.text.lower():
                column_index = index
                break
        return column_index
    
    @staticmethod
    def __get_report_data_table(request_url):
        r = requests.get(request_url)
        soup = BeautifulSoup(r.content, 'html5lib')
        report_data_div = soup.find(id = "report_data")
        table = report_data_div.find('table')
        return table

    @classmethod
    def get_ipos(cls):
        ipos = cls._get_ipos_with_gmp()
        ipo_subscriptions = cls._get_ipos_with_subscription()
        
        logging.debug(f"{ipos=}")
        logging.debug(f"{ipo_subscriptions=}")
        
        # cannot assume ipos and ipo_subscriptions tables have ipos in same order
        # Both tables have names of ipos in different formats. So matching first word of ipo name
        for ipo in ipos:
            for ipo_sub in ipo_subscriptions:
                if ipo.split()[0] == ipo_sub.split()[0]:
                    ipos[ipo] = ipos[ipo] | ipo_subscriptions[ipo_sub]
                    break
        return ipos
    
    @classmethod
    def get_open_ipos(cls):
        ipos = cls.get_ipos()
        open_ipos = {}
        today_midnight_ist = datetime.combine(datetime.now(timezone("Asia/Kolkata")), datetime.min.time())

        for ipo_name, ipo_data in ipos.items():
            if ipo_data['open_date'] <= today_midnight_ist <= ipo_data['close_date']:
                open_ipos[ipo_name] = ipo_data
        return open_ipos
    
    @classmethod
    def get_open_retail_ipos(cls):
        ipos = cls.get_open_ipos()
        open_retail_ipos = {}
        for ipo_name in ipos:
            if 'SME' not in ipo_name.upper():
                open_retail_ipos[ipo_name] = ipos[ipo_name]
        return open_retail_ipos
    
    @classmethod
    def get_open_sme_ipos(cls):
        ipos = cls.get_open_ipos()
        open_sme_ipos = {}
        for ipo_name in ipos:
            if 'SME' in ipo_name.upper():
                open_sme_ipos[ipo_name] = ipos[ipo_name]
        return open_sme_ipos
    
    @staticmethod
    def __parse_ipo_date(date_str):
        return datetime.strptime(date_str, '%d-%b-%Y')
