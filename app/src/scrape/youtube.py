import re
from src.utils.date import convert_to_exact_date
from src.utils.parse import parse_youtube_number

def youtube_scrapping(page, url: str):
    page.goto(url, wait_until="domcontentloaded", timeout=60000)

    try:
        page.locator('button', has_text='Reject all').click(timeout=3000)
    except:
        pass

    try:
        is_live = page.locator('meta[itemprop="isLiveBroadcast"]').count() > 0
        platform = 'Youtube Live' if is_live else 'Youtube'
    except:
        platform = "need to see it manual"

    page.evaluate("window.scrollBy(0, 600)")

    try:
        pattern = re.compile(r"like this video|me gusta", re.IGNORECASE)
        likes_locator = page.get_by_role("button", name=pattern).first
        likes_locator.wait_for(timeout=5000)
        
        aria_text = likes_locator.get_attribute("aria-label") or ""
        numeric_likes_string = "".join(filter(str.isdigit, aria_text))
        likes_count = int(numeric_likes_string) if numeric_likes_string else "need to see it manual"
    except:
        likes_count = "need to see it manual"
        
    try:
        kol_locator = 'ytd-video-owner-renderer #channel-name #text'
        page.wait_for_selector(kol_locator, timeout=5000)
        kol_element = page.locator(kol_locator).first
        
        kol = kol_element.get_attribute('title')
        if not kol:
            kol = kol_element.inner_text().strip()
    except:
        kol = 'need to see it manual'
        
    try:
        try:
            expand_btn = page.locator('ytd-text-inline-expander #expand').first
            expand_btn.wait_for(state="attached", timeout=3000)
            
            expand_btn.click(force=True)
        except:
            try:
                page.evaluate("document.querySelector('ytd-text-inline-expander #expand').click()")
            except:
                pass

        info_card = 'ytd-watch-info-text#ytd-watch-info-text'
        page.wait_for_selector(info_card, timeout=5000)
        
        bold_spans = page.locator(f'{info_card} #info span')
        
        raw_views = bold_spans.nth(0).inner_text()
        numeric_views_string = "".join(filter(str.isdigit, raw_views))
        views_count = int(numeric_views_string) if numeric_views_string else "need to see it manual"
        
        raw_date = bold_spans.last.inner_text()
        date = convert_to_exact_date(raw_date)
        
        if views_count == "need to see it manual":
            raise ValueError("Trigger fallback")
        
        try:
            page.locator('tp-yt-paper-button#collapse').click(timeout=3000)
        except:
            pass

    except:
        try:
            views_locator = page.locator('#info span.style-scope.yt-formatted-string').first
            views_locator.wait_for(timeout=5000)
            raw_views = views_locator.inner_text().split(' ')[0]
            clean_views = raw_views.strip()
            views_count = parse_youtube_number(clean_views)
        except:
            views_count = "need to see it manual"
            
        try:
            date_selector = '#info span.style-scope.yt-formatted-string'
            raw_date = page.locator(date_selector).nth(2).inner_text()
            date = convert_to_exact_date(raw_date)
        except:
            date = "need to see it manual"

    try:
        commentSelector = 'ytd-comments-header-renderer #count yt-formatted-string span'
        page.wait_for_selector(commentSelector, timeout=5000)
        comments_text = page.locator(commentSelector).first.inner_text()
        
        if '\n' in comments_text:
            raise ValueError("Animated comment count detected")
            
        clean_comments = comments_text.replace(',', '').strip()
        if not clean_comments:
            raise ValueError("Empty comments")
    except:
        clean_comments = "need to see it manual"

    return views_count, likes_count, clean_comments, date, platform, kol