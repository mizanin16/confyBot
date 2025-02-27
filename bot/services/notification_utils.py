def get_day_word(count: int) -> str:
    if count % 10 == 1 and count % 100 != 11:
        return "день"
    elif count % 10 in [2, 3, 4] and not (count % 100 in [12, 13, 14]):
        return "дня"
    else:
        return "дней"