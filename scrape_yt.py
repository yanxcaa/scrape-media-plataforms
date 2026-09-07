import os
import streamlit as st
from playwright.sync_api import sync_playwright
import openpyxl
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter
from datetime import datetime
import re
import io
from datetime import timedelta

os.system("playwright install chromium")

def convert_to_exact_date(date_text):
    if not date_text or date_text == 'need to see it manual':
        return 'need to see it manual'
        
    date_text = str(date_text).lower().strip()
    now = datetime.now()
    
    if "yesterday" in date_text or "ayer" in date_text:
        return (now - timedelta(days=1)).strftime("%m/%d/%Y")
        
    match = re.search(r'(\d+)', date_text)
    if match:
        num = int(match.group(1))
        
        if "minute" in date_text or "minuto" in date_text or "hour" in date_text or "hora" in date_text:
            return now.strftime("%m/%d/%Y")
            
        elif "day" in date_text or "día" in date_text or "dia" in date_text:
            return (now - timedelta(days=num)).strftime("%m/%d/%Y")
            
        elif "week" in date_text or "semana" in date_text:
            return (now - timedelta(weeks=num)).strftime("%m/%d/%Y")
            
    return date_text.title()

def parse_youtube_number(text):
    text = text.upper().strip()
    if 'K' in text:
        return int(float(text.replace('K', '')) * 1000)
    if 'M' in text:
        return int(float(text.replace('M', '')) * 1000000)
    if text.isdigit():
        return int(text)
    return text

def t_scrape(page, url: str):
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
        

def scrape(page, url: str):
    page.goto(url)

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
        date_selector = '#info span.style-scope.yt-formatted-string'
        page.wait_for_selector(date_selector, timeout=5000)
        raw_date = page.locator(date_selector).nth(2).inner_text()
        
        date = convert_to_exact_date(raw_date)
    except:
        date = 'need to see it manual'
        

    try:
        views_locator = page.locator('#info span.style-scope.yt-formatted-string').first
        views_locator.wait_for(timeout=5000)
        raw_views = views_locator.inner_text().split(' ')[0]
        clean_views = raw_views.strip()
        views_count = parse_youtube_number(clean_views)
    except:
        views_count = "need to see it manual"

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

def read_urls_from_excel(uploaded_file):
    workbook = openpyxl.load_workbook(uploaded_file)
    sheet = workbook.worksheets[0] 
    urls = []
    
    for row in sheet.iter_rows(min_row=2, max_col=1, values_only=True):
        if row[0]:
            urls.append(str(row[0]).strip())
            
    return urls

def generate_excel_in_memory(data):
    wb = openpyxl.Workbook()
    ws = wb.worksheets[0] 
    ws.title = "Scrape Results"
    
    headers = ['KOL Type', 'KOL', 'Date', 'Week', 'Month', 'Platform', 'Link', 'Game', 'Views', 'Comments', 'Likes', 'Timestamp']
    ws.append(headers)
    
    header_fill = PatternFill(start_color="c5a8f0", end_color="8b52e0", fill_type="solid")
    for cell in ws[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = header_fill
        
    for row in data:
        ws.append(row)
        
    for col_idx, col in enumerate(ws.columns, 1):
        max_length = 0
        column_letter = get_column_letter(col_idx)
        
        for cell in col:
            if cell.value is not None:
                try:
                    cell_length = len(str(cell.value))
                    if cell_length > max_length:
                        max_length = cell_length
                except:
                    pass
                    
        adjusted_width = (max_length + 2)
        ws.column_dimensions[column_letter].width = adjusted_width

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output

st.set_page_config(page_title="Data from Youtube and Twitch")
st.title("Youtube - Twitch data")

(col1,) = st.columns(1)
with col1:
    game = st.text_input('Game:')

uploaded_file = st.file_uploader("Upload your file excel.xlsx", type=["xlsx"])

if st.button("Start!!!"):
    if not uploaded_file:
        st.error("Socio/a suba el archivo primero")
    else:
        video_list = read_urls_from_excel(uploaded_file)
        
        if not video_list:
            st.error("Links invalidos")
        else:
            st.info(f"Se encontraron {len(video_list)} links....")
            
            now = datetime.now()
            current_week = now.isocalendar()[1]
            current_month = now.month
            kol_type = 'Coupon'
            
            results_data = []
            
            progress_bar = st.progress(0)
            status_text = st.empty()

            with sync_playwright() as brodoyourchamba:
                browser = brodoyourchamba.chromium.launch(headless=True)
                context = browser.new_context(viewport={'width': 1280, 'height': 720})
                page = context.new_page()
                
                for index, link in enumerate(video_list):
                    progress_bar.progress((index + 1) / len(video_list))
                    status_text.text(f"link: {link}")
                    
                    if ('youtu' in link.lower()):           
                        views, likes, comments, date, platform, kol = scrape(page, link)
                    elif ('twitch' in link.lower()):
                        views, date, kol, platform = t_scrape(page, link)
                        likes = "-"
                        comments = "-"
                    else:
                        continue
                    
                    row_data = [
                        kol_type,
                        kol,
                        date,
                        current_week,
                        current_month,
                        platform,
                        link,
                        game,
                        views,
                        comments,
                        likes,
                        '-'
                    ]
                    results_data.append(row_data)
                    
                browser.close()

            status_text.success("Completado")
            
            excel_file = generate_excel_in_memory(results_data)
            
            st.download_button(
                label="Descargar el archivo",
                data=excel_file,
                file_name="result.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )