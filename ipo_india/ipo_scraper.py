import requests
from bs4 import BeautifulSoup
from datetime import datetime
from pytz import timezone
import logging
import sys
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
        rows = cls.__get_report_data_rows(cls.GMP_URL)

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
        rows = cls.__get_report_data_rows(cls.SUBSCRIPTION_URL)
        
        # ipo_names = [row.find_all('td')[1].text for row in rows if row.find_all('td')]
        ipo_names = []
        for row in rows:
          try:
            if row.find_all('td'):
              ipo_names.append(row.find_all('td')[1].text)
          except:
            pass
        qib_subscriptions = []
        rii_subscriptions = []
        ret_subscriptions = []
        total_subscriptions = []
        for row in rows:
            if row.find_all('td'):
                try:
                    qib_subscriptions.append(row.find_all('td')[2].text)
                except:
                    qib_subscriptions.append("")
                try:
                    rii_subscriptions.append(row.find_all('td')[3].text)
                except:
                    rii_subscriptions.append("")
                try:
                    ret_subscriptions.append(row.find_all('td')[4].text)
                except:
                    ret_subscriptions.append("")
                try:
                    total_subscriptions.append(row.find_all('td')[5].text)
                except:
                    total_subscriptions.append("")

        ipo_subscriptions = {}
        for name, qib, rii, ret, total in zip(ipo_names, qib_subscriptions, rii_subscriptions, ret_subscriptions, total_subscriptions):
            if name and qib and rii and ret and total:
                ipo_subscriptions[name] = {'qib': qib, 'rii': rii, 'ret': ret, 'total': total}
        return ipo_subscriptions
        
    @staticmethod
    def __get_report_data_rows(request_url):
        r = requests.get(request_url)
        soup = BeautifulSoup(r.content, 'html5lib')
        report_data_div = soup.find(id = "report_data")
        table = report_data_div.find('table')
        rows = table.find_all('tr')
        return rows

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
