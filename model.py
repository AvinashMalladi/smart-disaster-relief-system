# Prompt:
# Implement simple logic for disaster risk prediction and camp allocation.
#
# The system should:
# - Predict risk level based on rainfall and water level
# - Return HIGH RISK if rainfall > 200 and water > 80
# - Return MEDIUM RISK if rainfall > 100
# - Otherwise return LOW RISK
#
# Also implement a function to suggest the best camp for victims
# based on available capacity and resources (food and water).
#
# Keep the implementation simple and easy to understand.

def predict_disaster(rainfall, water):
    if rainfall > 200 and water > 80:
        return "HIGH RISK"
    elif rainfall > 100:
        return "MEDIUM RISK"
    return "LOW RISK"

def suggest_camp(camps):
    best = None
    score = -1

    for c in camps:
        capacity = c[3]
        occupied = c[4]
        food = c[5]
        water = c[6]

        available = capacity - occupied

        # SMART SCORE
        current_score = available + food + water

        if available > 0 and current_score > score:
            score = current_score
            best = c

    return best