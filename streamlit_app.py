import json
import os
from datetime import datetime
from typing import List, Dict, Any

import streamlit as st
import re
import hashlib
import secrets


# ---------- Custom CSS ----------
def inject_custom_css() -> None:
    st.markdown("""
        <style>
        /* Main styling */
        .main > div {
            padding-top: 2rem;
        }
        
        /* Recipe cards */
        .recipe-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: transform 0.2s;
        }
        
        .recipe-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        }
        
        /* Category badges */
        .category-badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            margin-right: 0.5rem;
        }
        
        .category-breakfast {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
        }
        
        .category-fast_food {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
        }
        
        .category-healthy {
            background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
            color: white;
        }
        
        .category-vegetarian {
            background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
            color: white;
        }
        
        /* Stats cards */
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            padding: 1.5rem;
            text-align: center;
            color: white;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        /* Sidebar styling */
        .sidebar .sidebar-content {
            background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
        }
        
        /* Button improvements */
        .stButton > button {
            border-radius: 10px;
            border: none;
            transition: all 0.3s;
        }
        
        .stButton > button:hover {
            transform: scale(1.05);
        }
        
        /* Title styling */
        h1 {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: 700;
        }
        
        /* Metric improvements */
        [data-testid="stMetricValue"] {
            font-size: 2rem;
        }
        
        /* Form improvements - High contrast for readability */
        /* Override any gradient backgrounds on input fields */
        .stTextInput > div > div,
        .stTextArea > div > div,
        .stSelectbox > div > div {
            background: none !important;
            background-color: transparent !important;
        }
        
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stSelectbox > div > div > select {
            background-color: #ffffff !important;
            background-image: none !important;
            color: #1f2937 !important;
            border: 2px solid #e5e7eb !important;
            border-radius: 10px;
            padding: 0.5rem !important;
        }
        
        .stTextInput > div > div > input::placeholder,
        .stTextArea > div > div > textarea::placeholder {
            color: #6b7280 !important;
            opacity: 0.8 !important;
        }
        
        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus,
        .stSelectbox > div > div > select:focus {
            background-color: #ffffff !important;
            background-image: none !important;
            border-color: #667eea !important;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
            outline: none !important;
        }
        
        /* Ensure labels are readable */
        .stTextInput label,
        .stTextArea label,
        .stSelectbox label,
        .stSlider label {
            color: #1f2937 !important;
            font-weight: 600 !important;
            background: none !important;
        }
        
        /* Radio buttons and checkboxes */
        .stRadio label,
        .stCheckbox label {
            color: #1f2937 !important;
        }
        
        /* Ensure all form containers have proper background */
        .element-container .stTextInput,
        .element-container .stTextArea,
        .element-container .stSelectbox {
            background-color: transparent !important;
        }
        
        /* Info boxes */
        .stInfo {
            border-left: 4px solid #667eea;
            border-radius: 5px;
        }
        
        /* Expander styling */
        .streamlit-expanderHeader {
            background: linear-gradient(90deg, #f0f2f6 0%, #ffffff 100%);
            border-radius: 10px;
        }
        
        /* Ingredient list styling */
        .ingredient-tag {
            display: inline-block;
            background: #e0e0e0;
            padding: 0.3rem 0.8rem;
            border-radius: 20px;
            margin: 0.2rem;
            font-size: 0.9rem;
        }
        </style>
    """, unsafe_allow_html=True)


# ---------- File utilities ----------
def load_json(file_path: str, default: Any) -> Any:
    if not os.path.exists(file_path):
        return default
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def save_json(file_path: str, data: Any) -> None:
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# ---------- Auth & per-user helpers ----------
USERS_FILE = "users.json"

def load_users() -> Dict[str, Any]:
    data = load_json(USERS_FILE, {})
    return data if isinstance(data, dict) else {}

def save_users(data: Dict[str, Any]) -> None:
    save_json(USERS_FILE, data)

def hash_password(pw: str, salt: str) -> str:
    return hashlib.sha256((pw + salt).encode("utf-8")).hexdigest()

def validate_email(email: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email))

