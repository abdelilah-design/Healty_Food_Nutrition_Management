import os
import streamlit as st
import matplotlib.pyplot as plt
from dotenv import load_dotenv

# ===============================
# Load environment variables
# ===============================
load_dotenv()

# ===============================
# Streamlit page config
# ===============================
st.set_page_config(
    page_title="Healthy Food Nutrition Planner",
    page_icon="🥗",
    layout="centered"
)

# ===============================
# Session state initialization
# ===============================
if "food_log" not in st.session_state:
    st.session_state.food_log = []
if "total_calories" not in st.session_state:
    st.session_state.total_calories = 0
if "total_protein" not in st.session_state:
    st.session_state.total_protein = 0

# ===============================
# Food database
# ===============================
food_db = {
    "Chicken Breast": {"calories": 165, "protein": 31},
    "Brown Rice": {"calories": 216, "protein": 5},
    "Eggs": {"calories": 78, "protein": 6},
    "Banana": {"calories": 89, "protein": 1},
    "Greek Yogurt": {"calories": 100, "protein": 10},
    "Oats": {"calories": 150, "protein": 5},
    "Salmon": {"calories": 208, "protein": 20},
    "Broccoli": {"calories": 55, "protein": 4},
}

st.title("🥗 Healthy Food Nutrition Planner")

# ===============================
# Language selector
# ===============================
language_map = {
    "English 🇬🇧": "en",
    "العربية 🇲🇦": "ar",
    "Français 🇫🇷": "fr",
    "Español 🇪🇸": "es"
}
language_label = st.selectbox(
    "🌍 Select Language / اختر اللغة / Choisir la langue / Seleccionar idioma",
    list(language_map.keys())
)
language = language_map[language_label]

# ===============================
# Task prompt
# ===============================
task_description = f"""
Generate a 7-day healthy food nutrition plan for weight gain.
Calories per day: 2800–3500 kcal.
Include breakfast, lunch, dinner, and snacks.
Language: {language}
Rules:
- If Arabic → use clear Arabic food names
- If French → use correct French nutrition terms
- If Spanish → use neutral Spanish
- If English → use simple clear English
- Show daily calories and protein
"""

# ===============================
# CrewAI / AI CALL (SAFE)
# ===============================
@st.cache_data(show_spinner=True)
def generate_meal_plan(prompt: str):
    """
    This function MUST call your CrewAI logic.
    Replace the content inside with your crew.kickoff()
    """
    # ---- PLACEHOLDER ----
    # Example:
    # result = crew.kickoff(inputs={"prompt": prompt})
    # return result
    return f"✅ Meal plan generated successfully!\n\nLanguage: {language}\n\n(Replace this placeholder with CrewAI output)"

# ===============================
# Button to avoid reruns
# ===============================
if st.button("🍽️ Generate Meal Plan"):
    with st.spinner("Generating meal plan..."):
        result = generate_meal_plan(task_description)
        st.success("Done!")
        st.text(result)

# ===============================
# Nutrition Dashboard
# ===============================
st.markdown("## 📊 Nutrition Dashboard")
col1, col2 = st.columns(2)
with col1:
    st.metric("🔥 Calories", st.session_state.total_calories)
with col2:
    st.metric("💪 Protein", st.session_state.total_protein)

maintenance = 2000
if st.session_state.total_calories < maintenance:
    st.success("🔥 Calorie Deficit → Weight Loss Mode")
elif st.session_state.total_calories > maintenance:
    st.warning("⚠️ Calorie Surplus → Weight Gain Mode")
else:
    st.info("⚖️ Maintenance Mode")

# ===============================
# Food Tracker
# ===============================
st.markdown("## 🥗 Food Tracker")
food = st.selectbox("Select food", list(food_db.keys()))
quantity = st.number_input("Quantity", min_value=1, value=1)
if st.button("➕ Add Food"):
    calories = food_db[food]["calories"] * quantity
    protein = food_db[food]["protein"] * quantity
    st.session_state.total_calories += calories
    st.session_state.total_protein += protein
    st.session_state.food_log.append({
        "food": food,
        "qty": quantity,
        "calories": calories,
        "protein": protein
    })
    st.success(f"{food} added ✔")

# ===============================
# Food Log
# ===============================
st.markdown("## 📜 Food Log")
for item in st.session_state.food_log:
    st.write(
        f"🍽️ {item['food']} x{item['qty']} → "
        f"{item['calories']} kcal | {item['protein']}g protein"
    )

# ===============================
# Calories Graph (only if log has data)
# ===============================
if len(st.session_state.food_log) > 0:
    st.markdown("## 📈 Calories Graph")
    values = [x["calories"] for x in st.session_state.food_log]
    fig, ax = plt.subplots()
    ax.plot(values, marker="o")
    ax.set_title("Calories per Meal")
    ax.set_ylabel("Calories")
    st.pyplot(fig)

# ===============================
# Footer
# ===============================
st.markdown("---")
st.caption("Built with Streamlit + CrewAI | Localhost Safe Mode")
