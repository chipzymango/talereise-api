from rapidfuzz import process, fuzz

def correct_stop_place(stop, stop_list, threshold=65):
    match, score, _ = process.extractOne(stop, stop_list,scorer=fuzz.ratio)

    if score >= threshold:
        return match # correcting the word to the match found
    else:
        return stop