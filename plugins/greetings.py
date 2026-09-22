def colored_button(text: str, callback_data: str = None, url: str = None, style: str = "primary"):
    kwargs = {"text": text}
    if callback_data:
        kwargs["callback_data"] = callback_data
    if url:
        kwargs["url"] = url
    try:
        return InlineKeyboardButton(**kwargs, style=style)
    except TypeError:
        return InlineKeyboardButton(**kwargs)

def parse_buttons_and_clean_text(raw_text: str):
    if not raw_text:
        return "", None

    pattern = r"\[([^\[\]]+)\]\((?:buttonurl:)?\s*(https?://[^\s\)]+)\)|\[([^\[\]]+?)\|(?:\s*)(https?://[^\s]+)\]"
    buttons = []
    lines = raw_text.split("\n")
    cleaned_lines = []

    for line in lines:
        matches = re.findall(pattern, line)
        if matches:
            row = []
            for match in matches:
                text = match[0] if match[0] else match[2]
                url = match[1] if match[1] else match[3]
                
                # Determine color style based on emoji or keyword
                btn_style = "primary"
                if any(x in text.lower() for x in ["help", "rule", "alert", "ban", "danger", "🔴"]):
                    btn_style = "danger"
                elif any(x in text.lower() for x in ["music", "join", "chat", "group", "support", "🟢"]):
                    btn_style = "success"

                row.append(colored_button(text=text.strip(), url=url.strip(), style=btn_style))
            if row:
                buttons.append(row)
        else:
            cleaned_lines.append(line)

    cleaned_text = "\n".join(cleaned_lines).rstrip()
    keyboard = InlineKeyboardMarkup(buttons) if buttons else None
    return cleaned_text, keyboard
    
