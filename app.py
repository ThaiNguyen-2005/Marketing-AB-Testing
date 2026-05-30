import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.power import TTestIndPower
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import confusion_matrix, roc_curve, auc
from sklearn.pipeline import make_pipeline

# 1. Page Configuration
st.set_page_config(
    page_title="Marketing A/B Testing Dashboard Pro",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for premium styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');
    
    /* Apply custom font across the app */
    html, body, [data-testid="stSidebar"], .stApp {
        font-family: 'Outfit', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    /* Premium style for stMetric */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 20px 24px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.15);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        transition: all 0.3s ease-in-out;
    }
    div[data-testid="stMetric"]:hover {
        background: rgba(255, 255, 255, 0.04);
        border-color: rgba(255, 255, 255, 0.2);
        box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.25);
        transform: translateY(-3px);
    }
    div[data-testid="stMetricValue"] {
        font-size: 28px !important;
        font-weight: 700 !important;
        background: linear-gradient(90deg, #3b82f6, #6366f1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* KPI Card Style CSS */
    .kpi-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
        gap: 20px;
        margin-bottom: 30px;
    }
    .kpi-card {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 20px;
        padding: 22px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.15);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        transition: all 0.3s ease-in-out;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: 160px;
    }
    .kpi-card:hover {
        transform: translateY(-5px);
        background: rgba(255, 255, 255, 0.04);
        border-color: rgba(255, 255, 255, 0.2);
        box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.25);
    }
    .kpi-icon {
        font-size: 2rem;
        margin-bottom: 8px;
    }
    .kpi-title {
        font-size: 0.8rem;
        color: #9ca3af;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .kpi-value {
        font-size: 1.8rem;
        font-weight: 800;
        color: #ffffff;
        margin: 6px 0;
    }
    .kpi-subtitle {
        display: flex;
        gap: 8px;
        margin-top: 6px;
        flex-wrap: wrap;
    }
    
    /* Custom Badge elements */
    .badge-control {
        background-color: rgba(59, 130, 246, 0.15);
        color: #3b82f6;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.8rem;
        border: 1px solid rgba(59, 130, 246, 0.3);
        display: inline-block;
    }
    .badge-test {
        background-color: rgba(255, 111, 67, 0.15);
        color: #ff6f43;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.8rem;
        border: 1px solid rgba(255, 111, 67, 0.3);
        display: inline-block;
    }
    .badge-winner {
        background: linear-gradient(135deg, rgba(234, 179, 8, 0.2), rgba(202, 138, 4, 0.2));
        color: #facc15;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.8rem;
        border: 1px solid rgba(234, 179, 8, 0.4);
        display: inline-block;
    }
    
    /* Styled container headers */
    h1, h2, h3 {
        font-weight: 700 !important;
        letter-spacing: -0.02em;
    }
    
    /* Premium style for custom buttons */
    .stButton>button {
        background: linear-gradient(135deg, #4f46e5, #3b82f6);
        color: white;
        border: none;
        padding: 10px 24px;
        border-radius: 12px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
        width: auto;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #3b82f6, #2563eb);
        box-shadow: 0 6px 16px rgba(59, 130, 246, 0.4);
        transform: translateY(-1px);
        color: white;
    }
    
    /* Visual prediction box */
    .prediction-box {
        background: rgba(79, 70, 229, 0.1);
        border: 1px solid rgba(79, 70, 229, 0.3);
        border-radius: 16px;
        padding: 24px;
        margin-top: 15px;
        box-shadow: 0 8px 32px 0 rgba(79, 70, 229, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# 2. Global Metric Labels Map
METRIC_LABELS = {
    "purchase": "Lượt đơn hàng (Purchases)",
    "spend_usd": "Chi phí (Daily Spend USD)",
    "website_clicks": "Lượt click website (Clicks)",
    "impressions": "Lượt hiển thị (Impressions)",
    "reach": "Lượt tiếp cận (Reach)",
    "searches": "Lượt tìm kiếm (Searches)",
    "view_content": "Lượt xem sản phẩm (View Content)",
    "add_to_cart": "Lượt thêm vào giỏ hàng (Add to Cart)"
}

# 3. Load Cleaned Dataset
@st.cache_data
def load_data():
    df = pd.read_csv("data/processed/cleaned_marketing.csv")
    df['date'] = pd.to_datetime(df['date'])
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Không thể tải tệp cleaned_marketing.csv. Vui lòng kiểm tra lại đường dẫn! Lỗi: {e}")
    st.stop()

control_df = df[df['group'] == 'control'].sort_values('date')
test_df = df[df['group'] == 'test'].sort_values('date')

# 4. Sidebar Navigation
st.sidebar.markdown("""
<div style="text-align: center; margin-bottom: 10px;">
    <div style="font-size: 3.5rem; filter: drop-shadow(0 0 12px rgba(79, 70, 229, 0.5)); margin-bottom: 5px; display: inline-block;">
        ⚡
    </div>
    <h2 style="margin: 0; font-size: 1.6rem; font-weight: 800; background: linear-gradient(135deg, #3b82f6, #8b5cf6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
        A/B Testing Pulse
    </h2>
</div>
""", unsafe_allow_html=True)
st.sidebar.markdown("---")

navigation = st.sidebar.radio(
    "Danh mục phân tích:",
    [
        "🏠 Tổng quan KPI",
        "📈 Phân tích Chuỗi thời gian",
        "🎯 Phễu chuyển đổi",
        "🧮 Kiểm định Welch t-test & Giả định",
        "🔄 Bootstrap Simulator",
        "📊 Phân tích Hồi quy & Chẩn đoán",
        "🤖 Mô hình Phân loại & ML App",
        "⚡ Phân tích Lực lượng (Power Analysis)",
        "📋 Đối chiếu giả thuyết"
    ]
)

st.sidebar.markdown("---")
st.sidebar.subheader("Thông tin chiến dịch")
st.sidebar.markdown(f"**Control (Đối chứng):** 29 ngày  \n<span class='badge-control'>Bidding truyền thống</span>", unsafe_allow_html=True)
st.sidebar.markdown(f"**Test (Thử nghiệm):** 30 ngày  \n<span class='badge-test'>Bidding tự động</span>", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style="display: flex; align-items: center; gap: 12px; margin-top: 10px;">
    <div style="width: 40px; height: 40px; border-radius: 50%; background-color: rgba(255, 255, 255, 0.05); display: flex; align-items: center; justify-content: center; font-size: 1.25rem;">
        👤
    </div>
    <div style="display: flex; flex-direction: column;">
        <span style="font-size: 0.9rem; font-weight: 600; color: #fff;">Nguyễn Trần Bảo Thái</span>
        <span style="font-size: 0.75rem; color: #6b7280;">Data Analyst</span>
    </div>
</div>
""", unsafe_allow_html=True)

# 5. Main Title
st.title("📊 Marketing A/B Testing Production Dashboard")
st.markdown("Hệ thống phân tích hiệu suất chiến dịch quảng cáo & Mô hình dự đoán học máy")
st.markdown("---")

# 6. Render Sections based on Navigation Selection

if navigation == "🏠 Tổng quan KPI":
    st.header("🏠 Tổng quan hiệu suất sản xuất (Production KPIs)")
    st.markdown("Bảng điều khiển KPI cấp điều hành (Executive-level Dashboard)")
    
    # Calculate executive metrics
    total_p_c = control_df['purchase'].sum()
    total_p_t = test_df['purchase'].sum()
    
    cr_c = (control_df['purchase'].sum() / control_df['website_clicks'].sum()) * 100
    cr_t = (test_df['purchase'].sum() / test_df['website_clicks'].sum()) * 100
    
    total_spend_c = control_df['spend_usd'].sum()
    total_spend_t = test_df['spend_usd'].sum()
    
    avg_spend_c = control_df['spend_usd'].mean()
    avg_spend_t = test_df['spend_usd'].mean()
    
    cpa_c = total_spend_c / total_p_c
    cpa_t = total_spend_t / total_p_t
    
    # HTML Render for KPI Cards
    kpi_html = f"""
    <div class="kpi-container">
        <div class="kpi-card">
            <div class="kpi-icon">🛒</div>
            <div class="kpi-title">Tổng đơn hàng (Total Purchases)</div>
            <div class="kpi-value">{total_p_c:,.0f} <span style="font-size:1.1rem;color:#6b7280;">vs</span> {total_p_t:,.0f}</div>
            <div class="kpi-subtitle">
                <span class="badge-control">Control: {control_df['purchase'].mean():.1f}/ngày</span>
                <span class="badge-test">Test: {test_df['purchase'].mean():.1f}/ngày</span>
            </div>
        </div>
        <div class="kpi-card">
            <div class="kpi-icon">🔄</div>
            <div class="kpi-title">Tỷ lệ chuyển đổi (Conversion Rate)</div>
            <div class="kpi-value">{cr_c:.2f}% <span style="font-size:1.1rem;color:#6b7280;">vs</span> {cr_t:.2f}%</div>
            <div class="kpi-subtitle">
                <span class="badge-control">CTR: {(control_df['website_clicks'].sum()/control_df['impressions'].sum()*100):.2f}%</span>
                <span class="badge-test">CTR: {(test_df['website_clicks'].sum()/test_df['impressions'].sum()*100):.2f}%</span>
            </div>
        </div>
        <div class="kpi-card">
            <div class="kpi-icon">💰</div>
            <div class="kpi-title">Chi phí hàng ngày (Average Spend)</div>
            <div class="kpi-value">${avg_spend_c:,.0f} <span style="font-size:1.1rem;color:#6b7280;">vs</span> ${avg_spend_t:,.0f}</div>
            <div class="kpi-subtitle">
                <span class="badge-control">CPA: ${cpa_c:.2f}</span>
                <span class="badge-test">CPA: ${cpa_t:.2f}</span>
            </div>
        </div>
        <div class="kpi-card">
            <div class="kpi-icon">🏆</div>
            <div class="kpi-title">Chiến dịch chiến thắng (Winner)</div>
            <div class="kpi-value" style="color: #facc15; font-size: 1.5rem; margin-top: 12px; font-weight: 700;">Control Group</div>
            <div class="kpi-subtitle">
                <span class="badge-winner">Tiết kiệm 11.5% CPA</span>
            </div>
        </div>
    </div>
    """
    st.markdown(kpi_html, unsafe_allow_html=True)
    
    st.markdown("### 📊 Chi tiết so sánh hiệu suất Trung bình ngày (Daily Performance)")
    kpis = ['spend_usd', 'impressions', 'reach', 'website_clicks', 'purchase']
    c_means = control_df[kpis].mean()
    t_means = test_df[kpis].mean()
    pct_diffs = ((t_means - c_means) / c_means) * 100
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            label="Chi phí quảng cáo trung bình",
            value=f"${c_means['spend_usd']:,.0f} vs ${t_means['spend_usd']:,.0f}",
            delta=f"{pct_diffs['spend_usd']:.2f}% (Test vs Control)"
        )
    with col2:
        st.metric(
            label="Lượt hiển thị trung bình (Impressions)",
            value=f"{c_means['impressions']/1000:.1f}K vs {t_means['impressions']/1000:.1f}K",
            delta=f"{pct_diffs['impressions']:.2f}% (Test vs Control)"
        )
    with col3:
        st.metric(
            label="Lượt click website trung bình (Clicks)",
            value=f"{c_means['website_clicks']:,.0f} vs {t_means['website_clicks']:,.0f}",
            delta=f"{pct_diffs['website_clicks']:.2f}% (Test vs Control)"
        )
    with col4:
        st.metric(
            label="Lượt đơn hàng trung bình (Purchases)",
            value=f"{c_means['purchase']:.1f} vs {t_means['purchase']:.1f}",
            delta=f"{pct_diffs['purchase']:.2f}% (Test vs Control)",
            delta_color="off"
        )
        
    st.markdown("---")
    st.subheader("💡 Nhận xét chi tiết cấp điều hành (Executive Insights)")
    st.info("""
    - **Tại sao nhóm Control thắng cuộc?** Dù lượng đơn hàng (purchase) trung bình ngày giữa hai nhóm gần như tương đồng (22.8 vs 22.7 đơn/ngày) và không có sự khác biệt về mặt ý nghĩa thống kê (Welch t-test p = 0.945), nhóm **Control** lại tiết kiệm ngân sách đáng kể. Tổng chi tiêu quảng cáo của nhóm Test cao hơn Control **11.24%** dẫn đến chi phí trên một đơn hàng (**CPA**) của nhóm Test bị đội lên **$4.92** so với **$4.41** của Control.
    - **Cơ chế phân phối của Bidding tự động (Test):** Nhóm **Test** đạt tỷ lệ CTR rất cao (+45.41%) nhờ tập trung quảng cáo vào nhóm đối tượng có tỷ lệ tương tác ban đầu cao. Tuy nhiên, bidding tự động gặp lỗi **đứt gãy chuyển đổi cuối phễu** (giai đoạn Add-to-Cart sang Purchase), khiến cho chi phí tăng thêm không chuyển đổi thành đơn hàng tương xứng.
    """)

elif navigation == "📈 Phân tích Chuỗi thời gian":
    st.header("📈 Phân tích Chuỗi thời gian & Biến động")
    st.markdown("Khai thác trục thời gian của chiến dịch để theo dõi tính ổn định và sự phát triển lũy kế")
    
    time_tab1, time_tab2, time_tab3 = st.tabs(["Biến động hàng ngày", "Tỷ lệ chuyển đổi theo thời gian", "Đồ thị Lũy kế (Cumulative Charts)"])
    
    with time_tab1:
        st.subheader("Theo dõi chỉ số hàng ngày")
        metric_options = {
            "purchase": "Lượt đơn hàng (Purchases)",
            "spend_usd": "Chi phí (Daily Spend USD)",
            "website_clicks": "Lượt click website (Clicks)",
            "impressions": "Lượt hiển thị (Impressions)"
        }
        selected_metric = st.selectbox("Chọn chỉ số để hiển thị:", list(metric_options.keys()), format_func=lambda x: metric_options[x], key="time_series_daily")
        
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(
            x=control_df['date'], y=control_df[selected_metric],
            mode='lines+markers', name='Control',
            line=dict(color='#3b82f6', width=2.5),
            marker=dict(size=6)
        ))
        fig_line.add_trace(go.Scatter(
            x=test_df['date'], y=test_df[selected_metric],
            mode='lines+markers', name='Test',
            line=dict(color='#ff6f43', width=2.5),
            marker=dict(size=6)
        ))
        fig_line.update_layout(
            title=f"Xu hướng biến động của {metric_options[selected_metric]}",
            xaxis_title="Ngày",
            yaxis_title=metric_options[selected_metric],
            hovermode="x unified",
            template="plotly_dark"
        )
        st.plotly_chart(fig_line, use_container_width=True)
        
    with time_tab2:
        st.subheader("Tỷ lệ chuyển đổi hàng ngày (Daily Conversion Rate)")
        st.markdown("Tỷ lệ chuyển đổi được tính bằng: $\\text{{CR}} = \\frac{\\text{{Lượt đơn hàng (Purchases)}}}{\\text{{Lượt click website (Clicks)}}} \\times 100$")
        
        cr_c_series = (control_df['purchase'] / control_df['website_clicks']) * 100
        cr_t_series = (test_df['purchase'] / test_df['website_clicks']) * 100
        
        fig_cr = go.Figure()
        fig_cr.add_trace(go.Scatter(
            x=control_df['date'], y=cr_c_series,
            mode='lines+markers', name='Control (Bidding truyền thống)',
            line=dict(color='#3b82f6', width=2),
            marker=dict(size=5)
        ))
        fig_cr.add_trace(go.Scatter(
            x=test_df['date'], y=cr_t_series,
            mode='lines+markers', name='Test (Bidding tự động)',
            line=dict(color='#ff6f43', width=2),
            marker=dict(size=5)
        ))
        fig_cr.update_layout(
            title="Biến động Tỷ lệ chuyển đổi Click-to-Purchase theo ngày",
            xaxis_title="Ngày",
            yaxis_title="Tỷ lệ chuyển đổi (%)",
            hovermode="x unified",
            template="plotly_dark"
        )
        st.plotly_chart(fig_cr, use_container_width=True)
        
    with time_tab3:
        st.subheader("Hiệu số tích lũy của hai chiến dịch (Cumulative Performance)")
        st.markdown("Xem biểu đồ lũy kế giúp loại bỏ biến động nhiễu hàng ngày để thấy rõ xu hướng chênh lệch dài hạn.")
        
        cum_metric = st.selectbox(
            "Chọn chỉ số cộng dồn lũy kế:",
            ["purchase", "spend_usd", "website_clicks"],
            format_func=lambda x: {
                "purchase": "Đơn hàng lũy kế (Cumulative Purchases)",
                "spend_usd": "Chi phí lũy kế (Cumulative Spend USD)",
                "website_clicks": "Lượt click lũy kế (Cumulative Clicks)"
            }[x]
        )
        
        fig_cum = go.Figure()
        fig_cum.add_trace(go.Scatter(
            x=control_df['date'], y=control_df[cum_metric].cumsum(),
            mode='lines', name='Control Lũy kế',
            line=dict(color='#3b82f6', width=3),
            fill='tozeroy', fillcolor='rgba(59, 130, 246, 0.05)'
        ))
        fig_cum.add_trace(go.Scatter(
            x=test_df['date'], y=test_df[cum_metric].cumsum(),
            mode='lines', name='Test Lũy kế',
            line=dict(color='#ff6f43', width=3),
            fill='tozeroy', fillcolor='rgba(255, 111, 67, 0.05)'
        ))
        fig_cum.update_layout(
            title=f"Đồ thị lũy kế của {METRIC_LABELS[cum_metric]}",
            xaxis_title="Ngày",
            yaxis_title=f"Tổng số tích lũy",
            template="plotly_dark"
        )
        st.plotly_chart(fig_cum, use_container_width=True)

elif navigation == "🎯 Phễu chuyển đổi":
    st.header("🎯 Phễu chuyển đổi (Conversion Funnel)")
    st.markdown("Theo dõi tỷ lệ chuyển đổi lũy kế và so sánh hiệu suất chuyển đổi từng bước (step-by-step)")
    
    funnel_stages = ['impressions', 'website_clicks', 'searches', 'view_content', 'add_to_cart', 'purchase']
    stage_labels = ['Impressions', 'Clicks', 'Searches', 'View Content', 'Add to Cart', 'Purchase']
    
    c_means = [control_df[s].mean() for s in funnel_stages]
    t_means = [test_df[s].mean() for s in funnel_stages]
    
    # 1. Plotly Funnel Chart
    fig_funnel = go.Figure()
    fig_funnel.add_trace(go.Funnel(
        name='Control',
        y=stage_labels,
        x=c_means,
        textinfo="value+percent initial",
        marker=dict(color="#3b82f6")
    ))
    fig_funnel.add_trace(go.Funnel(
        name='Test',
        y=stage_labels,
        x=t_means,
        textinfo="value+percent initial",
        marker=dict(color="#ff6f43")
    ))
    fig_funnel.update_layout(
        title="Biểu đồ phễu chuyển đổi chiến dịch quảng cáo",
        template="plotly_dark"
    )
    st.plotly_chart(fig_funnel, use_container_width=True)
    
    # 2. Step-by-Step Conversion Table
    st.subheader("Chi tiết tỷ lệ chuyển đổi từng bước (Step-by-Step)")
    
    step_names = [
        'Impressions -> Clicks (CTR)',
        'Clicks -> Searches',
        'Searches -> View Content',
        'View Content -> Add to Cart',
        'Add to Cart -> Purchase'
    ]
    
    table_data = []
    for i in range(len(step_names)):
        c_rate = (c_means[i+1] / c_means[i]) * 100
        t_rate = (t_means[i+1] / t_means[i]) * 100
        diff = t_rate - c_rate
        
        status = "Test tốt hơn" if diff > 0.5 else ("Control tốt hơn" if diff < -0.5 else "Tương đồng")
        table_data.append({
            "Giai đoạn": step_names[i],
            "Control (%)": f"{c_rate:.2f}%",
            "Test (%)": f"{t_rate:.2f}%",
            "Chênh lệch": f"{diff:+.2f}%",
            "Đánh giá": status
        })
        
    st.table(pd.DataFrame(table_data))
    
    st.info("""
    **Insight Phễu:**
    - Chiến dịch **Test** vượt trội ở phần phễu trên (Impressions -> Clicks -> Searches). Tỷ lệ clicks tăng và nhu cầu tìm kiếm sau click cũng cao hơn nhóm Control.
    - Điểm đứt gãy lớn nhất ở nhóm **Test** nằm ở bước cuối: chuyển đổi từ thêm vào giỏ hàng (`add_to_cart`) sang mua hàng (`purchase`). Control đạt hiệu suất chuyển đổi **59.13%**, trong khi Test chỉ đạt **51.81%** (giảm gần 7.32% hiệu suất).
    """)

elif navigation == "🧮 Kiểm định Welch t-test & Giả định":
    st.header("🧮 Kiểm định Thống kê & Kiểm tra Giả định")
    st.markdown("Thực hiện kiểm định giả thuyết thống kê (Parametric & Non-parametric) và chẩn đoán phân phối dữ liệu")
    
    col1, col2 = st.columns(2)
    
    with col1:
        stat_metric = st.selectbox(
            "Chọn chỉ số kiểm định:",
            ["purchase", "spend_usd", "website_clicks", "impressions"],
            format_func=lambda x: METRIC_LABELS[x],
            key="welch_metric"
        )
    with col2:
        alpha = st.selectbox("Chọn mức ý nghĩa (\u03b1):", [0.01, 0.05, 0.10], index=1, format_func=lambda x: f"{x} (Độ tin cậy {(1-x)*100:.0f}%)", key="welch_alpha")
        
    # Welch's t-test execution
    c_vals = control_df[stat_metric].values
    t_vals = test_df[stat_metric].values
    
    t_stat, p_val = stats.ttest_ind(c_vals, t_vals, equal_var=False)
    
    # Calculate CIs
    n_c, n_t = len(c_vals), len(t_vals)
    mean_c, mean_t = c_vals.mean(), t_vals.mean()
    var_c, var_t = c_vals.var(ddof=1), t_vals.var(ddof=1)
    
    mean_diff = mean_t - mean_c
    se_diff = np.sqrt((var_c / n_c) + (var_t / n_t))
    
    # Welch-Satterthwaite df
    df_welch = ((var_c / n_c) + (var_t / n_t))**2 / (((var_c / n_c)**2 / (n_c - 1)) + ((var_t / n_t)**2 / (n_t - 1)))
    crit_t = stats.t.ppf(1 - alpha/2, df_welch)
    moe = crit_t * se_diff
    ci_lower, ci_upper = mean_diff - moe, mean_diff + moe
    
    # Cohen's d
    pooled_std = np.sqrt(((n_c - 1)*var_c + (n_t - 1)*var_t) / (n_c + n_t - 2))
    cohen_d = mean_diff / pooled_std
    
    # Group margin of error for individual means
    error_c = stats.t.ppf(0.975, n_c - 1) * (c_vals.std(ddof=1) / np.sqrt(n_c))
    error_t = stats.t.ppf(0.975, n_t - 1) * (t_vals.std(ddof=1) / np.sqrt(n_t))
    
    abs_d = abs(cohen_d)
    d_interpret = "Rất nhỏ (Negligible)" if abs_d < 0.2 else ("Nhỏ (Small)" if abs_d < 0.5 else ("Vừa (Medium)" if abs_d < 0.8 else "Lớn (Large)"))
    
    # Assumptions checks (Shapiro-Wilk normality test)
    shapiro_stat_c, shapiro_p_c = stats.shapiro(c_vals)
    shapiro_stat_t, shapiro_p_t = stats.shapiro(t_vals)
    
    # Non-parametric Mann-Whitney U test alternative
    u_stat, mw_p_val = stats.mannwhitneyu(c_vals, t_vals, alternative='two-sided')
    
    st.subheader("📊 Bảng kết quả kiểm định chi tiết (Welch t-test Report)")
    
    # Formatted Statistical Table
    stat_summary = pd.DataFrame({
        "Thông số kiểm định (Metric)": [
            "Trung bình nhóm Control (Control Mean)",
            "Trung bình nhóm Test (Test Mean)",
            "Hiệu số trung bình (Mean Difference)",
            "Trị số kiểm định t (T-Statistic)",
            "Hệ số P-value",
            "Mức ý nghĩa lựa chọn (Alpha)",
            "Khoảng tin cậy hiệu số (Confidence Interval)",
            "Kích thước hiệu ứng (Cohen's d)",
            "Đánh giá hiệu ứng (Effect Size)"
        ],
        "Giá trị thu được (Value)": [
            f"{mean_c:,.2f}",
            f"{mean_t:,.2f}",
            f"{mean_diff:+,.2f}",
            f"{t_stat:.4f}",
            f"{p_val:.5f}",
            f"{alpha:.2f}",
            f"[{ci_lower:.2f}, {ci_upper:.2f}]",
            f"{cohen_d:.4f}",
            d_interpret
        ]
    })
    
    # Dynamic coloring function based on significance
    def highlight_significance(row):
        is_p_row = row["Thông số kiểm định (Metric)"] == "Hệ số P-value"
        if is_p_row:
            if p_val < alpha:
                return ["background-color: rgba(46, 204, 113, 0.25); font-weight: bold"] * len(row)
            else:
                return ["background-color: rgba(231, 76, 60, 0.25); font-weight: bold"] * len(row)
        return [""] * len(row)
        
    st.dataframe(stat_summary.style.apply(highlight_significance, axis=1), use_container_width=True)
    
    col_inf1, col_inf2 = st.columns(2)
    with col_inf1:
        if p_val < alpha:
            st.success(f"🎉 **KẾT LUẬN: BÁC BỎ H₀ (REJECT H₀)** - Sự khác biệt về **{METRIC_LABELS[stat_metric]}** giữa hai nhóm có ý nghĩa thống kê rõ ràng ở mức độ tin cậy {(1-alpha)*100:.0f}%.")
        else:
            st.warning(f"⚠️ **KẾT LUẬN: THẤT BẠI BÁC BỎ H₀ (FAIL TO REJECT H₀)** - Không có sự chênh lệch có ý nghĩa thống kê nào về **{METRIC_LABELS[stat_metric]}** giữa Control và Test.")
            
    # Assumptions Check UI
    st.markdown("---")
    st.subheader("🛠️ Kiểm tra các giả định thống kê & Kiểm định phi tham số")
    
    col_a1, col_a2 = st.columns(2)
    
    with col_a1:
        st.markdown("##### 1. Giả định phân phối chuẩn (Normality Check - Shapiro-Wilk)")
        st.markdown(f"- Nhóm Control: Shapiro statistic = `{shapiro_stat_c:.4f}`, p-value = `{shapiro_p_c:.5f}`")
        st.markdown(f"- Nhóm Test: Shapiro statistic = `{shapiro_stat_t:.4f}`, p-value = `{shapiro_p_t:.5f}`")
        
        if shapiro_p_c >= 0.05 and shapiro_p_t >= 0.05:
            st.success("✅ **Đạt giả định phân phối chuẩn:** Cả hai mẫu đều không bác bỏ giả định phân phối chuẩn (p >= 0.05). Kiểm định Welch's t-test hoàn toàn đáng tin cậy.")
        else:
            st.warning("⚠️ **Vi phạm giả định phân phối chuẩn:** Ít nhất một mẫu có phân phối lệch chuẩn (p < 0.05). Tuy nhiên, vì cỡ mẫu mỗi nhóm tương đối đủ lớn ($N \\approx 30$), Welch's t-test vẫn khá vững chãi nhờ Định lý giới hạn trung tâm (CLT). Để kiểm chứng chéo, hãy quan sát kiểm định phi tham số bên cạnh.")
            
    with col_a2:
        st.markdown("##### 2. Kiểm định phi tham số thay thế (Mann-Whitney U test)")
        st.markdown("Mann-Whitney U test là kiểm định phi tham số thay thế khi dữ liệu lệch chuẩn và không yêu cầu giả định phân phối chuẩn.")
        st.markdown(f"- **U-Statistic:** `{u_stat:,.1f}` | **P-value:** `{mw_p_val:.5f}`")
        
        if mw_p_val < alpha:
            st.success(f"🎉 **Bác bỏ H₀ theo Mann-Whitney U test (p < {alpha}):** Phát hiện sự chênh lệch có ý nghĩa thống kê.")
        else:
            st.error(f"❌ **Chấp nhận H₀ theo Mann-Whitney U test (p >= {alpha}):** Không phát hiện sự chênh lệch có ý nghĩa thống kê nào.")

    # Visual comparison with error bars
    st.markdown("---")
    st.subheader("📊 Trực quan hóa giá trị trung bình & Khoảng tin cậy 95%")
    fig_ci = go.Figure()
    fig_ci.add_trace(go.Bar(
        name='Giá trị trung bình',
        x=['Control', 'Test'],
        y=[mean_c, mean_t],
        error_y=dict(
            type='data',
            array=[error_c, error_t],
            visible=True,
            thickness=2.5,
            width=15,
            color='rgba(255, 255, 255, 0.8)'
        ),
        marker_color=['#3b82f6', '#ff6f43'],
        opacity=0.85
    ))
    fig_ci.update_layout(
        title=f"So sánh giá trị trung bình kèm khoảng tin cậy 95% của {METRIC_LABELS[stat_metric]}",
        xaxis_title="Nhóm thử nghiệm",
        yaxis_title="Giá trị trung bình ngày",
        template="plotly_dark"
    )
    st.plotly_chart(fig_ci, use_container_width=True)

elif navigation == "🔄 Bootstrap Simulator":
    st.header("🔄 Mô phỏng Tái mẫu Bootstrap (Bootstrap Simulator)")
    st.markdown("Dựng phân phối mẫu bằng cách lấy mẫu lặp lại có thay thế 1,000 lần trực tiếp trên trình duyệt")
    
    control_vals = control_df['purchase'].values
    test_vals = test_df['purchase'].values
    
    # Use st.session_state to cache bootstrap results
    if 'boot_results' not in st.session_state:
        st.session_state.boot_results = None
        
    col_btn1, col_btn2 = st.columns([2, 5])
    with col_btn1:
        run_btn = st.button("🚀 Bắt đầu chạy mô phỏng Bootstrap (1,000 lần)")
    with col_btn2:
        if st.session_state.boot_results is not None:
            if st.button("🗑️ Xóa kết quả mô phỏng"):
                st.session_state.boot_results = None
                st.rerun()
                
    if run_btn:
        with st.spinner("Đang chạy mô phỏng tái mẫu (vectorized)..."):
            n_c = len(control_vals)
            n_t = len(test_vals)
            
            # Vectorized numpy simulation (very fast!)
            c_samples = np.random.choice(control_vals, size=(1000, n_c), replace=True)
            t_samples = np.random.choice(test_vals, size=(1000, n_t), replace=True)
            
            c_boot_means = c_samples.mean(axis=1)
            t_boot_means = t_samples.mean(axis=1)
            diff_boot_means = t_boot_means - c_boot_means
            
            # Calculate CIs
            c_ci = np.percentile(c_boot_means, [2.5, 97.5])
            t_ci = np.percentile(t_boot_means, [2.5, 97.5])
            diff_ci = np.percentile(diff_boot_means, [2.5, 97.5])
            
            # Cache in session state
            st.session_state.boot_results = {
                "c_boot_means": c_boot_means,
                "t_boot_means": t_boot_means,
                "diff_boot_means": diff_boot_means,
                "c_ci": c_ci,
                "t_ci": t_ci,
                "diff_ci": diff_ci
            }
            
    if st.session_state.boot_results is not None:
        res = st.session_state.boot_results
        c_boot_means = res["c_boot_means"]
        t_boot_means = res["t_boot_means"]
        diff_boot_means = res["diff_boot_means"]
        c_ci = res["c_ci"]
        t_ci = res["t_ci"]
        diff_ci = res["diff_ci"]
        
        # Calculate theoretical Welch standard error of difference
        var_c, var_t = control_vals.var(ddof=1), test_vals.var(ddof=1)
        n_c, n_t = len(control_vals), len(test_vals)
        se_diff = np.sqrt((var_c / n_c) + (var_t / n_t))
        se_boot = diff_boot_means.std()
        
        st.subheader("Kết quả mô phỏng")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**95% Bootstrap CI cho Control Mean:** `[{c_ci[0]:.2f}, {c_ci[1]:.2f}]`")
            st.markdown(f"**95% Bootstrap CI cho Test Mean:** `[{t_ci[0]:.2f}, {t_ci[1]:.2f}]`")
            st.markdown(f"**95% Bootstrap CI cho Hiệu số trung bình:** `[{diff_ci[0]:.2f}, {diff_ci[1]:.2f}]`")
            
            # Standard error convergence presentation
            st.markdown("##### 📊 So sánh Sai số chuẩn (Standard Error Convergence)")
            st.markdown(f"- **Sai số chuẩn lý thuyết (Welch SE):** `{se_diff:.4f}`")
            st.markdown(f"- **Sai số chuẩn thực nghiệm (Bootstrap SE):** `{se_boot:.4f}`")
            st.markdown(f"- **Độ lệch tuyệt đối giữa hai phương pháp:** `{abs(se_diff - se_boot):.5f}`")
        with col2:
            st.info("""
            **Kết luận phi tham số:**
            - Phân phối bootstrap trung bình của Control và Test chồng lấp lên nhau rất lớn.
            - Khoảng tin cậy 95% của hiệu số trung bình **chứa giá trị 0**.
            - Xác nhận vững chắc rằng **không có sự khác biệt có ý nghĩa thống kê** nào ở lượng đơn hàng giữa 2 chiến dịch.
            - **Sự tương đồng về Standard Error:** Sai số chuẩn từ Bootstrap hội tụ cực sát với công thức Welch lý thuyết, chứng minh tính tin cậy của cả hai phương pháp.
            """)
            
        # Draw Plotly Histograms
        fig_means = go.Figure()
        fig_means.add_trace(go.Histogram(x=c_boot_means, name='Control Mean', marker_color='#3b82f6', opacity=0.7))
        fig_means.add_trace(go.Histogram(x=t_boot_means, name='Test Mean', marker_color='#ff6f43', opacity=0.7))
        fig_means.update_layout(title="Phân phối Bootstrap của giá trị trung bình hai nhóm", barmode='overlay', template="plotly_dark")
        st.plotly_chart(fig_means, use_container_width=True)
        
        fig_diff = go.Figure()
        fig_diff.add_trace(go.Histogram(x=diff_boot_means, name='Hiệu số (Test - Control)', marker_color='#9f7aea', opacity=0.75))
        fig_diff.add_vline(x=0, line_dash="dash", line_color="red", annotation_text="Giá trị 0 (Không chênh lệch)")
        fig_diff.update_layout(title="Phân phối Bootstrap của Hiệu số trung bình", template="plotly_dark")
        st.plotly_chart(fig_diff, use_container_width=True)
    else:
        st.write("Nhấn nút phía trên để bắt đầu tính toán mô phỏng...")

elif navigation == "📊 Phân tích Hồi quy & Chẩn đoán":
    st.header("📊 Phân tích Hồi quy & Chẩn đoán mô hình OLS")
    st.markdown("Đánh giá các nhân tố ảnh hưởng tuyến tính đến đơn hàng (`purchase`), phân tích đa cộng tuyến VIF và kiểm tra các giả định hồi quy")

    reg_tab1, reg_tab2, reg_tab3 = st.tabs(["Hồi quy Đơn biến (Simple OLS)", "Hồi quy Đa biến (Multiple OLS) & VIF", "🛠️ Kiểm định Giả định OLS (Diagnostics)"])

    with reg_tab1:
        st.subheader("Hồi quy tuyến tính đơn biến: spend_usd vs purchase")
        st.markdown("Phân tích xem chi tiêu quảng cáo (`spend_usd`) có thực sự tác động tuyến tính đến lượng đơn hàng (`purchase`) hay không.")
        
        # Simple OLS
        X_simple = sm.add_constant(df['spend_usd'])
        y_simple = df['purchase']
        model_simple = sm.OLS(y_simple, X_simple).fit()
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Hệ số chặn (Intercept):** `{model_simple.params.iloc[0]:.4f}`")
            st.markdown(f"**Hệ số góc (Slope - spend_usd):** `{model_simple.params.iloc[1]:.4f}`")
            st.markdown(f"**R-squared ($R^2$):** `{model_simple.rsquared:.4f}`")
            st.markdown(f"**P-value của Spend:** `{model_simple.pvalues.iloc[1]:.4f}`")
        with col2:
            if model_simple.pvalues.iloc[1] < 0.05:
                st.success("💡 **Chi tiêu quảng cáo có tác động ý nghĩa thống kê** đến lượng đơn hàng (p < 0.05).")
            else:
                st.warning("💡 **Chi tiêu quảng cáo KHÔNG có tác động ý nghĩa thống kê** đến lượng đơn hàng (p >= 0.05).")
            st.markdown(f"Phương trình hồi quy: $\\text{{purchase}} = {model_simple.params.iloc[0]:.2f} + {model_simple.params.iloc[1]:.4f} \\times \\text{{spend\\_usd}}$")

        # Plotly plot showing the fit
        fig_ols = px.scatter(df, x='spend_usd', y='purchase', trendline="ols", 
                             trendline_color_override="red", 
                             title="Đường hồi quy spend_usd vs purchase",
                             labels={'spend_usd': 'Chi tiêu (USD)', 'purchase': 'Số đơn hàng'},
                             template="plotly_dark")
        st.plotly_chart(fig_ols, use_container_width=True)

    # Global multiselect definition for features
    all_features = ['spend_usd', 'impressions', 'reach', 'website_clicks', 'searches', 'view_content', 'add_to_cart']
    selected_features = st.multiselect(
        "Chọn các đặc trưng đưa vào mô hình hồi quy đa biến & Chẩn đoán:", 
        options=all_features,
        default=all_features,
        format_func=lambda x: METRIC_LABELS[x],
        key="regression_multi_select"
    )

    with reg_tab2:
        st.subheader("Hồi quy tuyến tính đa biến & Chỉ số VIF")
        st.markdown("Xây dựng mô hình OLS đa biến kết hợp nhiều đặc trưng trong phễu chuyển đổi để dự báo `purchase`.")
        
        if len(selected_features) == 0:
            st.warning("⚠️ Vui lòng chọn ít nhất một đặc trưng để chạy mô hình hồi quy!")
        else:
            X_multi = sm.add_constant(df[selected_features])
            model_multi = sm.OLS(df['purchase'], X_multi).fit()
            
            # Display coefficients in a clean table
            coef_df = pd.DataFrame({
                "Hệ số (Coefficient)": model_multi.params,
                "Sai số chuẩn (Std Error)": model_multi.bse,
                "T-Statistic": model_multi.tvalues,
                "P-value": model_multi.pvalues
            })
            st.markdown("**Kết quả hệ số hồi quy đa biến:**")
            st.dataframe(coef_df.style.format("{:.4f}").highlight_between(left=0, right=0.05, subset=["P-value"], color="rgba(46, 204, 113, 0.2)"), use_container_width=True)

            st.markdown(f"**R-squared ($R^2$):** `{model_multi.rsquared:.4f}` | **Adjusted $R^2$:** `{model_multi.rsquared_adj:.4f}`")
            
            # Calculate and display VIF (Corrected according to Statistical Learning theory by adding constant first)
            if len(selected_features) > 1:
                X_vif_with_const = sm.add_constant(df[selected_features])
                vifs = []
                # Compute VIF starting from index 1 to ignore the constant column
                for i in range(1, X_vif_with_const.shape[1]):
                    vif = variance_inflation_factor(X_vif_with_const.values, i)
                    vifs.append(vif)
                
                vif_data = pd.DataFrame({
                    "Đặc trưng (Feature)": selected_features,
                    "VIF": vifs
                })
                vif_data = vif_data.sort_values(by="VIF", ascending=False)
                
                st.subheader("⚠️ Đánh giá Đa cộng tuyến (Multicollinearity)")
                col_vif1, col_vif2 = st.columns([1, 1])
                with col_vif1:
                    st.dataframe(vif_data.style.format({"VIF": "{:.2f}"}).highlight_between(left=5, right=100, subset=["VIF"], color="rgba(231, 76, 60, 0.2)"), use_container_width=True)
                with col_vif2:
                    st.info("""
                    **Giải thích chỉ số VIF:**
                    - **VIF < 5:** Không xảy ra đa cộng tuyến nghiêm trọng.
                    - **VIF >= 5:** Có dấu hiệu đa cộng tuyến.
                    - **VIF >= 10:** Đa cộng tuyến nghiêm trọng.
                    
                    **Mẹo khám phá:** Hãy thử bỏ chọn `add_to_cart` (VIF > 12) hoặc `searches` (VIF > 9) trên hộp tùy chọn phía trên để quan sát xem độ cộng tuyến của mô hình hồi quy giảm nhanh thế nào và hệ số của các biến khác trở nên ổn định ra sao!
                    """)
            else:
                st.info("Cần ít nhất 2 đặc trưng được chọn để tính toán chỉ số đa cộng tuyến VIF.")

    with reg_tab3:
        st.subheader("🛠️ Kiểm định các giả định của OLS (OLS Assumptions)")
        st.markdown("Chẩn đoán thống kê để kiểm tra xem các giả định cốt lõi của mô hình OLS có bị vi phạm hay không.")
        
        if len(selected_features) == 0:
            st.warning("⚠️ Vui lòng chọn ít nhất một đặc trưng ở trên để chạy kiểm định chẩn đoán!")
        else:
            X_multi = sm.add_constant(df[selected_features])
            model_multi = sm.OLS(df['purchase'], X_multi).fit()
            residuals = model_multi.resid
            fitted_vals = model_multi.fittedvalues
            
            # 1. Shapiro-Wilk normality of residuals
            shapiro_stat_r, shapiro_p_r = stats.shapiro(residuals)
            
            # 2. Homoscedasticity check (Breusch-Pagan test)
            from statsmodels.stats.diagnostic import het_breuschpagan
            bp_test = het_breuschpagan(residuals, X_multi.values)
            bp_stat, bp_p = bp_test[0], bp_test[1]
            
            # 3. Autocorrelation (Durbin-Watson statistic)
            dw_stat = sm.stats.stattools.durbin_watson(residuals)
            
            diag_col1, diag_col2 = st.columns(2)
            with diag_col1:
                st.markdown("##### 1. Phân phối chuẩn của sai số (Normality of Residuals)")
                st.markdown(f"- **Kiểm định Shapiro-Wilk:** W = `{shapiro_stat_r:.4f}` | p-value = `{shapiro_p_r:.5f}`")
                if shapiro_p_r >= 0.05:
                    st.success("✅ **Giả định phân phối chuẩn được thỏa mãn:** Sai số tuân theo phân phối chuẩn (p >= 0.05).")
                else:
                    st.warning("⚠️ **Vi phạm giả định phân phối chuẩn (p < 0.05):** Sai số không phân phối chuẩn. Với dữ liệu marketing thực tế, điều này rất phổ biến nhưng không ảnh hưởng nhiều đến ước lượng hệ số hồi quy nhờ CLT.")
                
                st.markdown("##### 2. Giả định phương sai đồng nhất (Homoscedasticity)")
                st.markdown(f"- **Kiểm định Breusch-Pagan:** LM = `{bp_stat:.4f}` | p-value = `{bp_p:.5f}`")
                if bp_p >= 0.05:
                    st.success("✅ **Giả định phương sai đồng nhất được thỏa mãn:** Không phát hiện hiện tượng phương sai thay đổi (p >= 0.05).")
                else:
                    st.warning("⚠️ **Vi phạm giả định phương sai đồng nhất (Heteroscedasticity) (p < 0.05):** Phương sai sai số thay đổi. Ước lượng hệ số hồi quy vẫn không chệch nhưng sai số chuẩn có thể bị chệch (ảnh hưởng đến kiểm định t các hệ số).")
            
            with diag_col2:
                st.markdown("##### 3. Kiểm định tự tương quan (Autocorrelation)")
                st.markdown(f"- **Trị số Durbin-Watson:** `{dw_stat:.4f}`")
                if 1.5 <= dw_stat <= 2.5:
                    st.success("✅ **Không có tự tương quan nghiêm trọng:** Trị số Durbin-Watson nằm trong khoảng an toàn [1.5, 2.5] (không có tự tương quan chuỗi bậc nhất).")
                elif dw_stat < 1.5:
                    st.warning("⚠️ **Tự tương quan dương (Durbin-Watson < 1.5):** Các sai số có xu hướng tương quan dương theo thời gian.")
                else:
                    st.warning("⚠️ **Tự tương quan âm (Durbin-Watson > 2.5):** Các sai số có xu hướng tương quan âm theo thời gian.")
            
            st.markdown("---")
            st.subheader("📊 Đồ thị chẩn đoán (Diagnostic Plots)")
            plot_col1, plot_col2 = st.columns(2)
            
            with plot_col1:
                # Residuals vs Fitted values
                fig_res_fit = px.scatter(
                    x=fitted_vals, y=residuals,
                    labels={'x': 'Giá trị dự báo (Fitted Values)', 'y': 'Sai số (Residuals)'},
                    title="Sai số vs Giá trị dự báo (Residuals vs Fitted)"
                )
                fig_res_fit.add_hline(y=0, line_dash="dash", line_color="red")
                fig_res_fit.update_layout(template="plotly_dark")
                st.plotly_chart(fig_res_fit, use_container_width=True)
                st.info("💡 **Cách xem:** Các điểm dữ liệu cần phân bổ ngẫu nhiên và đều quanh đường ngang Y=0. Nếu điểm tạo thành hình phễu hay hình cong, giả định OLS bị vi phạm.")
                
            with plot_col2:
                # Q-Q Plot of Residuals
                sorted_residuals = np.sort(residuals)
                theoretical_quantiles = stats.probplot(residuals, dist="norm")[0][0]
                fig_qq = px.scatter(
                    x=theoretical_quantiles, y=sorted_residuals,
                    labels={'x': 'Phân vị lý thuyết (Theoretical Quantiles)', 'y': 'Phân vị thực nghiệm (Sample Quantiles)'},
                    title="Q-Q Plot của Sai số (Residuals Q-Q Plot)"
                )
                min_val = min(theoretical_quantiles.min(), sorted_residuals.min())
                max_val = max(theoretical_quantiles.max(), sorted_residuals.max())
                fig_qq.add_trace(go.Scatter(x=[min_val, max_val], y=[min_val, max_val], mode='lines', name='Đường tham chiếu', line=dict(dash='dash', color='red')))
                fig_qq.update_layout(template="plotly_dark", showlegend=False)
                st.plotly_chart(fig_qq, use_container_width=True)
                st.info("💡 **Cách xem:** Nếu các điểm nằm bám sát đường thẳng chéo tham chiếu màu đỏ, sai số hoàn toàn phân phối chuẩn.")

elif navigation == "🤖 Mô hình Phân loại & ML App":
    st.header("🤖 Mô hình Phân loại & Ứng dụng Dự báo (ML App)")
    st.markdown("Xây dựng, đánh giá mô hình máy học và tạo giao diện dự đoán tương tác thời gian thực")
    
    ml_tab1, ml_tab2 = st.tabs(["📊 Đánh giá Mô hình", "🔮 Ứng dụng Dự báo (Interactive Prediction)"])
    
    # Prepare classification data
    feat_cols = ['spend_usd', 'impressions', 'reach', 'website_clicks', 'searches', 'view_content', 'add_to_cart']
    X_class = df[feat_cols]
    y_class = (df['group'] == 'test').astype(int)
    
    # Interactive hyperparameters configuration
    with st.expander("⚙️ Tùy chỉnh tham số mô hình"):
        test_size_val = st.slider("Tỷ lệ tập kiểm tra (Test Size Ratio):", 0.10, 0.50, 0.25, 0.05, key="test_size_slider")
        rf_estimators = st.slider("Số lượng cây quyết định (n_estimators):", 10, 200, 100, 10, key="rf_est_slider")
        rf_max_depth = st.slider("Độ sâu tối đa của cây (max_depth):", 2, 10, 4, 1, key="rf_depth_slider")
        
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X_class, y_class, test_size=test_size_val, random_state=42, stratify=y_class)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Fit models
    lr_model = LogisticRegression(random_state=42)
    lr_model.fit(X_train_scaled, y_train)
    lr_train_acc = lr_model.score(X_train_scaled, y_train) * 100
    lr_test_acc = lr_model.score(X_test_scaled, y_test) * 100
    
    rf_model = RandomForestClassifier(random_state=42, n_estimators=rf_estimators, max_depth=rf_max_depth)
    rf_model.fit(X_train, y_train)
    rf_train_acc = rf_model.score(X_train, y_train) * 100
    rf_test_acc = rf_model.score(X_test, y_test) * 100
    
    # 5-fold CV to evaluate generalization performance without preprocessing leakages
    lr_pipeline = make_pipeline(StandardScaler(), LogisticRegression(random_state=42))
    lr_cv = cross_val_score(lr_pipeline, X_class, y_class, cv=5)
    lr_cv_mean, lr_cv_std = lr_cv.mean() * 100, lr_cv.std() * 100
    
    rf_cv = cross_val_score(RandomForestClassifier(random_state=42, n_estimators=rf_estimators, max_depth=rf_max_depth), X_class, y_class, cv=5)
    rf_cv_mean, rf_cv_std = rf_cv.mean() * 100, rf_cv.std() * 100
    
    with ml_tab1:
        st.subheader("Đánh giá độ chính xác của Mô hình Phân loại")
        st.markdown("Mô hình dự đoán xem một ngày thuộc nhóm chiến dịch nào (**Control** vs **Test**).")
        
        c_col1, c_col2 = st.columns(2)
        with c_col1:
            st.markdown("##### Logistic Regression")
            st.metric(label="Độ chính xác Train (Accuracy)", value=f"{lr_train_acc:.1f}%")
            st.metric(label="Độ chính xác Test (Accuracy)", value=f"{lr_test_acc:.1f}%")
            st.markdown(f"- **5-Fold Cross-Validation:** `{lr_cv_mean:.1f}% ± {lr_cv_std:.1f}%`")
        with c_col2:
            st.markdown("##### Random Forest Classifier")
            st.metric(label="Độ chính xác Train (Accuracy)", value=f"{rf_train_acc:.1f}%")
            st.metric(label="Độ chính xác Test (Accuracy)", value=f"{rf_test_acc:.1f}%")
            st.markdown(f"- **5-Fold Cross-Validation:** `{rf_cv_mean:.1f}% ± {rf_cv_std:.1f}%`")
            
        # Overfitting Analysis
        st.markdown("##### ⚠️ Đánh giá Quá khớp (Overfitting Analysis)")
        diff_rf = rf_train_acc - rf_test_acc
        if diff_rf > 15:
            st.warning(f"Mô hình Random Forest Classifier đang có dấu hiệu **Quá khớp (Overfitting)** nghiêm trọng (Độ chính xác trên Train là {rf_train_acc:.1f}% nhưng trên Test chỉ đạt {rf_test_acc:.1f}%, độ lệch {diff_rf:.1f}%). Điều này xảy ra do mô hình quá phức tạp so với kích thước tập dữ liệu nhỏ (n=59). Hãy thử kéo thanh trượt giảm độ sâu tối đa (`max_depth`) ở rộng rộng phía trên để kiểm soát hiện tượng quá khớp!")
        else:
            st.success("Mô hình hoạt động ổn định giữa tập Train và tập Test (không có hiện tượng quá khớp nghiêm trọng, độ lệch nằm trong tầm kiểm soát).")
            
        st.markdown("---")
        st.subheader("📈 Phân tích chuyên sâu: Ma trận nhầm lẫn & Đường cong ROC")
        
        col_plot1, col_plot2 = st.columns(2)
        
        # Calculate confusion matrix & ROC curve for Random Forest
        y_pred_rf = rf_model.predict(X_test)
        y_probs_rf = rf_model.predict_proba(X_test)[:, 1]
        
        with col_plot1:
            # Confusion Matrix Plot
            cm = confusion_matrix(y_test, y_pred_rf)
            fig_cm = px.imshow(
                cm,
                text_auto=True,
                labels=dict(x="Nhãn dự đoán", y="Nhãn thực tế", color="Số lượng ngày"),
                x=['Control', 'Test'],
                y=['Control', 'Test'],
                color_continuous_scale="Blues",
                title="Confusion Matrix (Random Forest)"
            )
            fig_cm.update_layout(template="plotly_dark")
            st.plotly_chart(fig_cm, use_container_width=True)
            
        with col_plot2:
            # ROC Curve Plot
            fpr, tpr, _ = roc_curve(y_test, y_probs_rf)
            roc_auc = auc(fpr, tpr)
            
            fig_roc = go.Figure()
            fig_roc.add_trace(go.Scatter(
                x=fpr, y=tpr, mode='lines',
                name=f'Random Forest (AUC = {roc_auc:.2f})',
                line=dict(color='#ff6f43', width=3)
            ))
            fig_roc.add_trace(go.Scatter(
                x=[0, 1], y=[0, 1], mode='lines',
                name='Đường ngẫu nhiên',
                line=dict(dash='dash', color='gray')
            ))
            fig_roc.update_layout(
                title="Receiver Operating Characteristic (ROC) Curve",
                xaxis_title="False Positive Rate",
                yaxis_title="True Positive Rate",
                template="plotly_dark",
                legend=dict(yanchor="bottom", y=0.01, xanchor="right", x=0.99)
            )
            st.plotly_chart(fig_roc, use_container_width=True)
            
        st.markdown("---")
        st.subheader("📊 Độ quan trọng của các đặc trưng (Feature Importance)")
        importances = rf_model.feature_importances_
        forest_importances = pd.DataFrame({"Đặc trưng": [METRIC_LABELS[f] for f in feat_cols], "Độ quan trọng": importances}).sort_values(by="Độ quan trọng", ascending=True)
        
        fig_imp = px.bar(forest_importances, x="Độ quan trọng", y="Đặc trưng", orientation="h",
                         title="Mức độ ảnh hưởng đến việc phân loại Control vs Test",
                         template="plotly_dark", color="Độ quan trọng",
                         color_continuous_scale="Viridis")
        st.plotly_chart(fig_imp, use_container_width=True)
        
    with ml_tab2:
        st.subheader("🔮 Trực quan hóa & Dự báo tương tác (Interactive Prediction)")
        st.markdown("Sử dụng các mô hình học máy đã huấn luyện để dự báo hiệu suất quảng cáo thời gian thực.")
        
        pred_mode = st.radio("Chọn mục tiêu dự báo:", ["🔮 Dự báo Lượng đơn hàng (Predict Purchases)", "🤖 Phân loại Nhóm chiến dịch (Predict Campaign Type)"], key="predict_mode_radio")
        
        if pred_mode == "🔮 Dự báo Lượng đơn hàng (Predict Purchases)":
            st.markdown("#### Mô hình hồi quy dự báo đơn hàng (Random Forest Regressor)")
            st.markdown("Điền các chỉ số chi phí và tương tác để dự đoán lượng đơn hàng (`purchase`) sẽ đạt được:")
            
            # Train a Random Forest Regressor on spend, clicks, add_to_cart
            reg_features = ['spend_usd', 'website_clicks', 'add_to_cart']
            X_reg = df[reg_features]
            y_reg = df['purchase']
            reg_model = RandomForestRegressor(n_estimators=100, random_state=42)
            reg_model.fit(X_reg, y_reg)
            
            # Input controls
            col_in1, col_in2, col_in3 = st.columns(3)
            with col_in1:
                in_spend = st.slider("Chi phí quảng cáo ngày (Spend USD):", 
                                     float(df['spend_usd'].min()), float(df['spend_usd'].max()), float(df['spend_usd'].mean()), key="in_spend_reg")
            with col_in2:
                in_clicks = st.slider("Lượt clicks ngày (Clicks):", 
                                      float(df['website_clicks'].min()), float(df['website_clicks'].max()), float(df['website_clicks'].mean()), key="in_clicks_reg")
            with col_in3:
                in_cart = st.slider("Lượt thêm giỏ hàng ngày (Add to Cart):", 
                                    float(df['add_to_cart'].min()), float(df['add_to_cart'].max()), float(df['add_to_cart'].mean()), key="in_cart_reg")
            
            # Execute prediction
            pred_val = reg_model.predict([[in_spend, in_clicks, in_cart]])[0]
            
            # Display Result
            st.markdown(f"""
            <div class="prediction-box">
                <h3 style="color: #4f46e5; margin: 0;">🔮 Kết quả dự báo số đơn hàng:</h3>
                <h1 style="color: #ffffff; font-size: 3.5rem; margin: 15px 0;">{pred_val:.2f} <span style="font-size: 1.5rem; color: #9ca3af; font-weight: 500;">đơn hàng</span></h1>
                <p style="color: #9ca3af; margin: 0; font-size: 0.9rem;">Dự đoán được xây dựng dựa trên dữ liệu lịch sử vận hành của 59 ngày chiến dịch (Control & Test).</p>
            </div>
            """, unsafe_allow_html=True)
            
        else:
            st.markdown("#### Mô hình phân loại nhóm chiến dịch (Random Forest Classifier)")
            st.markdown("Nhập các số liệu tương tác ngày để kiểm tra xem cấu trúc dữ liệu này phản ánh hành vi phân phối của **Bidding tự động** hay **Bidding truyền thống**:")
            
            col_cl1, col_cl2, col_cl3 = st.columns(3)
            with col_cl1:
                p_spend = st.number_input("Chi phí ngày (Spend USD):", float(df['spend_usd'].min()), float(df['spend_usd'].max()), float(df['spend_usd'].mean()), key="p_spend_clf")
                p_imp = st.number_input("Lượt hiển thị (Impressions):", float(df['impressions'].min()), float(df['impressions'].max()), float(df['impressions'].mean()), key="p_imp_clf")
            with col_cl2:
                p_reach = st.number_input("Số lượng tiếp cận (Reach):", float(df['reach'].min()), float(df['reach'].max()), float(df['reach'].mean()), key="p_reach_clf")
                p_clicks = st.number_input("Số lượt click website (Clicks):", float(df['website_clicks'].min()), float(df['website_clicks'].max()), float(df['website_clicks'].mean()), key="p_clicks_clf")
            with col_cl3:
                p_search = st.number_input("Số lượt tìm kiếm (Searches):", float(df['searches'].min()), float(df['searches'].max()), float(df['searches'].mean()), key="p_search_clf")
                p_view = st.number_input("Số lượt xem sản phẩm (View Content):", float(df['view_content'].min()), float(df['view_content'].max()), float(df['view_content'].mean()), key="p_view_clf")
                
            p_cart = st.slider("Lượt thêm vào giỏ hàng (Add to Cart):", float(df['add_to_cart'].min()), float(df['add_to_cart'].max()), float(df['add_to_cart'].mean()), key="p_cart_clf")
            
            # Predict
            features_input = [[p_spend, p_imp, p_reach, p_clicks, p_search, p_view, p_cart]]
            pred_class = rf_model.predict(features_input)[0]
            pred_proba = rf_model.predict_proba(features_input)[0]
            
            class_label = "Test (Bidding tự động)" if pred_class == 1 else "Control (Bidding truyền thống)"
            class_color = "#ff6f43" if pred_class == 1 else "#3b82f6"
            confidence = pred_proba[pred_class] * 100
            
            st.markdown(f"""
            <div class="prediction-box" style="border-color: {class_color};">
                <h3 style="color: {class_color}; margin: 0;">🤖 Nhóm chiến dịch được phân loại:</h3>
                <h1 style="color: #ffffff; font-size: 2.8rem; margin: 15px 0;">{class_label}</h1>
                <h4 style="color: #9ca3af; margin: 0; font-weight: 500;">Độ tin cậy của mô hình: <span style="color: #ffffff; font-weight: 700;">{confidence:.1f}%</span></h4>
            </div>
            """, unsafe_allow_html=True)

elif navigation == "⚡ Phân tích Lực lượng (Power Analysis)":
    st.header("⚡ Phân tích Lực lượng thống kê (Power Analysis)")
    st.markdown("Xác định cỡ mẫu cần thiết để phát hiện sự khác biệt có ý nghĩa thống kê giữa hai nhóm")
    
    # Standard statistics solver
    power_analysis = TTestIndPower()
    
    # Interactive Metric Selection
    power_metric = st.selectbox(
        "Chọn chỉ số để phân tích lực lượng:",
        ["purchase", "spend_usd", "website_clicks", "impressions"],
        format_func=lambda x: METRIC_LABELS[x],
        key="power_metric_sel"
    )
    
    # Calculate observed effect size
    c_vals = control_df[power_metric].values
    t_vals = test_df[power_metric].values
    mean_c, mean_t = c_vals.mean(), t_vals.mean()
    var_c, var_t = c_vals.var(ddof=1), t_vals.var(ddof=1)
    n_c, n_t = len(c_vals), len(t_vals)
    pooled_std = np.sqrt(((n_c - 1)*var_c + (n_t - 1)*var_t) / (n_c + n_t - 2))
    
    # Calculate observed cohen's d
    if pooled_std > 0:
        observed_d = (mean_t - mean_c) / pooled_std
    else:
        observed_d = 0.0
        
    abs_d = abs(observed_d)
    
    st.subheader("Cỡ mẫu cần thiết (Sample Size Calculator)")
    
    col_p1, col_p2 = st.columns([1, 2])
    
    with col_p1:
        # Inputs
        effect_size = st.slider("Effect Size (Cohen's d):", min_value=0.01, max_value=1.0, value=max(0.02, round(abs_d, 4)), step=0.01, format="%.2f")
        alpha_input = st.slider("Mức ý nghĩa (Alpha):", min_value=0.01, max_value=0.20, value=0.05, step=0.01)
        power_input = st.slider("Lực lượng thống kê (Power):", min_value=0.50, max_value=0.99, value=0.80, step=0.05)
        
    with col_p2:
        try:
            required_n = power_analysis.solve_power(
                effect_size=effect_size,
                alpha=alpha_input,
                power=power_input,
                alternative='two-sided'
            )
            required_n_val = int(np.ceil(required_n))
            
            st.metric(label="Cỡ mẫu yêu cầu mỗi nhóm (Required N per group):", value=f"{required_n_val:,} ngày")
            
            st.markdown(f"**Cỡ mẫu thực tế hiện tại:**")
            st.markdown(f"- Nhóm Control: `{n_c}` ngày")
            st.markdown(f"- Nhóm Test: `{n_t}` ngày")
            
            if n_c >= required_n_val and n_t >= required_n_val:
                st.success("✅ **ĐỦ CỠ MẪU:** Cỡ mẫu hiện tại đã đủ lớn để phát hiện effect size mong muốn với độ tin cậy được thiết lập.")
            else:
                st.error("❌ **THIẾU CỠ MẪU:** Cỡ mẫu hiện tại quá nhỏ so với yêu cầu. Kết quả kiểm định có thể có độ tin cậy thấp (lỗi Type II cao).")
        except Exception as e:
            st.error(f"Lỗi tính toán lực lượng thống kê: {e}")
            
    st.markdown("---")
    st.subheader("💡 Phân tích sâu về cỡ mẫu")
    
    # Custom message based on selection
    if power_metric == "purchase":
        st.info(f"""
        - **Effect size thực tế (Cohen's d) của lượng đơn hàng (purchase) là `{observed_d:.4f}` (rất nhỏ).**
        - Để phát hiện một sự khác biệt vô cùng nhỏ như vậy ở mức $\\alpha = 0.05$ và lực lượng $0.80$, ta sẽ cần tới **{int(np.ceil(power_analysis.solve_power(effect_size=abs_d, alpha=0.05, power=0.80, alternative='two-sided'))):,} ngày** chạy chiến dịch cho mỗi nhóm! Điều này là không khả thi trên thực tế.
        - Do đó, nếu doanh nghiệp muốn triển khai thử nghiệm mới, họ cần nhắm tới các thay đổi đột phá tạo ra effect size lớn hơn (Cohen's d từ **0.2** trở lên - cần khoảng **393 ngày** hoặc tối ưu phễu chuyển đổi để phát hiện thay đổi rõ ràng hơn).
        """)
    else:
        try:
            theoretical_n = int(np.ceil(power_analysis.solve_power(effect_size=abs_d, alpha=0.05, power=0.80, alternative='two-sided')))
            st.info(f"""
            - **Effect size thực tế (Cohen's d) của {METRIC_LABELS[power_metric]} là `{observed_d:.4f}`.**
            - Để phát hiện chính xác kích thước hiệu ứng thực tế này ở mức ý nghĩa $\\alpha = 0.05$ và lực lượng $0.80$, ta cần cỡ mẫu tối thiểu là **{theoretical_n:,} ngày** cho mỗi nhóm.
            - Nếu cỡ mẫu thực tế (`{max(n_c, n_t)}` ngày) nhỏ hơn cỡ mẫu lý thuyết, nghĩa là kết quả kiểm định của biến số này có độ tin cậy thống kê chưa thực sự tối ưu.
            """)
        except:
            st.info("Kích thước hiệu ứng quá nhỏ để tính toán cỡ mẫu lý thuyết trong khoảng hợp lệ.")

elif navigation == "📋 Đối chiếu giả thuyết":
    st.header("📋 Đối chiếu giả thuyết & Khuyến nghị Kinh doanh")
    st.markdown("Tổng kết kết quả kiểm định A/B test thực tế đối chiếu với các giả thuyết đã đề ra")
    
    # Hypothesis 1
    st.error("❌ **1. Giả thuyết về số lượng đơn hàng (Purchases - KPI chính)**")
    st.markdown("""
    - **Thiết lập:** $H_0: \\mu_{C, purchase} = \\mu_{T, purchase}$ vs $H_1: \\mu_{C, purchase} \\neq \\mu_{T, purchase}$
    - **Kết quả kiểm định:** Welch's t-test $p = 0.9449 \\ge 0.05$. Thất bại bác bỏ H₀.
    - **Kết luận:** Chiến dịch Test mới (bidding tự động) KHÔNG làm thay đổi số lượng đơn hàng trung bình ngày một cách có ý nghĩa thống kê.
    """)
    
    # Hypothesis 2
    st.success("✅ **2. Giả thuyết về chi phí quảng cáo (Daily Spend)**")
    st.markdown("""
    - **Thiết lập:** $H_0: \\mu_{C, spend} = \\mu_{T, spend}$ vs $H_1: \\mu_{C, spend} \\neq \\mu_{T, spend}$
    - **Kết quả kiểm định:** Welch's t-test $p = 0.0115 < 0.05$. Bác bỏ H₀, chấp nhận H₁.
    - **Kết luận:** Chi phí trung bình ngày của nhóm Test cao hơn nhóm Control một cách có hệ thống (tăng khoảng 11.24%).
    """)
    
    # Hypothesis 3
    st.error("❌ **3. Giả thuyết về lượt click website (Clicks)**")
    st.markdown("""
    - **Thiết lập:** Welch's t-test $p = 0.8927 \\ge 0.05$. Thất bại bác bỏ H₀.
    - **Kết luận:** Tăng ngân sách ở nhóm Test không làm tăng lượng click website trung bình ngày có ý nghĩa thống kê.
    """)
    
    st.markdown("---")
    st.subheader("💼 Quyết định Kinh doanh (Decision Framework)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<h4 style='color:#ef4444;'><i class='fa-solid fa-ban'></i> KHÔNG triển khai rộng rãi chiến dịch Test</h4>", unsafe_allow_html=True)
        st.write("""
        Chiến dịch Test không mang lại nhiều đơn hàng hơn nhưng lại tiêu tốn nhiều ngân sách hơn (+11.24%). 
        Điều này làm tăng chi phí có được một đơn hàng (CPA) từ **$4.41** (Control) lên **$4.92** (Test) - tăng **11.5%** chi phí. 
        Nếu triển khai toàn bộ, ROI tổng thể sẽ sụt giảm.
        """)
        
    with col2:
        st.markdown("<h4 style='color:#f59e0b;'><i class='fa-solid fa-hourglass-half'></i> Tiếp tục thử nghiệm (Kéo dài thời gian test)</h4>", unsafe_allow_html=True)
        st.write("""
        Phân tích lực lượng thống kê (Power Analysis) cho thấy với cỡ mẫu hiện tại (~30 ngày/nhóm), statistical power đạt được rất thấp do kích thước hiệu ứng (effect size) quá nhỏ. 
        Nếu doanh nghiệp tin rằng có sự khác biệt tiềm ẩn, cần chạy kiểm định dài hơn (ví dụ: 60 ngày) để tăng cỡ mẫu, giúp phát hiện hiệu ứng nhỏ này ở độ tin cậy mong muốn.
        """)
