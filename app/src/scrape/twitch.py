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
        views = 'NEED TO SEE IT MANUAL'
    
    
    try:
        date_selector = 'div.Layout-sc-1xcs6mc-0.kBZhWz p.CoreText-sc-1txzju1-0.fMPrtl'
        page.wait_for_selector(date_selector, timeout=5000)
        raw_date = page.locator(date_selector).first.inner_text()
        
        date = convert_to_exact_date(raw_date)
    except:
        date = 'NEED TO SEE IT MANUAL'
        
    try:
        game_selector = 'section#live-channel-stream-information a[data-a-target="video-info-game-boxart-link"]'
        page.wait_for_selector(game_selector, timeout=5000)
                
        raw_game_text = page.locator(game_selector).first.inner_text()
                
        clean_text = re.sub(r'[^\w\s]', '', raw_game_text)
                
        game_words = clean_text.split()
        x = []
                
        for word in game_words:
            upper_word = word.upper()
                    
            if upper_word in ['KOTZ']:
                        continue
                        
            if upper_word == 'EX':
                x.append('EX')
            else:
                x.append(upper_word[0])
                                
            game_twitch = ''.join(x)
                
        if game_twitch not in ['SSA', 'SSEX']:
            game_twitch = 'NEED TO SEE IT MANUAL'            
    except:
        game_twitch = 'NEED TO SEE IT MANUAL'
    
    try:
        kol_selector = 'div.Layout-sc-1xcs6mc-0.kEFEDy.metadata-layout__support h1.CoreText-sc-1txzju1-0.ScTitleText-sc-d9mj2s-0.fPJBrv.GsAAv.InjectLayout-sc-1i43xsx-0.kMQdEY.tw-title'
        page.wait_for_selector(kol_selector, timeout=5000)
        kol = page.locator(kol_selector).first.inner_text()
    except:
        kol = 'NEED TO SEE IT MANUAL'
        
    return views, date, kol, platform, game_twitch