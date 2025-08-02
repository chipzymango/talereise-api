from rapidfuzz import process

def correct_stop_place(stop, stop_list, threshold=65):
    match, score, _ = process.extractOne(stop, stop_list)

    if score >= threshold:
        print("Match found! Corrected to: " + match + ", score: " + str(score))
        return match
    else:
        print("Match not found! Remaining at: " + stop + ", score: " + str(score))
        return stop