def email_to_safe_id(email: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", email.strip().lower())

def user_file_paths(email: str) -> Dict[str, str]:
    safe = email_to_safe_id(email)
    return {
        "favorites": f"favorites_{safe}.json",
        "user_recipes": f"user_recipes_{safe}.json",
    }

def auth_gate() -> bool:
    # If already signed in, allow app to proceed
    if st.session_state.get("user"):
        return True

    st.set_page_config(page_title="Recipe App", page_icon="🍳", layout="wide")
    inject_custom_css()

    st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    border-radius: 15px; padding: 2rem; margin: 2rem 0; color: white;">
            <h1 style="margin: 0; font-size: 2.5rem;">🔐 Welcome to Recipe App</h1>
            <p style="margin-top: 0.5rem;">Log in or create an account to continue</p>
        </div>
    """, unsafe_allow_html=True)

    tabs = st.tabs(["Login", "Create account"])

    # Login tab
    with tabs[0]:
        with st.form("login_form", clear_on_submit=False):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted_login = st.form_submit_button("Login", type="primary", use_container_width=True)

        if submitted_login:
            users = load_users()
            u = users.get(email.strip().lower())
            if not u:
                st.error("Account not found.")
            else:
                salt = u.get("salt", "")
                if hash_password(password, salt) == u.get("password_hash"):
                    st.session_state.user = {"name": u.get("name"), "email": u.get("email")}
                    st.session_state.paths = user_file_paths(u["email"])
                    if "user_recipes" not in st.session_state:
                        st.session_state.user_recipes = load_json(st.session_state.paths["user_recipes"], [])
                    if "favorites" not in st.session_state:
                        st.session_state.favorites = load_json(st.session_state.paths["favorites"], [])
                    st.rerun()
                else:
                    st.error("Invalid password.")

    # Create account tab
    with tabs[1]:
        with st.form("register_form", clear_on_submit=False):
            name = st.text_input("Name")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password", help="Minimum 6 characters recommended")
            submitted_register = st.form_submit_button("Create account", type="primary", use_container_width=True)

        if submitted_register:
            if not name.strip():
                st.error("Please provide your name.")
            elif not validate_email(email):
                st.error("Please provide a valid email address.")
            elif len(password) < 6:
                st.error("Password must be at least 6 characters.")
            else:
                users = load_users()
                key = email.strip().lower()
                if key in users:
                    st.error("An account with this email already exists.")
                else:
                    salt = secrets.token_hex(16)
                    users[key] = {
                        "name": name.strip(),
                        "email": key,
                        "password_hash": hash_password(password, salt),
                        "salt": salt,
                        "created_at": datetime.now().isoformat(timespec="seconds"),
                    }
                    save_users(users)
                    # Auto-login after successful registration
                    st.session_state.user = {"name": name.strip(), "email": key}
                    st.session_state.paths = user_file_paths(key)
                    st.session_state.user_recipes = load_json(st.session_state.paths["user_recipes"], [])
                    st.session_state.favorites = load_json(st.session_state.paths["favorites"], [])
                    st.success("Account created! Logging you in...")
                    st.rerun()

    # Block the rest of the app until user logs in
    return False

def logout() -> None:
    # Clear user-specific session data and return to login
    for k in [
        "user", "paths", "favorites", "user_recipes",
        "rand_recipe", "rand_recipe_cat", "rand_recipes_multi"
    ]:
        if k in st.session_state:
            st.session_state.pop(k)
    st.rerun()

# ---------- Initialization ----------
def initialize_state() -> None:
    if "recipes" not in st.session_state:
        st.session_state.recipes = load_json("recipes.json", [])
    if "user_recipes" not in st.session_state:
        st.session_state.user_recipes = load_json("user_recipes.json", [])
    if "favorites" not in st.session_state:
        st.session_state.favorites = load_json("favorites.json", [])


def initialize_state_for_user() -> None:
    if "recipes" not in st.session_state:
        st.session_state.recipes = load_json("recipes.json", [])
    # For logged-in users, ensure per-user files are loaded
    if "user" in st.session_state and "paths" in st.session_state:
        if "user_recipes" not in st.session_state:
            st.session_state.user_recipes = load_json(st.session_state.paths["user_recipes"], [])
        if "favorites" not in st.session_state:
            st.session_state.favorites = load_json(st.session_state.paths["favorites"], [])

def get_all_recipes() -> List[Dict[str, Any]]:
    return list(st.session_state.recipes) + list(st.session_state.user_recipes)


def is_same_recipe(a: Dict[str, Any], b: Dict[str, Any]) -> bool:
    return a.get("id") == b.get("id") and a.get("name") == b.get("name")


def in_favorites(recipe: Dict[str, Any]) -> bool:
    return any(is_same_recipe(recipe, r) for r in st.session_state.favorites)


def add_to_favorites(recipe: Dict[str, Any]) -> None:
    if not in_favorites(recipe):
        st.session_state.favorites.append(recipe)
        path = st.session_state.paths["favorites"] if "paths" in st.session_state else "favorites.json"
        save_json(path, st.session_state.favorites)


def remove_from_favorites(recipe: Dict[str, Any]) -> None:
    st.session_state.favorites = [r for r in st.session_state.favorites if not is_same_recipe(r, recipe)]
    path = st.session_state.paths["favorites"] if "paths" in st.session_state else "favorites.json"
    save_json(path, st.session_state.favorites)


# ---------- UI helpers ----------
def get_category_emoji(category: str) -> str:
    """Get emoji for category"""
    emoji_map = {
        "breakfast": "🍳",
        "fast_food": "🍔",
        "healthy": "🥗",
        "vegetarian": "🥬"
    }
    return emoji_map.get(category.lower(), "🍽️")


def recipe_card(recipe: Dict[str, Any]) -> None:
    category = recipe.get('category', '-')
    category_title = category.title().replace('_', ' ')
    emoji = get_category_emoji(category)
    
    with st.container(border=True):
        # Header with gradient background
        header_cols = st.columns([4, 1])
        with header_cols[0]:
            header_html = f"""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        border-radius: 15px;
                        padding: 1.5rem;
                        margin-bottom: 1rem;
                        color: white;">
                <h2 style="margin: 0; color: white; font-size: 1.8rem;">{emoji} {recipe.get('name', 'Recipe')}</h2>
                <div style="margin-top: 0.75rem;">
                    <span style="background: rgba(255,255,255,0.3); padding: 0.4rem 1rem; border-radius: 20px; font-size: 0.85rem; margin-right: 0.5rem;">
                        {category_title}
                    </span>
                    <span style="background: rgba(255,255,255,0.3); padding: 0.4rem 1rem; border-radius: 20px; font-size: 0.85rem;">
                        ⏱️ {recipe.get('cook_time', '-')}
                    </span>
                </div>
            </div>
            """
            st.markdown(header_html, unsafe_allow_html=True)
        
        with header_cols[1]:
            st.write("")  # Spacer
            if in_favorites(recipe):
                if st.button("❤️ Remove", key=f"fav_remove_{recipe['id']}", use_container_width=True, type="primary"):
                    remove_from_favorites(recipe)
                    st.toast("Removed from favorites", icon="❌")
                    st.rerun()
            else:
                if st.button("🤍 Add", key=f"fav_add_{recipe['id']}", use_container_width=True):
                    add_to_favorites(recipe)
                    st.toast("Added to favorites", icon="❤️")
                    st.rerun()
        
        # Ingredients section
        ingredients = recipe.get("ingredients", [])
        if ingredients:
            st.markdown("### 🥘 Ingredients")
            # Create ingredient tags
            ingredient_html = '<div style="display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 1rem;">'
            for ing in ingredients:
                ingredient_html += f'<span style="background: #e0e7ff; color: #4338ca; padding: 0.4rem 1rem; border-radius: 20px; font-weight: 500;">{ing.title()}</span>'
            ingredient_html += '</div>'
            st.markdown(ingredient_html, unsafe_allow_html=True)
        else:
            st.markdown("### 🥘 Ingredients")
            st.write("-")

        # Instructions section
        st.markdown("### 📝 Instructions")
        instructions = recipe.get("instructions", "-")
        st.markdown(f'<div style="background: #f8fafc; padding: 1.25rem; border-radius: 10px; border-left: 4px solid #667eea; margin-top: 0.5rem;">{instructions}</div>', unsafe_allow_html=True)


# ---------- Pages ----------
def page_home() -> None:
    all_recipes = get_all_recipes()
    
    # Header with simple design (matching sidebar total recipes box)
    st.markdown("""
        <div style="background: #f8fafc;
                    border-radius: 10px;
                    padding: 1rem;
                    margin-bottom: 0.5rem;
                    text-align: center;">
            <h1 style="margin: 0; font-size: 2.5rem; color: #111827;"> Recipe App</h1>
            <p style="font-size: 1rem; margin-top: 0.5rem; color: #374151;">
                All Recipes, search, and save your favorite recipes
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Stats with better styling
    stats = st.columns(3)
    with stats[0]:
        st.markdown(f"""
            <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                        border-radius: 15px;
                        padding: 1.5rem;
                        text-align: center;
                        color: white;">
                <div style="font-size: 2.5rem; font-weight: bold;">{len(all_recipes)}</div>
                <div style="font-size: 1rem; margin-top: 0.5rem;">📚 Total Recipes</div>
            </div>
        """, unsafe_allow_html=True)
    
    with stats[1]:
        st.markdown(f"""
            <div style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
                        border-radius: 15px;
                        padding: 1.5rem;
                        text-align: center;
                        color: white;">
                <div style="font-size: 2.5rem; font-weight: bold;">{len(st.session_state.favorites)}</div>
                <div style="font-size: 1rem; margin-top: 0.5rem;">❤️ Favorites</div>
            </div>
        """, unsafe_allow_html=True)
    
    with stats[2]:
        st.markdown(f"""
            <div style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
                        border-radius: 15px;
                        padding: 1.5rem;
                        text-align: center;
                        color: white;">
                <div style="font-size: 2.5rem; font-weight: bold;">{len(st.session_state.user_recipes)}</div>
                <div style="font-size: 1rem; margin-top: 0.5rem;">📝 My Recipes</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Random recipe section
    st.markdown("""
        <div style="background: #f8fafc;
                    border-radius: 15px;
                    padding: 1.5rem;
                    margin-bottom: 1rem;
                    border-left: 5px solid #667eea;">
            <h2 style="margin: 0; color: #667eea;">🎲 Today's Random Recipe</h2>
        </div>
    """, unsafe_allow_html=True)
    
    if all_recipes:
        import random
        recipe = random.choice(all_recipes)
        recipe_card(recipe)
    else:
        st.info("⚠️ No recipes available. Generate the database from database_app.ipynb.")


def page_random() -> None:
    import random

    st.markdown("""
        <div style="background: white;
                    border-radius: 15px;
                    padding: 1.5rem;
                    margin-bottom: 2rem;
                    color: white;">
            <h1 style="color: white; margin: 0; font-size: 2.5rem;"> Random Recipe Generator</h1>
        </div>
    """, unsafe_allow_html=True)
    
    all_recipes = get_all_recipes()
    if not all_recipes:
        st.warning("⚠️ No recipes available.")
        return

    st.markdown("### Select Mode")
    mode = st.radio("Mode", ["Single", "By Category", "Multiple"], horizontal=True, label_visibility="collapsed")

    if mode == "Single":
        if st.button("🎲 Get Random Recipe", type="primary", use_container_width=True):
            st.session_state.rand_recipe = random.choice(all_recipes)
        if st.session_state.get("rand_recipe"):
            st.markdown("### Your Random Recipe")
            recipe_card(st.session_state.rand_recipe)

    elif mode == "By Category":
        categories = sorted({r.get("category", "-") for r in all_recipes})
        category = st.selectbox("📂 Select Category", categories)
        if st.button("🎲 Get Random in Category", type="primary", use_container_width=True):
            pool = [r for r in all_recipes if r.get("category") == category]
            if pool:
                st.session_state.rand_recipe_cat = random.choice(pool)
            else:
                st.session_state.rand_recipe_cat = None
        recipe = st.session_state.get("rand_recipe_cat")
        if recipe:
            st.markdown(f"### Random {category.title()} Recipe")
            recipe_card(recipe)
        elif "rand_recipe_cat" in st.session_state and st.session_state.rand_recipe_cat is None:
            st.info("ℹ️ No recipes found for that category.")

    else:
        n = st.slider("📊 How many recipes?", 1, 10, 3)
        if st.button("🎲 Get Multiple Recipes", type="primary", use_container_width=True):
            if len(all_recipes) >= n:
                st.session_state.rand_recipes_multi = random.sample(all_recipes, n)
            else:
                st.session_state.rand_recipes_multi = list(all_recipes)
        recipes_list = st.session_state.get("rand_recipes_multi", [])
        if recipes_list:
            st.markdown(f"### 🎉 Your {len(recipes_list)} Random Recipes")
            for idx, r in enumerate(recipes_list, start=1):
                st.markdown("---")
                st.markdown(f"#### {idx}. {get_category_emoji(r.get('category', '-'))} {r.get('name','-')}")
                st.markdown(f"**Category:** {r.get('category','-').title().replace('_', ' ')} • **Time:** {r.get('cook_time','-')}")
                with st.expander("View Full Recipe"):
                    recipe_card(r)


def page_All_Recipes() -> None:
    st.markdown("""
        <div style="background: white;
                    border-radius: 15px;
                    padding: 1.5rem;
                    margin-bottom: 2rem;
                    color: white;">
            <h1 style="color: white; margin: 0; font-size: 2.5rem;"> All Recipes by Category</h1>
        </div>
    """, unsafe_allow_html=True)
    
    all_recipes = get_all_recipes()
    if not all_recipes:
        st.info("ℹ️ No recipes available.")
        return

    categories = sorted({r.get("category", "-") for r in all_recipes})
    selected = st.radio(
        "Select Category",
        categories,
        format_func=lambda x: f"{get_category_emoji(x)} {x.title().replace('_', ' ')}",
        horizontal=True
    )

    filtered = [r for r in all_recipes if r.get("category") == selected]
    st.markdown(f"""
        <div style="background: #f8fafc;
                    border-radius: 10px;
                    padding: 1rem;
                    margin-bottom: 1rem;
                    border-left: 4px solid #667eea;">
            <strong>📊 {len(filtered)} recipes in {selected.title().replace('_', ' ')}</strong>
        </div>
    """, unsafe_allow_html=True)
    
    for r in filtered:
        recipe_card(r)


def page_search() -> None:
    st.markdown("""
        <div style="background: white;
                    border-radius: 15px;
                    padding: 1.5rem;
                    margin-bottom: 2rem;
                    color: white;">
            <h1 style="color: white; margin: 0; font-size: 2.5rem;"> Search by Ingredients</h1>
        </div>
    """, unsafe_allow_html=True)
    
    all_recipes = get_all_recipes()
    if not all_recipes:
        st.info("ℹ️ No recipes available.")
        return

    st.markdown("### Select Search Mode")
    mode = st.radio("Search Mode", ["Single Ingredient", "Multiple Ingredients", "Advanced"], horizontal=True, label_visibility="collapsed")

    if mode == "Single Ingredient":
        term = st.text_input("🔍 Search for ingredient", placeholder="e.g., chicken, eggs, flour")
        if term:
            term_l = term.strip().lower()
            results = [r for r in all_recipes if any(term_l in ing.lower() for ing in r.get("ingredients", []))]
            if results:
                st.markdown(f"""
                    <div style="background: #e0e7ff;
                                border-radius: 10px;
                                padding: 1rem;
                                margin: 1rem 0;
                                border-left: 4px solid #4338ca;">
                        <strong>✅ Found {len(results)} result(s)</strong>
                    </div>
                """, unsafe_allow_html=True)
                for r in results:
                    recipe_card(r)
            else:
                st.info("🔍 No recipes found with that ingredient.")

    elif mode == "Multiple Ingredients":
        terms_s = st.text_input("🔍 Ingredients (comma separated)", placeholder="e.g., chicken, cheese, bread")
        if terms_s:
            terms = [t.strip().lower() for t in terms_s.split(",") if t.strip()]
            ranked: List[Any] = []
            for r in all_recipes:
                recipe_ings = [i.lower() for i in r.get("ingredients", [])]
                matches = sum(1 for t in terms if any(t in i for i in recipe_ings))
                if matches > 0:
                    ranked.append((r, matches))
            ranked.sort(key=lambda x: x[1], reverse=True)
            if ranked:
                st.markdown(f"""
                    <div style="background: #e0e7ff;
                                border-radius: 10px;
                                padding: 1rem;
                                margin: 1rem 0;
                                border-left: 4px solid #4338ca;">
                        <strong>✅ Found {len(ranked)} result(s)</strong>
                    </div>
                """, unsafe_allow_html=True)
                for r, m in ranked:
                    st.markdown(f"""
                        <div style="background: #f8fafc;
                                    border-radius: 10px;
                                    padding: 0.75rem;
                                    margin-bottom: 0.5rem;
                                    border-left: 4px solid #10b981;">
                            <strong>{get_category_emoji(r.get('category', '-'))} {r.get('name','-')}</strong> — 
                            <span style="color: #10b981; font-weight: bold;">{m} ingredient match(es)</span>
                        </div>
                    """, unsafe_allow_html=True)
                    recipe_card(r)
            else:
                st.info("🔍 No recipes found with those ingredients.")

    else:
        must = st.text_input("🎯 Must have (comma separated)", placeholder="Required ingredients")
        can = st.text_input("⭐ Can have (comma separated)", placeholder="Optional ingredients")
        if must or can:
            must_list = [t.strip().lower() for t in must.split(",") if t.strip()]
            can_list = [t.strip().lower() for t in can.split(",") if t.strip()]
            ranked: List[Any] = []
            for r in all_recipes:
                ings = [i.lower() for i in r.get("ingredients", [])]
                must_ok = all(any(m in i for i in ings) for m in must_list) if must_list else True
                can_matches = sum(1 for c in can_list if any(c in i for i in ings)) if can_list else 0
                if must_ok and (not can_list or can_matches > 0):
                    ranked.append((r, can_matches))
            ranked.sort(key=lambda x: x[1], reverse=True)
            if ranked:
                st.markdown(f"""
                    <div style="background: #e0e7ff;
                                border-radius: 10px;
                                padding: 1rem;
                                margin: 1rem 0;
                                border-left: 4px solid #4338ca;">
                        <strong>✅ Found {len(ranked)} result(s)</strong>
                    </div>
                """, unsafe_allow_html=True)
                for r, m in ranked:
                    st.markdown(f"""
                        <div style="background: #f8fafc;
                                    border-radius: 10px;
                                    padding: 0.75rem;
                                    margin-bottom: 0.5rem;
                                    border-left: 4px solid #f59e0b;">
                            <strong>{get_category_emoji(r.get('category', '-'))} {r.get('name','-')}</strong> — 
                            <span style="color: #f59e0b; font-weight: bold;">{m} bonus ingredient(s)</span>
                        </div>
                    """, unsafe_allow_html=True)
                    recipe_card(r)
            else:
                st.info("🔍 No recipes found matching your criteria.")


def page_favorites() -> None:
    st.markdown("""
        <div style="background: white;
                    border-radius: 15px;
                    padding: 1.5rem;
                    margin-bottom: 2rem;
                    color: white;">
            <h1 style="color: white; margin: 0; font-size: 2.5rem;">❤️ My Favorites</h1>
        </div>
    """, unsafe_allow_html=True)
    
    favs = st.session_state.favorites
    if not favs:
        st.info("💔 No favorites yet. Add some recipes to your favorites!")
        return
    
    st.markdown(f"""
        <div style="background: #fef3c7;
                    border-radius: 10px;
                    padding: 1rem;
                    margin-bottom: 1rem;
                    border-left: 4px solid #f59e0b;">
            <strong>📋 You have {len(favs)} favorite recipe(s)</strong>
        </div>
    """, unsafe_allow_html=True)
    
    for r in list(favs):
        recipe_card(r)


def page_add_recipe() -> None:
    st.markdown("""
        <div style="background: white;
                    border-radius: 15px;
                    padding: 1.5rem;
                    margin-bottom: 2rem;
                    color: white;">
            <h1 style="color: white; margin: 0; font-size: 2.5rem;">➕ Add New Recipe</h1>
        </div>
    """, unsafe_allow_html=True)

    with st.form("add_recipe_form", clear_on_submit=True, border=False):
        st.markdown("### 📝 Recipe Details")
        name = st.text_input("Recipe Name", placeholder="e.g., Chocolate Chip Cookies")
        category = st.selectbox(
            "Category",
            ["breakfast", "fast_food", "healthy", "vegetarian"],
            format_func=lambda x: f"{get_category_emoji(x)} {x.title().replace('_', ' ')}"
        )
        cook_time = st.text_input("⏱️ Cook Time", placeholder="e.g., 15 minutes")
        
        st.markdown("### 🥘 Ingredients")
        ingredients_text = st.text_area("Enter ingredients (one per line)", placeholder="e.g.,\nflour\neggs\nbutter", height=150)
        
        st.markdown("### 📝 Instructions")
        instructions = st.text_area("Enter cooking instructions", placeholder="Describe the cooking process...", height=150)
        
        submitted = st.form_submit_button("✅ Add Recipe", type="primary", use_container_width=True)

    if submitted:
        if not name or not ingredients_text or not instructions:
            st.error("Please fill in name, ingredients, and instructions.")
            return

        all_recipes = get_all_recipes()
        if any(r.get("name", "").strip().lower() == name.strip().lower() for r in all_recipes):
            st.error(f"Recipe '{name}' already exists.")
            return

        new_id = max([r.get("id", 0) for r in all_recipes], default=0) + 1
        new_recipe = {
            "id": new_id,
            "category": category,
            "name": name.strip(),
            "ingredients": [i.strip() for i in ingredients_text.splitlines() if i.strip()],
            "cook_time": cook_time.strip() or "Unknown",
            "instructions": instructions.strip(),
            "created_by": "user",
            "created_date": datetime.now().strftime("%Y-%m-%d"),
        }

        st.session_state.user_recipes.append(new_recipe)
        save_json(st.session_state.paths["user_recipes"], st.session_state.user_recipes)
        st.success(f"Recipe '{name}' added!")


def page_my_recipes() -> None:
    st.markdown("""
        <div style="background: white;
                    border-radius: 15px;
                    padding: 1.5rem;
                    margin-bottom: 2rem;
                    color: white;">
            <h1 style="color: white; margin: 0; font-size: 2.5rem;"> My Added Recipes</h1>
        </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.user_recipes:
        st.info("📝 You haven't added any recipes yet. Add some recipes first!")
        return

    st.markdown(f"""
        <div style="background: #dbeafe;
                    border-radius: 10px;
                    padding: 1rem;
                    margin-bottom: 1rem;
                    border-left: 4px solid #3b82f6;">
            <strong>📋 You have {len(st.session_state.user_recipes)} recipe(s)</strong>
        </div>
    """, unsafe_allow_html=True)

    for idx, recipe in enumerate(list(st.session_state.user_recipes)):
        with st.expander(f"{get_category_emoji(recipe.get('category', '-'))} {recipe.get('name','-')} ({recipe.get('category','-').title().replace('_', ' ')})"):
            recipe_card(recipe)

            st.markdown("---")
            st.markdown("### ✏️ Edit Recipe")
            with st.form(f"edit_{recipe['id']}"):
                new_name = st.text_input("📝 Name", value=recipe.get("name", ""))
                new_category = st.selectbox(
                    "📂 Category",
                    ["breakfast", "fast_food", "healthy", "vegetarian"],
                    index=["breakfast", "fast_food", "healthy", "vegetarian"].index(recipe.get("category", "healthy")),
                    format_func=lambda x: f"{get_category_emoji(x)} {x.title().replace('_', ' ')}"
                )
                new_time = st.text_input("⏱️ Cook Time", value=recipe.get("cook_time", ""))
                new_ingredients = st.text_area("🥘 Ingredients (one per line)", value="\n".join(recipe.get("ingredients", [])), height=100)
                new_instructions = st.text_area("📝 Instructions", value=recipe.get("instructions", ""), height=100)
                col_b = st.columns(2)
                save_btn = col_b[0].form_submit_button("💾 Save Changes", type="primary", use_container_width=True)
                del_btn = col_b[1].form_submit_button("🗑️ Delete Recipe", use_container_width=True)

            if save_btn:
                recipe["name"] = new_name.strip() or recipe["name"]
                recipe["category"] = new_category
                recipe["cook_time"] = new_time.strip() or recipe["cook_time"]
                ings = [i.strip() for i in new_ingredients.splitlines() if i.strip()]
                if ings:
                    recipe["ingredients"] = ings
                recipe["instructions"] = new_instructions.strip() or recipe["instructions"]
                save_json(st.session_state.paths["user_recipes"], st.session_state.user_recipes)
                st.success("✅ Recipe updated successfully!")

            if del_btn:
                st.session_state.user_recipes.pop(idx)
                save_json(st.session_state.paths["user_recipes"], st.session_state.user_recipes)
                st.toast("🗑️ Recipe deleted", icon="🗑️")
                st.rerun()


def page_about() -> None:
    st.markdown("""
        <div style="background: white;
                    border-radius: 15px;
                    padding: 1.5rem;
                    margin-bottom: 2rem;
                    color: white;">
            <h1 style="color: white; margin: 0; font-size: 2.5rem;"> About Us</h1>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div style="background: #f8fafc;
                    border-radius: 15px;
                    padding: 2rem;
                    border-left: 5px solid #667eea;">
            <h2>🍳 Our Story</h2>
            <p style="font-size: 1.1rem; line-height: 1.8;">
                It all started with a simple idea — to make cooking fun, easy, and accessible for everyone. 
                Our small team of food enthusiasts and developers wanted to bring together the joy of home-cooked 
                meals with the convenience of modern technology. From our humble beginnings experimenting in a 
                family kitchen to creating this digital recipe hub, our mission has always been the same: 
                to help people discover new flavors, share their creations, and fall in love with cooking again.
            </p>
        </div>
    """, unsafe_allow_html=True)


# ---------- App ----------
def main() -> None:
    # Show login/register first; stop rendering if not signed in
    if not auth_gate():
        return

    # Signed in; apply CSS and init per-user state
    inject_custom_css()
    initialize_state_for_user()

    with st.sidebar:
        st.markdown("""
            <div style="text-align: center; padding: 1rem 0;">
                <h1 style="color: #667eea; margin: 0;"> Recipe App</h1>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        if st.session_state.get("user"):
            st.markdown(f"**Signed in as:** {st.session_state.user.get('name','')} ({st.session_state.user.get('email','')})")
            if st.button("Log out", use_container_width=True):
                logout()
        
        st.markdown("### 🧭 Navigation")
        page = st.radio(
            "Navigate",
            ["Home", "Random", "All Recipes", "Search", "Favorites", "Add Recipe", "My Recipes", "About"],
            index=0,
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Quick stats in sidebar
        all_recipes = get_all_recipes()
        st.markdown("### 📊 Quick Stats")
        st.markdown(f"""
            <div style="background: #f8fafc;
                        border-radius: 10px;
                        padding: 1rem;
                        margin-bottom: 0.5rem;">
                <strong>📚 {len(all_recipes)}</strong> Total Recipes<br>
                <strong>❤️ {len(st.session_state.favorites)}</strong> Favorites<br>
                <strong>📝 {len(st.session_state.user_recipes)}</strong> My Recipes
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.caption("💡 Tip: Generate the DB via `database_app.ipynb` if recipes are empty.")

    if page == "Home":
        page_home()
    elif page == "Random":
        page_random()
    elif page == "All Recipes":
        page_All_Recipes()
    elif page == "Search":
        page_search()
    elif page == "Favorites":
        page_favorites()
    elif page == "Add Recipe":
        page_add_recipe()
    elif page == "My Recipes":
        page_my_recipes()
    else:
        page_about()


if __name__ == "__main__":
    main()





