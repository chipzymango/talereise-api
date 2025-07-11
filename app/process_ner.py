from rapidfuzz import process

def correct_stop_place(ner_stop_place, stop_list, threshold=65):
    match, score, _ = process.extractOne(ner_stop_place, stop_list)

    if score >= threshold:
        print("Match found! Corrected to: " + match + ", score: " + str(score))
        return match
    else:
        print("Match not found! Remaining at: " + ner_stop_place + ", score: " + str(score))
        return ner_stop_place