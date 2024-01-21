def calculate_average_rating(comments_rating: list[int]) -> float | None:
    # Apply linear transformation to map binary scores to ratings
    ratings = [((score + 1) / 2) * 9 + 1 for score in comments_rating]

    if ratings:
        average_rating = sum(ratings) / len(ratings)
        return average_rating
    else:
        return None
