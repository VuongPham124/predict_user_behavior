import streamlit as st

def inject_custom_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        * { font-family: 'Inter', sans-serif; }
        
        .main-header {
            background: #00A19B;
            padding: 2rem;
            border-radius: 10px;
            color: white;
            text-align: center;
            margin-bottom: 1rem;
        }
        .main-header h1 { font-size: 2rem; }
        .main-header p { font-size: 1rem; }
        
        .predict-card {
            background: #FF9B33;
            padding: 1rem;
            border-radius: 12px;
            text-align: center;
            transition: 0.3s;
        }
        .predict-card:hover {
            background: #FBD38D;
        }

        .predict-card-title {
            font-size: 1.1rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }

        .predict-card-prob {
            font-size: 1.4rem;
            font-weight: 600;
        }
                
        .stButton > button {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 0.8rem 1.5rem;
            border-radius: 10px;
            font-weight: 600;
            width: 100%;
        }
        .stTextArea textarea, .stNumberInput > div > div > input, .stSelectbox > div > div {
            border-radius: 8px !important;
            border: 1px solid #e2e8f0 !important;
        }
        .footer {
            margin-top: 3rem;
            padding-top: 1rem;
            border-top: 1px solid #e0e0e0;
            text-align: center;
            font-size: 0.9rem;
            color: #777;
        }
    </style>
    """, unsafe_allow_html=True)