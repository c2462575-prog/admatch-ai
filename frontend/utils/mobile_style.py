"""Mobile-responsive CSS injection for Streamlit."""
import streamlit as st


def inject_mobile_css():
    """Inject CSS to improve mobile experience."""
    st.markdown("""
    <style>
    /* === Mobile Responsive Overrides === */

    /* Reduce padding on mobile */
    @media (max-width: 768px) {
        .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            padding-top: 2rem !important;
        }

        /* Stack columns vertically on mobile */
        [data-testid="stHorizontalBlock"] {
            flex-wrap: wrap !important;
        }
        [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
            width: 100% !important;
            flex: 1 1 100% !important;
            min-width: 100% !important;
        }

        /* Smaller titles */
        h1 { font-size: 1.5rem !important; }
        h2 { font-size: 1.25rem !important; }
        h3 { font-size: 1.1rem !important; }

        /* Fix metric cards */
        [data-testid="stMetric"] {
            padding: 0.5rem !important;
        }
        [data-testid="stMetricValue"] {
            font-size: 1.2rem !important;
        }

        /* Fix tables */
        table { font-size: 0.8rem !important; }

        /* Sidebar collapse by default on mobile */
        [data-testid="stSidebar"] {
            min-width: 0 !important;
        }

        /* Charts responsive */
        .js-plotly-plot {
            width: 100% !important;
        }

        /* Code blocks */
        code {
            font-size: 0.85rem !important;
            word-break: break-all !important;
        }
    }

    /* === Tablet (768-1024px) === */
    @media (min-width: 769px) and (max-width: 1024px) {
        .block-container {
            padding-left: 2rem !important;
            padding-right: 2rem !important;
        }

        [data-testid="stHorizontalBlock"] {
            flex-wrap: wrap !important;
        }
        /* Allow 2 columns on tablet */
        [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
            min-width: 45% !important;
        }
    }

    /* === General UI Polish === */
    /* Better card borders */
    [data-testid="stExpander"] {
        border-radius: 8px !important;
    }

    /* Smoother buttons */
    .stButton > button {
        border-radius: 8px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
    }

    /* Better form inputs */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div {
        border-radius: 8px !important;
    }

    /* Progress bar styling */
    .stProgress > div > div > div {
        border-radius: 4px !important;
    }

    /* Container borders */
    [data-testid="stVerticalBlockBorderWrapper"]:has(> div > [data-testid="stVerticalBlock"] > [data-testid="stMarkdown"]) {
        border-radius: 12px !important;
    }

    /* Hide Streamlit branding on mobile */
    @media (max-width: 768px) {
        #MainMenu { display: none !important; }
        footer { display: none !important; }
        header { display: none !important; }
    }
    </style>
    """, unsafe_allow_html=True)
