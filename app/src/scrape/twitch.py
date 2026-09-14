import re
from src.utils.parse import parse_youtube_number
from src.utils.date import convert_to_exact_date

def twitch_scrapping(page, url: str):
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
    except Exception:
        pass
    
    platform = 'Twitch'
    
    page.evaluate("window.scrollBy(0, 300)")
    
    try:
        views_pattern = re.compile(r"^[\d,KMB\.]+\s*(?:views|vistas)$", re.IGNORECASE)
        views_locator = page.get_by_text(views_pattern).first
        
        views_locator.wait_for(timeout=15000)
        whole_views = views_locator.inner_text()
        
        raw_views = whole_views.split(' ')[0]
        clean_views = raw_views.replace(',', '').strip()
        
        views = parse_youtube_number(clean_views)
    except:
        views = 'need to see it manual'
    
    
    try:
        date_selector = 'div.Layout-sc-1xcs6mc-0.kBZhWz p.CoreText-sc-1txzju1-0.fMPrtl'
        page.wait_for_selector(date_selector, timeout=5000)
        raw_date = page.locator(date_selector).first.inner_text()
        
        date = convert_to_exact_date(raw_date)
    except:
        date = 'need to see it manual'
    
    try:
        kol_selector = 'div.Layout-sc-1xcs6mc-0.kEFEDy.metadata-layout__support h1.CoreText-sc-1txzju1-0.ScTitleText-sc-d9mj2s-0.fPJBrv.GsAAv.InjectLayout-sc-1i43xsx-0.kMQdEY.tw-title'
        page.wait_for_selector(kol_selector, timeout=5000)
        kol = page.locator(kol_selector).first.inner_text()
    except:
        kol = 'need to see it manual'
        
    return views, date, kol, platform     