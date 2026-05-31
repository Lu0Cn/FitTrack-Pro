from datetime import datetime, timedelta

def calculate_age(birth_date_str):
    try:
        birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d")
        today = datetime.today()
        return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    except:
        return 30 # Default

def calculate_bmi(weight_kg, height_cm):
    if not height_cm: return 0
    height_m = height_cm / 100
    return round(weight_kg / (height_m ** 2), 2)

def calculate_bmr(weight_kg, height_cm, age, gender):
    """
    Mifflin-St Jeor Equation:
    Men: (10 × weight in kg) + (6.25 × height in cm) - (5 × age in years) + 5
    Women: (10 × weight in kg) + (6.25 × height in cm) - (5 × age in years) - 161
    """
    base = (10 * weight_kg) + (6.25 * height_cm) - (5 * age)
    if gender == "Male":
        return round(base + 5)
    else:
        return round(base - 161)

def calculate_tdee(bmr, activity_level):
    multipliers = {
        "Sedentary (office job)": 1.2,
        "Lightly active (1-3 days/week)": 1.375,
        "Moderately active (3-5 days/week)": 1.55,
        "Very active (6-7 days/week)": 1.725,
        "Super active (physical job)": 1.9
    }
    return round(bmr * multipliers.get(activity_level, 1.2))

def estimate_goal_date(current_weight, target_weight, weekly_loss_kg):
    if current_weight <= target_weight:
        return datetime.today().strftime("%Y-%m-%d")
    
    loss_needed = current_weight - target_weight
    weeks_needed = loss_needed / weekly_loss_kg
    days_needed = weeks_needed * 7
    
    target_date = datetime.today() + timedelta(days=days_needed)
    return target_date.strftime("%Y-%m-%d")

def get_bmi_category(bmi):
    if bmi < 18.5: return "Underweight"
    elif bmi < 25: return "Normal weight"
    elif bmi < 30: return "Overweight"
    else: return "Obese"
