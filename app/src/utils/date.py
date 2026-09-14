from datetime import datetime
import re
from datetime import timedelta

def get_week_and_month(date_str):
    if date_str == 'need to see it manual' or not date_str:
        return 'need to see it manual', 'need to see it manual'
        
    try:
        date_obj = datetime.strptime(date_str, "%m/%d/%Y")
        
        video_week = date_obj.isocalendar()[1]
        video_month = date_obj.month
        
        return video_week, video_month
    except:
        return 'need to see it manual', 'need to see it manual'
    
def convert_to_exact_date(date_text):
    if not date_text or date_text == 'need to see it manual':
        return 'need to see it manual'
        
    date_text = str(date_text).lower().strip()
    now = datetime.now()
    
    if "yesterday" in date_text or "ayer" in date_text:
        return (now - timedelta(days=1)).strftime("%m/%d/%Y")
        
    match = re.search(r'(\d+)\s+(minute|minuto|hour|hora|day|día|dia|week|semana)', date_text)
    if match:
        num = int(match.group(1))
        unit = match.group(2)
        
        if unit in ["minute", "minuto", "hour", "hora"]:
            return now.strftime("%m/%d/%Y")
        elif unit in ["day", "día", "dia"]:
            return (now - timedelta(days=num)).strftime("%m/%d/%Y")
        elif unit in ["week", "semana"]:
            return (now - timedelta(weeks=num)).strftime("%m/%d/%Y")
            
    year_match = re.search(r'(20\d{2})', date_text)
    temp_text = date_text.replace(year_match.group(1), "") if year_match else date_text
    day_match = re.search(r'(?<!\d)(\d{1,2})(?!\d)', temp_text)
    
    month_map = {
        'jan': '01', 'ene': '01', 'feb': '02', 'mar': '03', 'apr': '04', 'abr': '04',
        'may': '05', 'jun': '06', 'jul': '07', 'aug': '08', 'ago': '08', 'sep': '09',
        'oct': '10', 'nov': '11', 'dec': '12', 'dic': '12'
    }
    
    month_val = None
    for m_key, m_val in month_map.items():
        if m_key in date_text:
            month_val = m_val
            break
            
    if year_match and day_match and month_val:
        day_val = day_match.group(1).zfill(2)
        return f"{month_val}/{day_val}/{year_match.group(1)}"
        
    return date_text.title()