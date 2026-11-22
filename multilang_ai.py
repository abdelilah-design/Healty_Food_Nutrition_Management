# app_multilang_ai.py

import streamlit as st
from openai import OpenAI
import smtplib
from email.mime.text import MIMEText

# =========================
# CONFIGURATION AI
# =========================
# Assurez-vous d'avoir votre clé OpenAI
client = OpenAI(api_key="YOUR_OPENAI_API_KEY")

# =========================
# LANGUES
# =========================
languages = {
    "English": {
        "title": "🍽️ Nutrition For All",
        "select_profile": "Select your profile",
        "generate_plan": "Generate Meal Plan",
        "send_email": "Email My Plan",
        "enter_email": "Enter your email"
    },
    "Français": {
        "title": "🍽️ Nutrition Pour Tous",
        "select_profile": "Sélectionnez votre profil",
        "generate_plan": "Générer le plan",
        "send_email": "Envoyer mon plan par email",
        "enter_email": "Entrez votre email"
    },
    "Español": {
        "title": "🍽️ Nutrición Para Todos",
        "select_profile": "Selecciona tu perfil",
        "generate_plan": "Generar plan",
        "send_email": "Enviar mi plan por correo",
        "enter_email": "Introduce tu correo"
    },
    "العربية": {
        "title": "🍽️ التغذية للجميع",
        "select_profile": "اختر ملفك الشخصي",
        "generate_plan": "إنشاء خطة الطعام",
        "send_email": "أرسل خطتي بالبريد",
        "enter_email": "أدخل بريدك الإلكتروني"
    }
}

# =========================
# FONCTION IA
# =========================
def generate_meal_plan(profile_type, lang):
    """
    Génère un plan de repas via OpenAI selon le profil et la langue.
    """
    prompt = f"""
    You are a nutrition expert. Create a 7-day healthy meal plan for a {profile_type} person.
    Provide breakfast, lunch, dinner, and snacks.
    Translate the plan to {lang}.
    Include approximate calories, protein, carbs, fats, fiber, and GI values.
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content

# =========================
# FONCTION EMAIL
# =========================
def send_email_plan(user_email, meal_plan, subject="Your Healthy Meal Plan"):
    sender_email = "your.email@example.com"
    password = "YOUR_EMAIL_PASSWORD"

    msg = MIMEText(meal_plan)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = user_email

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, password)
            server.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Error sending email: {e}")
        return False

# =========================
# INTERFACE STREAMLIT
# =========================
st.set_page_config(
    page_title="Healthy Food AI",
    page_icon="🤖🥗",
    layout="centered"
)

# Choix de la langue
selected_lang = st.selectbox("🌍 Language / اللغة / Langue", ["English", "Français", "Español", "العربية"])
text = languages[selected_lang]

st.title(text["title"])

# Choix du profil
profile_type = st.radio(text["select_profile"], ('Diabetic', 'Slim', 'Fat'))

# Bouton pour générer le plan
meal_plan = ""
if st.button(text["generate_plan"]):
    with st.spinner("Generating your meal plan..."):
        meal_plan = generate_meal_plan(profile_type.lower(), selected_lang)
    st.subheader("📝 Meal Plan")
    st.text(meal_plan)

# Envoi par email
user_email = st.text_input(text["enter_email"])
if st.button(text["send_email"]):
    if not meal_plan:
        st.warning("Please generate your meal plan first!")
    elif user_email:
        success = send_email_plan(user_email, meal_plan)
        if success:
            st.success(f"✅ Plan sent to {user_email}")
    else:
        st.warning("Please enter a valid email")
