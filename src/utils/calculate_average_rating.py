def calculate_average_rating(comments_rating: list[int], scale: int = 10) -> float | None:
    total_rating = sum(comments_rating)
    count = len(comments_rating)

    if count == 0:
        return None
    else:
        return float(format(total_rating / count * scale, '.2f'))
