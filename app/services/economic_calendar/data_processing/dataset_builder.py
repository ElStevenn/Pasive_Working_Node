from bs4 import BeautifulSoup
from services.economic_calendar.data_processing import cleaner
from services.economic_calendar.data_fetching import fetcher

import requests


feacher = fetcher.DataFetcher()
clenaer_ = cleaner.DataCleaner()


async def trading_view_news():

    url = "https://www.tradingview.com/#main-market-summary"
    headers = {
         'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'en-US,en;q=0.9,es-ES;q=0.8,es;q=0.7',
        'cache-control': 'max-age=0',
        'cookie': 'theme=dark; _ga=GA1.1.1807097056.1710441614; cookiesSettings={"analytics":true,"advertising":true}; cookiePrivacyPreferenceBannerProduction=accepted; g_state={"i_p":1711273722472,"i_l":3}; device_t=aGtYZEFROjA.jXV_DENGaIWxV-N2tmbTHTP1HJVgCMIVmXTBqNPvLq0; sessionid=lav2u1v8kscx6r2h2wk1tsnz7wwnn37w; tv_ecuid=74b14ed2-3927-4243-b312-13c52ec85b1d; __eoi=ID=116cfdc8a497d74b:T=1710668926:RT=1716659570:S=AA-AfjYcmAX1nZf8PKZI0LhXjuse; _gcl_au=1.1.323970221.1716659715; sessionid_sign=v3:kRP8DOdqdBHkl3DS5t8qQ9dBozeIWyyXTX6oD5GbFQ4=; backend=prod_backend; backend_sign=v3:6b++IEBp2YyLGIK3HHhCa0eb+xOx+CM1NkAgVtOp0CI=; _sp_ses.cf1a=*; _ga_YVVRYGL0E0=GS1.1.1723201802.556.1.1723203996.51.0.0; _sp_id.cf1a=d87a7156-1f68-4be7-97fd-2f92dbee4c87.1710433204.551.1723204007.1723199807.114d106b-ba74-430a-b25c-0429c0097ca2',
        'priority': 'u=0, i',
        'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36'
    }

    