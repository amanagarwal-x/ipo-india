from ipo import Ipo
from ipo_scraper import TopShareBrokersIPO
import logging
def get_ipos(readable: bool = False,
             open_ipos: bool = False,
             retail: bool = False,
             sme: bool = False):
    try:
        if open_ipos:
            if retail:
                ipos = TopShareBrokersIPO.get_open_retail_ipos()
            elif sme:
                ipos = TopShareBrokersIPO.get_open_sme_ipos()
            else:
                ipos = TopShareBrokersIPO.get_open_ipos()
        else:
            ipos = TopShareBrokersIPO.get_ipos()
        
        if readable:
            ipos = [str(Ipo(name=ipo_name, **ipo_data)) for ipo_name, ipo_data in ipos.items()]
        else:
            ipos = [Ipo(name=ipo_name, **ipo_data) for ipo_name, ipo_data in ipos.items()]

        return ipos
    except Exception:
        raise Exception("Faield to get IPOs")

if __name__ == "__main__":
    ipos = get_ipos(readable=True, open_ipos=False)
    logging.info(ipos)
    