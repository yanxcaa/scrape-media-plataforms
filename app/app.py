import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import os
import time
import streamlit as st
from playwright.sync_api import sync_playwright

from src.utils.date import get_week_and_month
from src.utils.excel import generate_excel_in_memory, read_urls_from_excel
from src.utils.browser import optimize_page_memory

from src.scrape.youtube import youtube_scrapping
from src.scrape.twitch import twitch_scrapping

os.system("playwright install chromium")

st.set_page_config(page_title="Game Evidence Collection")
st.title("Game Evidence Collection")

(col1,) = st.columns(1)
with col1:
    game = st.text_input('Game:')

uploaded_file = st.file_uploader("Upload your file excel.xlsx", type=["xlsx"])

if st.button("Start!!!"):
    if not uploaded_file:
        st.error("Upload the xlsx file first.")
    else:
        video_list = read_urls_from_excel(uploaded_file)
        
        if not video_list:
            st.error("Invalid Links")
        else:
            st.info(f"{len(video_list)} links were found...")
            
            kol_type = 'Coupon'
            
            results_data = []
            
            progress_bar = st.progress(0)
            status_text = st.empty()

            with sync_playwright() as brodoyourchamba:
                browser = brodoyourchamba.chromium.launch(headless=False)
                context = browser.new_context(viewport={'width': 1280, 'height': 720})
                
                for index, link in enumerate(video_list):
                    progress_bar.progress((index + 1) / len(video_list))
                    status_text.text(f"link: {link}")
                    
                    page = context.new_page()
                    
                    optimize_page_memory(page)
                    
                    scraped_game = None
                    
                    if ('youtu' in link.lower()):           
                        views, likes, comments, date, platform, kol, scraped_game = youtube_scrapping(page, link)
                    elif ('twitch' in link.lower()):
                        views, date, kol, platform, scraped_game = twitch_scrapping(page, link)
                        likes = "-"
                        comments = "-"
                    else:
                        page.close()
                        continue
                    
                    video_week, video_month = get_week_and_month(date)
                    
                    if scraped_game and scraped_game != 'NEED TO SEE IT MANUAL':
                        final_game = scraped_game
                    else:
                        final_game = game
                    
                    row_data = [
                        kol_type,
                        kol,
                        date,
                        video_week,
                        video_month,
                        platform,
                        link,
                        final_game,
                        views,
                        comments,
                        likes,
                        '-'
                    ]
                    results_data.append(row_data)
                    
                    page.close()
                    
                    time.sleep(1.5)
                    
                browser.close()

            status_text.success("Completed")
            
            excel_file = generate_excel_in_memory(results_data)
            
            st.download_button(
                label="Download the File",
                data=excel_file,
                file_name="result.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )