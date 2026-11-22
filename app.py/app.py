import streamlit as st
import io
import json
# ================= FOOD DATABASE =================
food_db = {
    "chicken breast": {"calories": 165, "protein": 31},
    "rice": {"calories": 130, "protein": 2.7},
    "egg": {"calories": 70, "protein": 6},
    "banana": {"calories": 105, "protein": 1.3},
    "apple": {"calories": 95, "protein": 0.5},
    "salmon": {"calories": 208, "protein": 20},
    "yogurt": {"calories": 100, "protein": 10},
    "bread": {"calories": 80, "protein": 3}
}

# ================= SESSION STATE =================
if "total_calories" not in st.session_state:
    st.session_state.total_calories = 0

if "total_protein" not in st.session_state:
    st.session_state.total_protein = 0

if "food_log" not in st.session_state:
    st.session_state.food_log = []
from datetime import datetime, timedelta
from healthy_food_nutrition_management_system.crew import HealthyFoodNutritionManagementSystemCrew
from healthy_food_nutrition_management_system.pdf_generator import MealPlanPDFGenerator

# Page config
st.set_page_config(
    page_title="Nutrition For All - AI Meal Planner",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': 'https://www.nutritionforall.com/help',
        'Report a bug': 'https://www.nutritionforall.com/bug',
        'About': '# Nutrition For All\n### Affordable, Healthy Meals for Everyone!'
    }
)

# Beautiful CSS with improved design
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #48c6ef 50%, #6dd5ed 75%, #2dce89 100%);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
    }
    @keyframes gradient {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }
    .main .block-container {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        backdrop-filter: blur(10px);
    }
    h1 {
        background: linear-gradient(120deg, #2dce89, #48c6ef, #667eea);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-size: 3rem !important;
        font-weight: 800 !important;
    }
    h2, h3 {
        color: #2dce89;
        font-weight: 600;
    }
    .stButton>button {
        border-radius: 15px;
        font-weight: 600;
        transition: all 0.3s ease;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
    }
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
    }
    .info-card {
        background: linear-gradient(135deg, rgba(45, 206, 137, 0.1), rgba(72, 198, 239, 0.1));
        border-left: 4px solid #2dce89;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .premium-badge {
        background: linear-gradient(135deg, #FFD700, #FFA500);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0%, 100% {transform: scale(1);}
        50% {transform: scale(1.05);}
    }
    .pricing-card {
        background: white;
        border-radius: 15px;
        padding: 2rem;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        text-align: center;
        transition: transform 0.3s;
    }
    .pricing-card:hover {
        transform: translateY(-10px);
    }
    .feature-list {
        text-align: left;
        margin: 1rem 0;
    }
    .feature-item {
        padding: 0.5rem 0;
        border-bottom: 1px solid #eee;
    }
    hr {
        margin: 2rem 0;
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #2dce89, transparent);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for user management
if 'user_plan' not in st.session_state:
    st.session_state.user_plan = 'free'  # 'free', 'basic', 'premium'
if 'plans_generated_today' not in st.session_state:
    st.session_state.plans_generated_today = 0
if 'last_reset_date' not in st.session_state:
    st.session_state.last_reset_date = datetime.now().date()
if 'saved_plans' not in st.session_state:
    st.session_state.saved_plans = []
if 'lang' not in st.session_state:
    st.session_state.lang = 'en'
if 'goal' not in st.session_state:
    st.session_state.goal = None
if 'country' not in st.session_state:
    st.session_state.country = 'USA'

# Reset daily counter
if st.session_state.last_reset_date != datetime.now().date():
    st.session_state.plans_generated_today = 0
    st.session_state.last_reset_date = datetime.now().date()

# Plan limits
PLAN_LIMITS = {
    'free': {'daily_plans': 3, 'languages': ['en', 'fr', 'es'], 'countries': 1, 'history': False, 'shopping_list': False},
    'basic': {'daily_plans': 10, 'languages': ['en', 'fr', 'es', 'ar', 'de'], 'countries': 3, 'history': True, 'shopping_list': False},
    'premium': {'daily_plans': 999, 'languages': ['en', 'fr', 'es', 'ar', 'de', 'ms', 'zh', 'ru'], 'countries': 999, 'history': True, 'shopping_list': True}
}

# Translations
TEXTS = {
    'en': {
        'title': '🍽️ Nutrition For All',
        'subtitle': '✨ AI-Powered Affordable Meal Plans ✨',
        'upgrade': '⭐ Upgrade to Premium',
        'free_plan': 'FREE Plan',
        'basic_plan': 'BASIC Plan',
        'premium_plan': 'PREMIUM Plan',
        'plans_left': 'Plans left today',
        'select_lang': '🌍 Language',
        'country': '🌍 Country',
        'choose_goal': '🎯 Your Goal',
        'generate': '🚀 GENERATE',
        'generating': '⏳ Creating...',
        'success': '✅ Ready!',
        'muscle': '💪 Muscle',
        'weight': '🔥 Loss',
        'balanced': '⚖️ Balanced',
        'diabetic': '🩺 Diabetic',
        'budget': '💰 Budget',
        'your_plan': '📋 Your Plan',
        'download_pdf': '📄 PDF',
        'save_plan': '💾 Save',
        'history': '📚 History',
        'pricing': '💳 Pricing',
        'per_month': '/month'
    },
    'fr': {
        'title': '🍽️ Nutrition Pour Tous',
        'subtitle': '✨ Plans de Repas IA Abordables ✨',
        'upgrade': '⭐ Passer à Premium',
        'free_plan': 'Plan GRATUIT',
        'basic_plan': 'Plan BASIC',
        'premium_plan': 'Plan PREMIUM',
        'plans_left': "Plans restants aujourd'hui",
        'select_lang': '🌍 Langue',
        'country': '🌍 Pays',
        'choose_goal': '🎯 Objectif',
        'generate': '🚀 GÉNÉRER',
        'generating': '⏳ Création...',
        'success': '✅ Prêt!',
        'muscle': '💪 Muscle',
        'weight': '🔥 Perte',
        'balanced': '⚖️ Équilibré',
        'diabetic': '🩺 Diabète',
        'budget': '💰 Budget',
        'your_plan': '📋 Votre Plan',
        'download_pdf': '📄 PDF',
        'save_plan': '💾 Sauver',
        'history': '📚 Historique',
        'pricing': '💳 Tarifs',
        'per_month': '/mois'
    }
}

COUNTRIES = {
    'en': ['USA', 'UK', 'Canada', 'Australia', 'Nigeria', 'Kenya', 'South Africa', 'India'],
    'fr': ['France', 'Belgique', 'Maroc', 'Algérie', 'Tunisie', 'Sénégal'],
    'es': ['España', 'México', 'Argentina', 'Colombia', 'Chile'],
    'ar': ['السعودية', 'الإمارات', 'مصر', 'المغرب'],
    'de': ['Deutschland', 'Österreich', 'Schweiz'],
    'ms': ['Malaysia', 'Indonesia'],
    'zh': ['中国', '台湾'],
    'ru': ['Россия', 'Украина']
}

TOPICS = {
    'muscle_gain': 'Create detailed 7-day HIGH PROTEIN meal plan using affordable local ingredients from {country}. Include: Daily meals, Local foods list, Complete nutrition (Protein/Carbs/Fats/Calories/Vitamins/Minerals), Daily cost in local currency, Preparation tips.',
    'weight_loss': 'Create detailed 7-day LOW-CALORIE weight loss plan using affordable local ingredients from {country}. Include: Daily meals, Local foods list, Nutrition breakdown, Daily cost, Portions.',
    'balanced': 'Create detailed 7-day BALANCED meal plan using affordable local ingredients from {country}. Include: Daily meals, Local foods list, Complete nutrition, Daily cost, Tips.',
    'diabetic': 'Create detailed 7-day DIABETIC-FRIENDLY low-GI meal plan using affordable local ingredients from {country}. Include: Daily meals, Local foods list, GI values, Nutrition, Cost.',
    'budget': 'Create detailed 7-day ULTRA-BUDGET nutritious meal plan using cheapest local ingredients from {country}. Include: Daily meals, Affordable local foods, Nutrition, Lowest cost possible.'
}

def t(key):
    return TEXTS.get(st.session_state.lang, TEXTS['en']).get(key, key)

def check_plan_limit():
    limit = PLAN_LIMITS[st.session_state.user_plan]['daily_plans']
    return st.session_state.plans_generated_today < limit

def save_plan_to_history(plan_data):
    if PLAN_LIMITS[st.session_state.user_plan]['history']:
        st.session_state.saved_plans.append({
            'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'country': st.session_state.country,
            'goal': st.session_state.goal,
            'content': plan_data
        })

# ========== SIDEBAR ==========
with st.sidebar:
    st.markdown(f"### {t('upgrade') if st.session_state.user_plan == 'free' else '✅ Premium Active'}")
    
    # Current plan badge
    if st.session_state.user_plan == 'premium':
        st.markdown("<div class='premium-badge'>⭐ PREMIUM USER</div>", unsafe_allow_html=True)
    elif st.session_state.user_plan == 'basic':
        st.info("📊 BASIC USER")
    else:
        st.warning("🆓 FREE USER")
    
    # Usage stats
    limit = PLAN_LIMITS[st.session_state.user_plan]['daily_plans']
    st.progress(st.session_state.plans_generated_today / limit)
    st.caption(f"{t('plans_left')}: {limit - st.session_state.plans_generated_today}")
    
    st.markdown("---")
    
    # Pricing button
    if st.button("💳 " + t('pricing'), use_container_width=True):
        st.session_state.show_pricing = True
    
    # History button (premium only)
    if PLAN_LIMITS[st.session_state.user_plan]['history']:
        if st.button("📚 " + t('history'), use_container_width=True):
            st.session_state.show_history = True
    
    st.markdown("---")
    st.caption("🌍 Available in 8+ languages")
    st.caption("💚 Affordable nutrition for all")

# ========== PRICING MODAL ==========
if 'show_pricing' in st.session_state and st.session_state.show_pricing:
    st.markdown("## 💳 Choose Your Plan")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class='pricing-card'>
            <h3>🆓 FREE</h3>
            <h2>$0<span style='font-size:1rem'>/month</span></h2>
            <div class='feature-list'>
                <div class='feature-item'>✓ 3 plans/day</div>
                <div class='feature-item'>✓ 3 languages</div>
                <div class='feature-item'>✓ 1 country</div>
                <div class='feature-item'>✗ No history</div>
                <div class='feature-item'>✗ No shopping list</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Current Plan" if st.session_state.user_plan == 'free' else "Downgrade", key="free_btn"):
            st.session_state.user_plan = 'free'
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class='pricing-card'>
            <h3>📊 BASIC</h3>
            <h2>$4.99<span style='font-size:1rem'>/month</span></h2>
            <div class='feature-list'>
                <div class='feature-item'>✓ 10 plans/day</div>
                <div class='feature-item'>✓ 5 languages</div>
                <div class='feature-item'>✓ 3 countries</div>
                <div class='feature-item'>✓ History saved</div>
                <div class='feature-item'>✗ No shopping list</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Upgrade to Basic" if st.session_state.user_plan != 'basic' else "Current Plan", key="basic_btn"):
            st.session_state.user_plan = 'basic'
            st.success("✅ Upgraded to Basic! (Demo)")
            st.rerun()
    
    with col3:
        st.markdown("""
        <div class='pricing-card' style='border: 3px solid #FFD700;'>
            <div class='premium-badge'>⭐ BEST VALUE</div>
            <h3>💎 PREMIUM</h3>
            <h2>$9.99<span style='font-size:1rem'>/month</span></h2>
            <div class='feature-list'>
                <div class='feature-item'>✓ UNLIMITED plans</div>
                <div class='feature-item'>✓ ALL 8 languages</div>
                <div class='feature-item'>✓ ALL countries</div>
                <div class='feature-item'>✓ Full history</div>
                <div class='feature-item'>✓ Shopping list</div>
                <div class='feature-item'>✓ Priority support</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("⭐ Upgrade to Premium" if st.session_state.user_plan != 'premium' else "Current Plan", key="premium_btn", type="primary"):
            st.session_state.user_plan = 'premium'
            st.balloons()
            st.success("🎉 Upgraded to Premium! (Demo)")
            st.rerun()
    
    if st.button("← Back", key="close_pricing"):
        st.session_state.show_pricing = False
        st.rerun()
    
    st.stop()

# ========== HISTORY MODAL ==========
if 'show_history' in st.session_state and st.session_state.show_history:
    st.markdown("## 📚 Your Saved Plans")
    
    if st.session_state.saved_plans:
        for i, plan in enumerate(reversed(st.session_state.saved_plans[-10:])):
            with st.expander(f"📅 {plan['date']} - {plan['country']} - {plan['goal']}"):
                st.markdown(plan['content'])
    else:
        st.info("No saved plans yet. Generate your first plan!")
    
    if st.button("← Back", key="close_history"):
        st.session_state.show_history = False
        st.rerun()
    
    st.stop()

# ========== MAIN APP ==========
st.markdown(f"# {t('title')}")
st.markdown(f"<p style='text-align:center; font-size:1.3rem; color:#2dce89; font-weight:600;'>{t('subtitle')}</p>", unsafe_allow_html=True)
st.markdown("---")

# Language & Country
col_lang, col_country = st.columns(2)

with col_lang:
    st.markdown(f"### {t('select_lang')}")
    available_langs = PLAN_LIMITS[st.session_state.user_plan]['languages']
    
    lc1 = st.columns(4)
    lc2 = st.columns(4)
    langs = [('en','🇬🇧'),('fr','🇫🇷'),('es','🇪🇸'),('ar','🇸🇦'),('de','🇩🇪'),('ms','🇲🇾'),('zh','🇨🇳'),('ru','🇷🇺')]
    
    for i, (code, flag) in enumerate(langs):
        col = lc1[i] if i < 4 else lc2[i-4]
        with col:
            disabled = code not in available_langs
            btn_type = "primary" if st.session_state.lang==code else "secondary"
            label = f"{flag} 🔒" if disabled else flag
            
            if st.button(label, key=f"l{code}", use_container_width=True, type=btn_type, disabled=disabled):
                st.session_state.lang = code
                st.session_state.country = COUNTRIES.get(code, ['USA'])[0]
                st.rerun()

with col_country:
    st.markdown(f"### {t('country')}")
    available_countries = COUNTRIES.get(st.session_state.lang, ['USA'])
    max_countries = PLAN_LIMITS[st.session_state.user_plan]['countries']
    
    st.session_state.country = st.selectbox(
        t('country'),
        options=available_countries[:max_countries],
        index=0,
        label_visibility="collapsed"
    )

st.markdown("---")

# Goals
st.markdown(f"### {t('choose_goal')}")
gc = st.columns(5)
goals = [('muscle_gain','muscle'),('weight_loss','weight'),('balanced','balanced'),('diabetic','diabetic'),('budget','budget')]

for i, (gcode, gkey) in enumerate(goals):
    with gc[i]:
        if st.button(t(gkey), key=f"g{gcode}", use_container_width=True, type="primary" if st.session_state.goal==gcode else "secondary"):
            st.session_state.goal = gcode
            st.rerun()

st.markdown("---")

# Generate button
c1, c2, c3 = st.columns([1,2,1])
with c2:
    can_generate = check_plan_limit()
    
    if not can_generate:
        st.error(f"⚠️ Daily limit reached! Upgrade to generate more plans.")
        st.button("⭐ Upgrade Now", key="upgrade_btn", use_container_width=True, type="primary", on_click=lambda: setattr(st.session_state, 'show_pricing', True))
    else:
        if st.button(t('generate'), key="gen", use_container_width=True, type="primary", disabled=not st.session_state.goal):
            if st.session_state.goal:
                topic_template = TOPICS.get(st.session_state.goal, '')
                my_topic = topic_template.replace('{country}', st.session_state.country)
                
                with st.spinner(t('generating')):
                    try:
                        crew = HealthyFoodNutritionManagementSystemCrew()
                        res = crew.crew().kickoff(inputs={'topic': my_topic, 'language': st.session_state.lang})
                        st.session_state.result = res
                        st.session_state.plans_generated_today += 1
                        
                        # Extract text
                        if hasattr(res, 'raw'):
                            txt = res.raw
                        elif hasattr(res, 'tasks_output') and res.tasks_output:
                            txt = res.tasks_output[-1].raw
                        else:
                            txt = str(res)
                        
                        save_plan_to_history(txt)
                        st.success(t('success'))
                        st.balloons()
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {e}")

st.markdown("---")

# Display results
if 'result' in st.session_state and st.session_state.result:
    st.markdown(f"## {t('your_plan')}")
    
    # Extract text
    if hasattr(st.session_state.result, 'raw'):
        txt = st.session_state.result.raw
    elif hasattr(st.session_state.result, 'tasks_output') and st.session_state.result.tasks_output:
        txt = st.session_state.result.tasks_output[-1].raw
    else:
        txt = str(st.session_state.result)
    
    st.markdown(txt)
    
    st.markdown("---")
    
    # Actions
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button(f"📄 {t('download_pdf')}", use_container_width=True):
            try:
                pdf = MealPlanPDFGenerator()
                buf = io.BytesIO()
                pdf.generate_pdf(txt, buf)
                buf.seek(0)
                st.download_button(
                    t('download_pdf'),
                    buf,
                    f"plan_{st.session_state.country}.pdf",
                    "application/pdf",
                    key="dlf",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"PDF: {e}")
    
    with col2:
        if PLAN_LIMITS[st.session_state.user_plan]['history']:
            st.success("💾 Auto-saved to history!")
        else:
            st.info("💾 Upgrade for history")
    
    with col3:
        if PLAN_LIMITS[st.session_state.user_plan]['shopping_list']:
            if st.button("🛒 Shopping List", use_container_width=True):
                st.info("🛒 Shopping list feature coming soon!")
        else:
            st.button("🛒 🔒 Premium", use_container_width=True, disabled=True)

else:
    st.info("👈 Select your country, goal, and click Generate!")

# Footer
st.markdown("---")
st.markdown("""
<p style='text-align:center; color:#2dce89; font-weight:600;'>
💚 Nutrition For All • Powered by AI • Available Worldwide 💚<br>
<small>Free plan: 3 plans/day | Basic $4.99/mo | Premium $9.99/mo</small>
</p>
""", unsafe_allow_html=True)
