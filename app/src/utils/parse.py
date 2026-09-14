def parse_youtube_number(text):
    text = text.upper().strip()
    if 'K' in text:
        return int(float(text.replace('K', '')) * 1000)
    if 'M' in text:
        return int(float(text.replace('M', '')) * 1000000)
    if text.isdigit():
        return int(text)
    return text