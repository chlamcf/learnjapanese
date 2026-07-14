from datetime import datetime, timedelta

def sm2_update(ef, repetition, interval_days, quality):
    """
    Simplified SM-2 update.
    quality: 0-5 scale (0 = total blackout, 5 = perfect recall)
    Returns updated (ef, repetition, interval_days, next_review) tuple.
    """
    if quality < 3:
        repetition = 0
        interval_days = 1
    else:
        repetition += 1
        if repetition == 1:
            interval_days = 1
        elif repetition == 2:
            interval_days = 6
        else:
            interval_days = int(interval_days * ef)

        ef = max(1.3, ef + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))

    next_review = datetime.now() + timedelta(days=interval_days)
    return ef, repetition, interval_days, next_review


def quality_from_correctness(is_correct):
    """
    Maps a simple right/wrong multiple-choice result to an SM-2 quality score.
    Correct -> 4 (good recall), Incorrect -> 2 (failed recall).
    """
    return 4 if is_correct else 2