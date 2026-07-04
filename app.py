import streamlit as st
import database
import auth
import employee
import admin

# ─────────────────────────────────────────────
# 1. Page Configuration
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Leave Management Agent | HRMS",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize database
database.init_db()

# ─────────────────────────────────────────────
# 2. Session State
# ─────────────────────────────────────────────
def init_session():
    defaults = {
        'page': 'home',        # home | dashboard
        'logged_in': False,
        'user': None,
        'role': None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()

# ─────────────────────────────────────────────
# 3. GLOBAL CSS — premium redesigned login
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [class*="css"], .stMarkdown, .stTextInput, .stButton,
.stCheckbox, .stForm, .stRadio, .stSelectbox, p, span, div, h1, h2, h3, h4, h5, h6 {
    font-family: 'Poppins', sans-serif !important;
}

/* ── Layout ── */
.block-container {
    padding: 0 !important; margin: 0 !important;
    max-width: 100% !important; background: transparent !important;
}
.stApp {
    min-height: 100vh !important; overflow-y: auto !important;
    background: linear-gradient(135deg, #0a1628 0%, #0f2458 28%, #1a3fb0 58%, #1d6ff5 80%, #0ea5e9 100%) !important;
}
html, body { min-height: 100vh !important; overflow-y: auto !important; }
section[data-testid="stMain"] {
    padding: 0 !important; background: transparent !important;
    min-height: 100vh !important; overflow-y: auto !important;
}

#MainMenu, footer, header, .stDeployButton { visibility: hidden !important; height: 0 !important; }
[data-testid="stToolbar"] { display: none !important; }

/* ── Animated background ── */
.bg-bubbles { position: fixed; inset: 0; pointer-events: none; z-index: 0; overflow: hidden; }
.bubble { position: absolute; border-radius: 50%; filter: blur(70px); opacity: 0.22; animation: floatUp 10s ease-in-out infinite; }
.bubble.b1 { width: 420px; height: 420px; background: #1e40af; top: -8%; left: -6%; animation-delay: 0s; }
.bubble.b2 { width: 520px; height: 520px; background: #3730a3; bottom: -18%; right: -8%; animation-delay: -4s; }
.bubble.b3 { width: 280px; height: 280px; background: #0369a1; top: 40%; left: 12%; animation-delay: -7s; }
.dot-grid {
    position: absolute; width: 220px; height: 220px;
    background-image: radial-gradient(rgba(255,255,255,0.16) 2px, transparent 2px);
    background-size: 26px 26px;
}
.dot-grid.tl { top: 6%; left: 2%; }
.dot-grid.br { bottom: 6%; right: 2%; }

@keyframes floatUp {
    0%, 100% { transform: translateY(0px) scale(1); }
    50% { transform: translateY(-24px) scale(1.04); }
}

/* ── Auth shell (center column wrapper) ── */
.auth-shell {
    position: relative; z-index: 1;
    width: 100%; max-width: 460px;
    margin: 0 auto; padding: 20px 16px 28px;
}

/* ── Glass card ── */
.auth-card {
    background: rgba(255, 255, 255, 0.10);
    backdrop-filter: blur(28px) saturate(1.4);
    -webkit-backdrop-filter: blur(28px) saturate(1.4);
    border: 1px solid rgba(255, 255, 255, 0.18);
    border-radius: 28px;
    padding: 34px 32px 28px;
    box-shadow: 0 28px 80px rgba(4, 8, 36, 0.40), 0 0 0 1px rgba(255,255,255,0.06) inset;
    color: #ffffff;
    margin-bottom: 16px;
}

/* ── Hero header ── */
.hero-wrap { text-align: center; padding-top: 28px; margin-bottom: 4px; }

.hero-icon-ring {
    width: 84px; height: 84px; border-radius: 50%;
    background: rgba(255, 255, 255, 0.12);
    border: 2px solid rgba(255, 255, 255, 0.28);
    display: flex; align-items: center; justify-content: center;
    margin: 0 auto 16px auto;
    box-shadow: 0 8px 32px rgba(37, 99, 235, 0.40);
    font-size: 40px;
    transition: transform 0.35s ease, box-shadow 0.35s ease;
}
.hero-icon-ring:hover {
    transform: scale(1.07);
    box-shadow: 0 12px 42px rgba(37, 99, 235, 0.55);
}

.hero-title {
    text-align: center; font-size: 1.72rem; font-weight: 800;
    letter-spacing: -0.02em; margin-bottom: 6px; color: #ffffff;
    text-shadow: 0 2px 12px rgba(0,0,0,0.22);
}
.hero-subtitle {
    text-align: center; font-size: 0.80rem;
    color: rgba(255,255,255,0.62); letter-spacing: 0.03em; margin-bottom: 0;
}

/* ── Section label ── */
.section-label {
    text-align: center; font-size: 0.70rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.14em;
    color: rgba(255,255,255,0.48); margin: 20px 0 10px 0;
}

/* ── Portal toggle — radio styled as pills ── */
div[data-testid="stRadio"] > label { display: none !important; }
div[data-testid="stRadio"] > div {
    display: flex !important;
    background: rgba(255,255,255,0.07) !important;
    border: 1px solid rgba(255,255,255,0.14) !important;
    border-radius: 100px !important;
    padding: 5px !important;
    gap: 4px !important;
    width: 100% !important;
}
div[data-testid="stRadio"] > div > label {
    flex: 1 !important; text-align: center !important;
    padding: 9px 18px !important; border-radius: 100px !important;
    color: rgba(255,255,255,0.60) !important;
    font-size: 13px !important; font-weight: 600 !important;
    cursor: pointer !important; transition: all 0.30s ease !important;
    user-select: none !important;
}
div[data-testid="stRadio"] > div > label:has(input:checked) {
    background: linear-gradient(135deg, #2563eb 0%, #1a4fd6 100%) !important;
    color: #ffffff !important;
    box-shadow: 0 4px 18px rgba(37,99,235,0.50) !important;
}
div[data-testid="stRadio"] > div > label > div:first-child { display: none !important; }
div[data-testid="stRadio"] > div > label > div { color: inherit !important; }

/* ── Form inputs ── */
.form-title {
    text-align: center; font-size: 1.05rem; font-weight: 700;
    color: #ffffff; margin-bottom: 18px; letter-spacing: -0.01em;
}

.stTextInput > div > div > input, .stTextArea textarea, .stDateInput input {
    background-color: #1e293b !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    border-radius: 14px !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    caret-color: #ffffff !important;
    font-family: 'Poppins', sans-serif !important;
    font-size: 14px !important;
    padding: 14px 16px !important;
    transition: border-color 0.25s, background 0.25s, box-shadow 0.25s !important;
}
.stTextInput > div > div > input:focus, .stTextArea textarea:focus, .stDateInput input:focus {
    border-color: rgba(147,197,253,0.85) !important;
    background-color: #27374d !important;
    box-shadow: 0 0 0 3px rgba(147,197,253,0.18) !important;
    outline: none !important;
}
.stTextInput > div > div > input::placeholder, .stTextArea textarea::placeholder, .stDateInput input::placeholder { color: rgba(255,255,255,0.35) !important; }
.stTextInput > div > div > input:disabled, .stTextArea textarea:disabled, .stDateInput input:disabled {
    opacity: 0.55 !important; cursor: not-allowed !important;
}
.stTextInput label, .stTextInput > label,
.stTextInput > div > label, .stTextInput > div > div > label {
    color: rgba(255,255,255,0.72) !important;
    font-size: 11px !important; font-weight: 700 !important;
    letter-spacing: 0.08em !important; text-transform: uppercase !important;
}

/* Autofill fix */
.stTextInput input:-webkit-autofill,
.stTextInput input:-webkit-autofill:focus,
.stTextInput input:-webkit-autofill:hover {
    -webkit-box-shadow: 0 0 0 1000px rgba(15, 36, 88, 0.90) inset !important;
    -webkit-text-fill-color: #ffffff !important;
    caret-color: #ffffff !important;
}

/* ── Checkbox ── */
.stCheckbox > label { color: rgba(255,255,255,0.78) !important; font-size: 13px !important; }
.stCheckbox > label > span { color: rgba(255,255,255,0.78) !important; }

/* ── Column align for eye button row ── */
div[data-testid="stHorizontalBlock"] { align-items: flex-end !important; gap: 8px !important; }

/* ── Eye / show-hide button ── */
.eye-btn .stButton > button {
    background: rgba(255,255,255,0.09) !important;
    border: 1px solid rgba(255,255,255,0.16) !important;
    border-radius: 14px !important; color: rgba(255,255,255,0.75) !important;
    font-size: 19px !important; height: 50px !important; width: 50px !important;
    padding: 0 !important; line-height: 1 !important;
    display: flex !important; align-items: center !important; justify-content: center !important;
    transition: all 0.22s ease !important; cursor: pointer !important;
    min-height: 50px !important;
}
.eye-btn .stButton > button:hover {
    background: rgba(255,255,255,0.16) !important;
    border-color: rgba(255,255,255,0.28) !important;
}

/* ── Sign in button ── */
.sign-in-btn > div > .stButton > button,
.sign-in-btn .stButton > button {
    width: 100% !important;
    background: linear-gradient(135deg, #2563eb 0%, #1a4fd6 100%) !important;
    color: #ffffff !important; border: none !important;
    border-radius: 14px !important;
    font-family: 'Poppins', sans-serif !important;
    font-size: 15px !important; font-weight: 700 !important;
    padding: 14px 24px !important; height: 52px !important;
    letter-spacing: 0.04em !important;
    box-shadow: 0 10px 32px rgba(37,99,235,0.45) !important;
    transition: all 0.28s ease !important; cursor: pointer !important;
    margin-top: 6px !important;
}
.sign-in-btn > div > .stButton > button:hover,
.sign-in-btn .stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 18px 44px rgba(37,99,235,0.55) !important;
}

/* ── Register button ── */
.register-btn .stButton > button {
    width: 100% !important;
    background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
    color: #ffffff !important; border: none !important;
    border-radius: 14px !important;
    font-family: 'Poppins', sans-serif !important;
    font-size: 15px !important; font-weight: 700 !important;
    padding: 14px 24px !important; height: 52px !important;
    box-shadow: 0 10px 32px rgba(5,150,105,0.38) !important;
    transition: all 0.28s ease !important; cursor: pointer !important;
    margin-top: 6px !important;
}
.register-btn .stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 18px 44px rgba(5,150,105,0.50) !important;
}

/* ── Link-style button ── */
.link-btn .stButton > button {
    background: transparent !important; border: none !important;
    color: #60a5fa !important; font-size: 13px !important;
    font-weight: 700 !important; padding: 2px 0 !important;
    text-decoration: underline !important; cursor: pointer !important;
    box-shadow: none !important; height: auto !important;
    min-height: unset !important; width: auto !important;
    letter-spacing: 0.01em !important;
    transition: color 0.2s ease !important;
}
.link-btn .stButton > button:hover { color: #93c5fd !important; }

/* ── OR divider ── */
.or-divider {
    display: flex; align-items: center; gap: 12px;
    margin: 16px 0; color: rgba(255,255,255,0.38);
    font-size: 11px; font-weight: 600; letter-spacing: 0.12em;
}
.or-divider::before, .or-divider::after {
    content: ''; flex: 1; height: 1px;
    background: rgba(255,255,255,0.14);
}

/* ── Forgot password ── */
.forgot-text {
    text-align: right; font-size: 12px; color: #60a5fa;
    font-weight: 600; cursor: pointer;
    transition: color 0.2s; user-select: none;
}
.forgot-text:hover { color: #93c5fd; }

/* ── Selectbox dark theme ── */
.stSelectbox > div > div {
    background-color: #1e293b !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    border-radius: 14px !important; color: #ffffff !important;
}
.stSelectbox label {
    color: rgba(255,255,255,0.72) !important; font-size: 11px !important;
    font-weight: 700 !important; letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
}

/* ── Alerts ── */
.stAlert > div { background: rgba(255,255,255,0.12) !important; border-radius: 14px !important; }

/* ── Responsive ── */
@media (max-width: 600px) {
    .auth-card { padding: 26px 18px; border-radius: 22px; }
    .hero-title { font-size: 1.42rem; }
    .hero-icon-ring { width: 72px; height: 72px; font-size: 34px; }
}
</style>
""", unsafe_allow_html=True)




# ─────────────────────────────────────────────
# 4. Navigation helpers
# ─────────────────────────────────────────────
def go_home():
    st.session_state.update({'page':'home','logged_in':False,'user':None,'role':None})

def do_login(identifier, password, expected_role):
    if not identifier.strip() or not password:
        return False, "Please fill in all fields."
    user = auth.authenticate_user(identifier.strip(), password)
    if not user:
        return False, "Invalid username or password."
    if user['role'] != expected_role:
        target = "Admin" if expected_role == 'admin' else "Employee"
        return False, f"This account cannot access the {target} portal."
    st.session_state['logged_in'] = True
    st.session_state['user'] = dict(user)
    st.session_state['role'] = user['role']
    st.session_state['page'] = 'dashboard'
    return True, f"Welcome, {user['name']}!"

# Right panel removed to avoid raw HTML/backside code appearing in the UI.

# ─────────────────────────────────────────────
# 6. AUTH PAGE
# ─────────────────────────────────────────────
def show_auth_page():
    import streamlit.components.v1 as components

    # ── Session state init ──
    if 'auth_portal' not in st.session_state:
        st.session_state['auth_portal'] = 'employee'
    if 'auth_view' not in st.session_state:
        st.session_state['auth_view'] = 'login'   # 'login' | 'register'
    if 'show_pw' not in st.session_state:
        st.session_state['show_pw'] = False
    if 'show_reg_pw' not in st.session_state:
        st.session_state['show_reg_pw'] = False
    if 'show_reg_cpw' not in st.session_state:
        st.session_state['show_reg_cpw'] = False

    # ── Animated background ──
    st.markdown("""
    <div class="bg-bubbles">
        <div class="bubble b1"></div>
        <div class="bubble b2"></div>
        <div class="bubble b3"></div>
        <div class="dot-grid tl"></div>
        <div class="dot-grid br"></div>
    </div>
    """, unsafe_allow_html=True)

    # ── Three-column layout: blank | content | blank ──
    _, center, _ = st.columns([1, 2.2, 1])

    with center:
        # ── Hero ──
        st.markdown("""
        <div class="hero-wrap">
            <div class="hero-icon-ring">📅</div>
            <h1 class="hero-title">Leave Management Agent</h1>
            <p class="hero-subtitle">Smart Leave Tracking &amp; Management System</p>
        </div>
        """, unsafe_allow_html=True)

        # ════════════════════════════
        # LOGIN VIEW
        # ════════════════════════════
        if st.session_state['auth_view'] == 'login':

            # ── Portal toggle ──
            st.markdown('<p class="section-label">Choose Your Portal</p>', unsafe_allow_html=True)
            portal_opts = ["👤  Employee", "🛡️  Admin"]
            default_idx = 0 if st.session_state['auth_portal'] == 'employee' else 1
            portal_choice = st.radio(
                "portal", portal_opts,
                index=default_idx, horizontal=True,
                key="portal_radio", label_visibility="collapsed"
            )
            new_portal = 'employee' if portal_choice == portal_opts[0] else 'admin'
            if new_portal != st.session_state['auth_portal']:
                st.session_state['auth_portal'] = new_portal
                st.rerun()

            # ── Glass card ──
            st.markdown('<div class="auth-card">', unsafe_allow_html=True)
            st.markdown('<p class="form-title">Sign In</p>', unsafe_allow_html=True)

            # Email
            identifier = st.text_input(
                "Email Address", placeholder="you@example.com",
                key="auth_email"
            )

            # Password with show/hide (key swap preserves value)
            pw_col, eye_col = st.columns([8, 1])
            with pw_col:
                if st.session_state['show_pw']:
                    if 'auth_pass_txt' not in st.session_state:
                        st.session_state['auth_pass_txt'] = st.session_state.get('auth_pass_pw', '')
                    password = st.text_input(
                        "Password", key="auth_pass_txt", placeholder="Enter your password"
                    )
                else:
                    if 'auth_pass_pw' not in st.session_state:
                        st.session_state['auth_pass_pw'] = st.session_state.get('auth_pass_txt', '')
                    password = st.text_input(
                        "Password", type="password", key="auth_pass_pw", placeholder="••••••••"
                    )
            with eye_col:
                st.markdown('<div class="eye-btn">', unsafe_allow_html=True)
                if st.button(
                    "🙈" if st.session_state['show_pw'] else "👁️",
                    key="toggle_pw"
                ):
                    st.session_state['show_pw'] = not st.session_state['show_pw']
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            # Remember Me + Forgot Password
            rm_col, fp_col = st.columns([1.2, 1])
            with rm_col:
                st.checkbox("Remember Me", value=True, key="remember_me")
            with fp_col:
                st.markdown(
                    '<p class="forgot-text">Forgot Password?</p>',
                    unsafe_allow_html=True
                )

            # Sign In button
            st.markdown('<div class="sign-in-btn">', unsafe_allow_html=True)
            if st.button("Sign In  →", use_container_width=True, key="sign_in_btn"):
                success, msg = do_login(
                    identifier, password, st.session_state['auth_portal']
                )
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
            st.markdown('</div>', unsafe_allow_html=True)

            # ── OR divider ──
            st.markdown('<div class="or-divider">OR</div>', unsafe_allow_html=True)

            # ── Create account ──
            st.markdown(
                '<div style="text-align:center;font-size:13px;color:rgba(255,255,255,0.60);">'
                "Don't have an account?</div>",
                unsafe_allow_html=True
            )
            st.markdown('<div class="link-btn" style="text-align:center;">', unsafe_allow_html=True)
            if st.button("Create Account", key="go_register"):
                st.session_state['auth_view'] = 'register'
                st.session_state['show_pw'] = False
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)  # /auth-card

        # ════════════════════════════
        # REGISTER VIEW
        # ════════════════════════════
        else:
            st.markdown('<div class="auth-card">', unsafe_allow_html=True)
            st.markdown('<p class="form-title">Create Account</p>', unsafe_allow_html=True)

            # Row 1: Full Name + Employee ID
            n_col, id_col = st.columns(2)
            with n_col:
                full_name = st.text_input(
                    "Full Name", placeholder="John Doe", key="reg_name"
                )
            with id_col:
                emp_id = st.text_input(
                    "Employee ID", placeholder="EMP-001", key="reg_emp_id"
                )

            # Email
            email_reg = st.text_input(
                "Email", placeholder="you@company.com", key="reg_email"
            )

            # Auto-generated username (display only)
            auto_uname = email_reg.split('@')[0].lower() if '@' in email_reg and email_reg.split('@')[0] else ''
            st.text_input(
                "Username (auto-generated from email)",
                value=auto_uname if auto_uname else "—",
                disabled=True
            )

            # Password with show/hide
            rpw_col, reye_col = st.columns([8, 1])
            with rpw_col:
                if st.session_state['show_reg_pw']:
                    if 'reg_pass_txt' not in st.session_state:
                        st.session_state['reg_pass_txt'] = st.session_state.get('reg_pass_pw', '')
                    reg_password = st.text_input(
                        "Password", key="reg_pass_txt", placeholder="Min. 6 characters"
                    )
                else:
                    if 'reg_pass_pw' not in st.session_state:
                        st.session_state['reg_pass_pw'] = st.session_state.get('reg_pass_txt', '')
                    reg_password = st.text_input(
                        "Password", type="password", key="reg_pass_pw",
                        placeholder="Min. 6 characters"
                    )
            with reye_col:
                st.markdown('<div class="eye-btn">', unsafe_allow_html=True)
                if st.button(
                    "🙈" if st.session_state['show_reg_pw'] else "👁️",
                    key="toggle_reg_pw"
                ):
                    st.session_state['show_reg_pw'] = not st.session_state['show_reg_pw']
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            # Confirm password with show/hide
            rcpw_col, rceye_col = st.columns([8, 1])
            with rcpw_col:
                if st.session_state['show_reg_cpw']:
                    if 'reg_cpass_txt' not in st.session_state:
                        st.session_state['reg_cpass_txt'] = st.session_state.get('reg_cpass_pw', '')
                    reg_confirm = st.text_input(
                        "Confirm Password", key="reg_cpass_txt", placeholder="Re-enter password"
                    )
                else:
                    if 'reg_cpass_pw' not in st.session_state:
                        st.session_state['reg_cpass_pw'] = st.session_state.get('reg_cpass_txt', '')
                    reg_confirm = st.text_input(
                        "Confirm Password", type="password", key="reg_cpass_pw",
                        placeholder="Re-enter password"
                    )
            with rceye_col:
                st.markdown('<div class="eye-btn">', unsafe_allow_html=True)
                if st.button(
                    "🙈" if st.session_state['show_reg_cpw'] else "👁️",
                    key="toggle_reg_cpw"
                ):
                    st.session_state['show_reg_cpw'] = not st.session_state['show_reg_cpw']
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            # Department + Role
            dept_col, role_col = st.columns(2)
            with dept_col:
                department = st.selectbox(
                    "Department",
                    ["Engineering", "HR", "Finance", "Marketing",
                     "Operations", "Sales", "IT", "Legal", "Other"],
                    key="reg_dept"
                )
            with role_col:
                st.selectbox(
                    "Role",
                    ["Employee"],
                    key="reg_role",
                    disabled=True,
                    help="Admin accounts can only be created by an existing admin."
                )

            # Register button
            st.markdown('<div class="register-btn">', unsafe_allow_html=True)
            if st.button("Register  →", use_container_width=True, key="register_btn"):
                if not full_name.strip():
                    st.error("⚠️ Please enter your full name.")
                elif not email_reg.strip() or '@' not in email_reg:
                    st.error("⚠️ Please enter a valid email address.")
                elif len(reg_password) < 6:
                    st.error("⚠️ Password must be at least 6 characters.")
                elif reg_password != reg_confirm:
                    st.error("⚠️ Passwords do not match.")
                else:
                    ok, msg = database.register_user(
                        full_name.strip(), email_reg.strip(),
                        reg_password, role='employee'
                    )
                    if ok:
                        st.success(f"🎉 {msg}")
                        # Reset register state
                        for k in ['reg_name','reg_emp_id','reg_email','reg_dept',
                                  'reg_pass_txt','reg_pass_pw','reg_cpass_txt','reg_cpass_pw',
                                  'show_reg_pw','show_reg_cpw']:
                            st.session_state.pop(k, None)
                        st.session_state['auth_view'] = 'login'
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")
            st.markdown('</div>', unsafe_allow_html=True)

            # Sign In link
            st.markdown(
                '<div style="text-align:center;font-size:13px;color:rgba(255,255,255,0.60);margin-top:10px;">'
                'Already have an account?</div>',
                unsafe_allow_html=True
            )
            st.markdown('<div class="link-btn" style="text-align:center;">', unsafe_allow_html=True)
            if st.button("Sign In", key="go_login"):
                st.session_state['auth_view'] = 'login'
                st.session_state['show_reg_pw'] = False
                st.session_state['show_reg_cpw'] = False
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)  # /auth-card

        # Footer
        st.markdown("""
        <div style="text-align:center;color:rgba(255,255,255,0.32);font-size:11px;
                    margin-top:14px;padding-bottom:20px;">
            &copy; 2026 Leave Management Agent &nbsp;·&nbsp; All rights reserved.
        </div>
        """, unsafe_allow_html=True)

    # Enter key → trigger Sign In
    components.html("""
    <script>
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            const btns = Array.from(window.parent.document.querySelectorAll('button'));
            for (const b of btns) {
                const t = b.innerText.trim().toLowerCase();
                if (t.includes('sign in') || t.includes('register')) {
                    b.click(); break;
                }
            }
        }
    });
    </script>
    """, height=0)

# ─────────────────────────────────────────────
# 7. DASHBOARD PAGE
# ─────────────────────────────────────────────
def show_dashboard():
    current_user = st.session_state['user']
    role = st.session_state['role']

    # Sidebar
    st.sidebar.markdown(f"""
    <div style="text-align:center; padding:20px 0 10px 0;">
        <div style="font-size:48px;">{"🛡️" if role=="admin" else "👤"}</div>
        <div style="font-size:16px; font-weight:700; color:#0f172a; margin-top:8px;">{current_user['name']}</div>
        <div style="margin-top:6px;">
            <span class="status-badge"
              style="background:{'#ede9fe' if role=='admin' else '#eff6ff'};
                     color:{'#5b21b6' if role=='admin' else '#1e40af'};
                     border:1px solid {'#ddd6fe' if role=='admin' else '#bfdbfe'};
                     font-size:10px;">
                {role.upper()}
            </span>
        </div>
    </div>
    <hr style="border-color:#e2e8f0; margin:16px 0;">
    <div style="font-size:12px; font-weight:600; color:#94a3b8;
                text-transform:uppercase; letter-spacing:0.1em; margin-bottom:12px;">
        Navigation
    </div>
    """, unsafe_allow_html=True)

    if st.sidebar.button("🏠  Home", use_container_width=True):
        go_home()
        st.rerun()

    st.sidebar.markdown("""
    <hr style="border-color:#e2e8f0; margin:20px 0 12px 0;">
    <div style="text-align:center; font-size:11px; color:#94a3b8; line-height:1.8;">
        Leave Management Agent<br>
        v1.0.0 · SQLite · Streamlit · Gemini AI
    </div>
    """, unsafe_allow_html=True)

    # Restore light background for dashboard
    st.markdown("""
    <style>
    html, body, [class*="css"] { font-family: 'Poppins', sans-serif !important; min-height: 100% !important; overflow-y: auto !important; }
    .stApp { background: #f8fafc !important; min-height: 100vh !important; overflow-y: auto !important; }
    .block-container { min-height: 100vh !important; overflow-y: auto !important; max-width: 100% !important; padding-top: 0 !important; }
    section[data-testid="stMain"] { min-height: 100vh !important; overflow-y: auto !important; }
    section[data-testid="stMain"] > div:first-child { max-width: 100% !important; min-height: 100vh !important; overflow-y: auto !important; }
    </style>
    """, unsafe_allow_html=True)

    if role == 'admin':
        admin.show_admin_dashboard(current_user)
    else:
        employee.show_employee_dashboard(current_user)


# ─────────────────────────────────────────────
# 8. Router
# ─────────────────────────────────────────────
if st.session_state['logged_in'] and st.session_state['page'] == 'dashboard':
    show_dashboard()
else:
    # Guard: if somehow flagged logged in but wrong page, reset
    if st.session_state.get('logged_in') and st.session_state.get('page') != 'dashboard':
        go_home()
    show_auth_page()
