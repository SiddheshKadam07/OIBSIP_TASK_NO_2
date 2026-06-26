# ============================================================
#  calculator.py  –  BMI Calculation & Classification Logic
# ============================================================

def calculate_bmi(weight_kg: float, height_m: float) -> float:
    """Return BMI rounded to 2 decimal places."""
    if height_m <= 0:
        raise ValueError("Height must be greater than zero.")
    return round(weight_kg / (height_m ** 2), 2)


def classify_bmi(bmi: float) -> tuple[str, str]:
    """
    Return (category, hex_color) based on WHO BMI ranges.
    Colors:  Underweight=blue, Normal=green, Overweight=orange, Obese=red
    """
    if bmi < 18.5:
        return "Underweight", "#3498db"
    elif bmi < 25.0:
        return "Normal",      "#2ecc71"
    elif bmi < 30.0:
        return "Overweight",  "#f39c12"
    else:
        return "Obese",       "#e74c3c"


def get_health_tip(category: str) -> str:
    """Return a short health tip for each BMI category."""
    tips = {
        "Underweight": (
            "Consider increasing caloric intake with nutritious foods "
            "such as whole grains, lean proteins, and healthy fats. "
            "Consult a doctor or dietitian for a personalised plan."
        ),
        "Normal": (
            "Great job! Maintain your healthy lifestyle with a balanced diet "
            "and at least 150 minutes of moderate exercise per week."
        ),
        "Overweight": (
            "Focus on a balanced, calorie-conscious diet and gradually "
            "increase physical activity. Small, consistent changes make a big difference."
        ),
        "Obese": (
            "Please consult a healthcare professional for a personalised plan. "
            "Medical support, dietary changes, and regular exercise can help significantly."
        ),
    }
    return tips.get(category, "")


def convert_imperial_to_metric(weight_lbs: float,
                                height_ft: float,
                                height_in: float = 0) -> tuple[float, float]:
    """Convert lbs / ft-in → kg / metres."""
    weight_kg = weight_lbs * 0.453592
    height_m  = (height_ft * 12 + height_in) * 0.0254
    return round(weight_kg, 2), round(height_m, 3)


def validate_inputs(weight_kg: float, height_m: float) -> str | None:
    """
    Return an error string if inputs are out of reasonable range,
    otherwise return None.
    """
    if not (1 <= weight_kg <= 500):
        return "Weight must be between 1 and 500 kg."
    if not (0.5 <= height_m <= 2.5):
        return "Height must be between 0.5 and 2.5 m."
    return None
