import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.power import TTestIndPower
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

# 1. Page Configuration
st.set_page_config(
    page_title="Marketing A/B Testing Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for premium styling
st.markdown("""
<style>
    /* Custom CSS variables & styles */
    .metric-card {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 10px;
        text-align: center;
    }
    .badge-control {
        background-color: rgba(59, 130, 246, 0.15);
        color: #3b82f6;
        padding: 4px 10px;
        border-radius: 12px;
        font-weight: bold;
    }
    .badge-test {
        background-color: rgba(255, 111, 67, 0.15);
        color: #ff6f43;
        padding: 4px 10px;
        border-radius: 12px;
        font-weight: bold;
    }
</style>
""", unsafe_allowed_html=True)

# 2. Load Cleaned Dataset
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

# 3. Sidebar Navigation
st.sidebar.image("https://img.icons8.com/clouds/100/ab-testing.png", width=70)
st.sidebar.title("A/B Testing Pulse")
st.sidebar.markdown("---")

navigation = st.sidebar.radio(
    "Danh mục phân tích:",
    [
        "🏠 Tổng quan KPI",
        "📈 Xu hướng hàng ngày",
        "🎯 Phễu chuyển đổi",
        "🧮 Kiểm định Welch t-test",
        "🔄 Bootstrap Simulator",
        "📊 Phân tích Hồi quy (Regression)",
        "🤖 Mô hình Phân loại (Classification)",
        "⚡ Phân tích Lực lượng (Power Analysis)",
        "📋 Đối chiếu giả thuyết"
    ]
)

st.sidebar.markdown("---")
st.sidebar.subheader("Thông tin chiến dịch")
st.sidebar.markdown(f"**Control (Đối chứng):** 29 ngày  \n<span class='badge-control'>Bidding truyền thống</span>", unsafe_allowed_html=True)
st.sidebar.markdown(f"**Test (Thử nghiệm):** 30 ngày  \n<span class='badge-test'>Bidding tự động</span>", unsafe_allowed_html=True)

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
""", unsafe_allowed_html=True)

# 4. Main Title
st.title("📊 Marketing A/B Testing Interactive Dashboard")
st.markdown("Hệ thống đánh giá hiệu suất quảng cáo & Kiểm định thống kê tự động (Triển khai bằng Streamlit)")
st.markdown("---")

# 5. Render Sections based on Navigation Selection

if navigation == "🏠 Tổng quan KPI":
    st.header("🏠 Tổng quan hiệu suất tổng thể")
    st.markdown("So sánh các chỉ số hiệu suất trung bình ngày giữa hai nhóm chiến dịch Control và Test")
    
    # Calculate means
    kpis = ['spend_usd', 'impressions', 'reach', 'website_clicks', 'purchase']
    c_means = control_df[kpis].mean()
    t_means = test_df[kpis].mean()
    pct_diffs = ((t_means - c_means) / c_means) * 100
    
    # Grid columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Chi phí quảng cáo trung bình (Daily Spend)",
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
            delta_color="off" # Purchases difference is tiny and negative
        )
        
    st.markdown("---")
    st.subheader("💡 Nhận xét nhanh (Quick Insights)")
    st.info("""
    - **Hiệu quả chi phí thấp hơn ở nhóm Test:** Nhóm **Test** có chi phí trung bình hàng ngày tăng **11.24%** so với nhóm **Control**, nhưng số lượng đơn hàng (purchase) trung bình hàng ngày lại giảm nhẹ **-0.30%**.
    - **Cơ chế phân phối ngân sách khác nhau:** Nhóm **Control** hiển thị rộng hơn nhiều (+62.15% impressions), nhưng nhóm **Test** lại thu hút lượng clicks và searches tốt hơn tương đương với lượng ngân sách chi tiêu, cho thấy cơ chế bidding của Test hướng tới tệp đối tượng có tương tác ban đầu cao hơn.
    - **Đứt gãy chuyển đổi cuối phễu:** Dù thu hút lượt click và tìm kiếm nhiều hơn ở phần trên của phễu, nhóm **Test** lại ghi nhận tỷ lệ chuyển đổi từ thêm vào giỏ hàng sang đơn hàng (Cart-to-Purchase) sụt giảm lớn so với Control.
    """)

elif navigation == "📈 Xu hướng hàng ngày":
    st.header("📈 Xu hướng & Phân phối hàng ngày")
    st.markdown("Phân tích biến động, phân phối tần suất và mối quan hệ giữa các chỉ số marketing")
    
    # Metric Selection
    metric_options = {
        "purchase": "Lượt đơn hàng (Purchases)",
        "spend_usd": "Chi phí (Daily Spend USD)",
        "website_clicks": "Lượt click website (Clicks)",
        "impressions": "Lượt hiển thị (Impressions)"
    }
    selected_metric = st.selectbox("Chọn chỉ số trực quan:", list(metric_options.keys()), format_func=lambda x: metric_options[x])
    
    # 1. Daily Trend Plotly Line Chart
    st.subheader("Biểu đồ biến động theo ngày")
    
    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(
        x=control_df['date'], y=control_df[selected_metric],
        mode='lines+markers', name='Control',
        line=dict(color='#3b82f6', width=2),
        marker=dict(size=6)
    ))
    fig_line.add_trace(go.Scatter(
        x=test_df['date'], y=test_df[selected_metric],
        mode='lines+markers', name='Test',
        line=dict(color='#ff6f43', width=2),
        marker=dict(size=6)
    ))
    fig_line.update_layout(
        title=f"Xu hướng biến động của {metric_options[selected_metric]}",
        xaxis_title="Ngày",
        yaxis_title=metric_options[selected_metric],
        hovermode="x unified",
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
        template="plotly_dark"
    )
    st.plotly_chart(fig_line, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Phân phối dữ liệu (Boxplot)")
        fig_box = px.box(
            df, x='group', y=selected_metric, color='group',
            color_discrete_map={'control': '#3b82f6', 'test': '#ff6f43'},
            title=f"Phân phối của {metric_options[selected_metric]} giữa 2 nhóm"
        )
        fig_box.update_layout(template="plotly_dark", showlegend=False)
        st.plotly_chart(fig_box, use_container_width=True)
        
    with col2:
        st.subheader("Tương quan Chi phí vs Đơn hàng")
        fig_scatter = px.scatter(
            df, x='spend_usd', y='purchase', color='group',
            color_discrete_map={'control': '#3b82f6', 'test': '#ff6f43'},
            trendline="ols",
            title="Chi phí quảng cáo (Spend) vs Đơn hàng (Purchases)"
        )
        fig_scatter.update_layout(template="plotly_dark")
        st.plotly_chart(fig_scatter, use_container_width=True)

elif navigation == "🎯 Phễu chuyển đổi":
    st.header("🎯 Phễu chuyển đổi (Conversion Funnel)")
    st.markdown("Theo dõi tỷ lệ chuyển đổi lũy kế và so sánh hiệu suất chuyển đổi từng bước (step-by-step)")
    
    funnel_stages = ['impressions', 'website_clicks', 'searches', 'view_content', 'add_to_cart', 'purchase']
    stage_labels = ['Impressions', 'Clicks', 'Searches', 'View Content', 'Add to Cart', 'Purchase']
    
    c_means = [control_df[s].mean() for s in funnel_stages]
    t_means = [test_df[s].mean() for s in funnel_stages]
    
    # Calculate cumulative rate
    c_cum = [(v / c_means[0]) * 100 for v in c_means]
    t_cum = [(v / t_means[0]) * 100 for v in t_means]
    
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

elif navigation == "🧮 Kiểm định Welch t-test":
    st.header("🧮 Kiểm định thống kê Welch's t-test")
    st.markdown("Chạy kiểm định t-test độc lập với giả định phương sai không đồng nhất")
    
    col1, col2 = st.columns(2)
    
    with col1:
        stat_metric = st.selectbox(
            "Chọn chỉ số kiểm định:",
            ["purchase", "spend_usd", "website_clicks", "impressions"],
            format_func=lambda x: {
                "purchase": "Lượt đơn hàng (Purchases)",
                "spend_usd": "Chi phí (Daily Spend USD)",
                "website_clicks": "Lượt click website (Clicks)",
                "impressions": "Lượt hiển thị (Impressions)"
            }[x]
        )
    with col2:
        alpha = st.selectbox("Chọn mức ý nghĩa (\u03b1):", [0.01, 0.05, 0.10], index=1, format_func=lambda x: f"{x} (Độ tin cậy {(1-x)*100:.0f}%)")
        
    # Welch's t-test execution
    c_vals = control_df[stat_metric].values
    t_vals = test_df[stat_metric].values
    
    t_stat, p_val = stats.ttest_ind(c_vals, t_vals, equal_var=False)
    
    # Calculate CIs
    n_c, n_t = len(c_vals), len(t_vals)
    mean_c, mean_t = c_vals.mean(), t_vals.values.mean() if hasattr(t_vals, 'values') else t_vals.mean()
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
    
    # Show Results UI
    st.subheader("Kết quả Kiểm định Welch t-test")
    
    res_col1, res_col2 = st.columns(2)
    
    with res_col1:
        st.markdown(f"**T-Statistic:** `{t_stat:.4f}`")
        st.markdown(f"**P-Value:** `{p_val:.4f}`")
        
        if p_val < alpha:
            st.success(f"**KẾT LUẬN: BÁC BỎ H₀ (REJECT H₀)**")
            st.markdown(f"Sự khác biệt về {stat_metric} giữa hai nhóm **CÓ ý nghĩa thống kê** ở mức &alpha; = {alpha}.")
        else:
            st.error(f"**KẾT LUẬN: THẤT BẠI TRONG VIỆC BÁC BỎ H₀ (FAIL TO REJECT H₀)**")
            st.markdown(f"Sự khác biệt về {stat_metric} giữa hai nhóm **KHÔNG có ý nghĩa thống kê** ở mức &alpha; = {alpha}.")
            
    with res_col2:
        st.markdown(f"**Trung bình Control:** `{mean_c:.2f}`")
        st.markdown(f"**Trung bình Test:** `{mean_t:.2f}`")
        st.markdown(f"**Hiệu số trung bình (Test - Control):** `{mean_diff:.2f}`")
        st.markdown(f"**Khoảng tin cậy {(1-alpha)*100:.0f}% của hiệu số:** `[{ci_lower:.2f}, {ci_upper:.2f}]`")
        
        # Cohen's d interpretation
        abs_d = abs(cohen_d)
        d_interpret = "Negligible (Rất nhỏ)" if abs_d < 0.2 else ("Small (Nhỏ)" if abs_d < 0.5 else ("Medium (Vừa)" if abs_d < 0.8 else "Large (Lớn)"))
        st.markdown(f"**Cohen's d (Effect Size):** `{cohen_d:.4f}` ({d_interpret})")
        
    st.markdown("---")
    st.subheader("⚠️ Phân tích Đa cộng tuyến (VIF)")
    st.markdown("""
    Trong mô hình hồi quy đa biến dự báo `purchase`, chúng ta phát hiện sự cộng tuyến mạnh giữa **`add_to_cart` (VIF = 12.45)** và **`searches` (VIF = 9.12)**. 
    Điều này làm suy yếu sự ổn định của hệ số hồi quy đa biến và khiến việc phân biệt độc lập vai trò của hai đặc trưng này trở nên khó khăn.
    """)

elif navigation == "🔄 Bootstrap Simulator":
    st.header("🔄 Mô phỏng Tái mẫu Bootstrap (Bootstrap Simulator)")
    st.markdown("Dựng phân phối mẫu bằng cách lấy mẫu lặp lại có thay thế 1,000 lần trực tiếp trên trình duyệt")
    
    control_vals = control_df['purchase'].values
    test_vals = test_df['purchase'].values
    
    if st.button("🚀 Bắt đầu chạy mô phỏng Bootstrap (1,000 lần)"):
        # Run bootstrap loop in python
        n_c = len(control_vals)
        n_t = len(test_vals)
        
        c_boot_means = []
        t_boot_means = []
        diff_boot_means = []
        
        progress_bar = st.progress(0)
        
        for i in range(1000):
            c_sample = np.random.choice(control_vals, size=n_c, replace=True)
            t_sample = np.random.choice(test_vals, size=n_t, replace=True)
            
            c_m = c_sample.mean()
            t_m = t_sample.mean()
            
            c_boot_means.append(c_m)
            t_boot_means.append(t_m)
            diff_boot_means.append(t_m - c_m)
            
            if i % 100 == 0:
                progress_bar.progress((i + 1) / 1000)
                
        progress_bar.progress(1.0)
        
        c_boot_means = np.array(c_boot_means)
        t_boot_means = np.array(t_boot_means)
        diff_boot_means = np.array(diff_boot_means)
        
        # Calculate CIs
        c_ci = np.percentile(c_boot_means, [2.5, 97.5])
        t_ci = np.percentile(t_boot_means, [2.5, 97.5])
        diff_ci = np.percentile(diff_boot_means, [2.5, 97.5])
        
        st.subheader("Kết quả mô phỏng")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**95% Bootstrap CI cho Control Mean:** `[{c_ci[0]:.2f}, {c_ci[1]:.2f}]`")
            st.markdown(f"**95% Bootstrap CI cho Test Mean:** `[{t_ci[0]:.2f}, {t_ci[1]:.2f}]`")
            st.markdown(f"**95% Bootstrap CI cho Hiệu số trung bình:** `[{diff_ci[0]:.2f}, {diff_ci[1]:.2f}]`")
        with col2:
            st.info("""
            **Kết luận phi tham số:**
            - Phân phối bootstrap trung bình của Control và Test chồng lấp lên nhau rất lớn.
            - Khoảng tin cậy 95% của hiệu số trung bình **chứa giá trị 0**.
            - Xác nhận vững chắc rằng **không có sự khác biệt có ý nghĩa thống kê** nào ở lượng đơn hàng giữa 2 chiến dịch.
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

elif navigation == "📊 Phân tích Hồi quy (Regression)":
    st.header("📊 Phân tích Hồi quy (Regression Analysis)")
    st.markdown("Đánh giá các yếu tố ảnh hưởng đến đơn hàng (`purchase`) và kiểm tra đa cộng tuyến VIF")

    reg_tab1, reg_tab2 = st.tabs(["Hồi quy Đơn biến (Simple OLS)", "Hồi quy Đa biến (Multiple OLS) & VIF"])

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

    with reg_tab2:
        st.subheader("Hồi quy tuyến tính đa biến & Chỉ số VIF")
        st.markdown("Xây dựng mô hình OLS đa biến kết hợp nhiều đặc trưng trong phễu chuyển đổi để dự báo `purchase`.")
        
        feature_cols = ['spend_usd', 'impressions', 'reach', 'website_clicks', 'searches', 'view_content', 'add_to_cart']
        X_multi = sm.add_constant(df[feature_cols])
        model_multi = sm.OLS(df['purchase'], X_multi).fit()
        
        # Display coefficients in a clean table
        coef_df = pd.DataFrame({
            "Hệ số (Coefficient)": model_multi.params,
            "Sai số chuẩn (Std Error)": model_multi.bse,
            "T-Statistic": model_multi.tvalues,
            "P-value": model_multi.pvalues
        })
        st.markdown("**Kết quả hệ số hồi quy đa biến:**")
        st.dataframe(coef_df.style.format("{:.4f}").highlight_between(left=0, right=0.05, subset=["P-value"], color="rgba(46, 204, 113, 0.2)"))

        st.markdown(f"**R-squared ($R^2$):** `{model_multi.rsquared:.4f}` | **Adjusted $R^2$:** `{model_multi.rsquared_adj:.4f}`")
        
        # Calculate and display VIF
        X_vif = df[feature_cols]
        vif_data = pd.DataFrame()
        vif_data["Đặc trưng (Feature)"] = X_vif.columns
        vif_data["VIF"] = [variance_inflation_factor(X_vif.values, i) for i in range(len(X_vif.columns))]
        vif_data = vif_data.sort_values(by="VIF", ascending=False)
        
        st.subheader("⚠️ Đánh giá Đa cộng tuyến (Multicollinearity)")
        col_vif1, col_vif2 = st.columns([1, 1])
        with col_vif1:
            st.dataframe(vif_data.style.format({"VIF": "{:.2f}"}).highlight_between(left=5, right=100, subset=["VIF"], color="rgba(231, 76, 60, 0.2)"))
        with col_vif2:
            st.info("""
            **Giải thích chỉ số VIF:**
            - **VIF < 5:** Không xảy ra đa cộng tuyến nghiêm trọng.
            - **VIF >= 5:** Có dấu hiệu đa cộng tuyến.
            - **VIF >= 10:** Đa cộng tuyến nghiêm trọng.
            
            **Nhận xét:** Biến `add_to_cart` (VIF > 12) và `searches` (VIF > 9) có tương quan tuyến tính rất mạnh với nhau. Điều này khiến cho hệ số hồi quy đa biến của chúng có thể bị sai lệch (standard error lớn) và khó giải thích độc lập.
            """)

elif navigation == "🤖 Mô hình Phân loại (Classification)":
    st.header("🤖 Mô hình Phân loại nhóm chiến dịch (Control vs Test)")
    st.markdown("Xây dựng mô hình máy học dự đoán một ngày thuộc nhóm **Control** (Bidding truyền thống) hay **Test** (Bidding tự động) dựa trên hành vi vận hành.")
    
    st.warning("⚠️ **Tránh rò rỉ dữ liệu (Data Leakage):** Chỉ số KPI chính `purchase` đã bị loại bỏ khỏi danh sách đặc trưng đầu vào để tránh rò rỉ kết quả A/B test vào mô hình phân loại.")

    # Model Setup
    feat_cols = ['spend_usd', 'impressions', 'reach', 'website_clicks', 'searches', 'view_content', 'add_to_cart']
    X_class = df[feat_cols]
    y_class = (df['group'] == 'test').astype(int)
    
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X_class, y_class, test_size=0.25, random_state=42, stratify=y_class)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Fit models
    lr_model = LogisticRegression(random_state=42)
    lr_model.fit(X_train_scaled, y_train)
    lr_train_acc = lr_model.score(X_train_scaled, y_train) * 100
    lr_test_acc = lr_model.score(X_test_scaled, y_test) * 100
    
    rf_model = RandomForestClassifier(random_state=42, n_estimators=100, max_depth=4)
    rf_model.fit(X_train, y_train)
    rf_train_acc = rf_model.score(X_train, y_train) * 100
    rf_test_acc = rf_model.score(X_test, y_test) * 100
    
    # Metrics
    c_col1, c_col2 = st.columns(2)
    with c_col1:
        st.subheader("Logistic Regression")
        st.metric(label="Accuracy trên Train", value=f"{lr_train_acc:.1f}%")
        st.metric(label="Accuracy trên Test", value=f"{lr_test_acc:.1f}%")
    with c_col2:
        st.subheader("Random Forest Classifier")
        st.metric(label="Accuracy trên Train", value=f"{rf_train_acc:.1f}%")
        st.metric(label="Accuracy trên Test", value=f"{rf_test_acc:.1f}%")
        
    # Feature Importance plot
    st.subheader("Độ quan trọng của các đặc trưng (Random Forest Feature Importance)")
    importances = rf_model.feature_importances_
    forest_importances = pd.DataFrame({"Đặc trưng": feat_cols, "Độ quan trọng": importances}).sort_values(by="Độ quan trọng", ascending=True)
    
    fig_imp = px.bar(forest_importances, x="Độ quan trọng", y="Đặc trưng", orientation="h",
                     title="Mức độ ảnh hưởng đến việc phân lớp Control vs Test",
                     template="plotly_dark", color="Độ quan trọng",
                     color_continuous_scale="Viridis")
    st.plotly_chart(fig_imp, use_container_width=True)
    
    st.info("""
    **Ý nghĩa nghiệp vụ:**
    - Độ chính xác mô hình rất cao chứng minh hai chiến dịch **Control** và **Test** vận hành khác hẳn nhau (không phải do ngẫu nhiên).
    - Đặc trưng `reach` và `impressions` là các nhân tố chính phân biệt 2 nhóm này, phản ánh nhóm **Control** tiếp cận số đông rộng hơn, trong khi nhóm **Test** có xu hướng tập trung tương tác tốt hơn trên lượng ngân sách bỏ ra.
    """)

elif navigation == "⚡ Phân tích Lực lượng (Power Analysis)":
    st.header("⚡ Phân tích Lực lượng thống kê (Power Analysis)")
    st.markdown("Xác định cỡ mẫu cần thiết để phát hiện sự khác biệt có ý nghĩa thống kê giữa hai nhóm")
    
    # Standard statistics solver
    power_analysis = TTestIndPower()
    
    # Calculate observed effect size for purchase
    c_vals = control_df['purchase'].values
    t_vals = test_df['purchase'].values
    mean_c, mean_t = c_vals.mean(), t_vals.mean()
    var_c, var_t = c_vals.var(ddof=1), t_vals.var(ddof=1)
    n_c, n_t = len(c_vals), len(t_vals)
    pooled_std = np.sqrt(((n_c - 1)*var_c + (n_t - 1)*var_t) / (n_c + n_t - 2))
    observed_d = (mean_t - mean_c) / pooled_std
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
    st.info(f"""
    - **Effect size thực tế (Cohen's d) của lượng đơn hàng (purchase) là `{observed_d:.4f}` (rất nhỏ).**
    - Để phát hiện một sự khác biệt vô cùng nhỏ như vậy ở mức $\\alpha = 0.05$ và lực lượng $0.80$, ta sẽ cần tới **{int(np.ceil(power_analysis.solve_power(effect_size=abs_d, alpha=0.05, power=0.80, alternative='two-sided'))):,} ngày** chạy chiến dịch cho mỗi nhóm! Điều này là không khả thi trên thực tế.
    - Do đó, nếu doanh nghiệp muốn triển khai thử nghiệm mới, họ cần nhắm tới các thay đổi đột phá tạo ra effect size lớn hơn (Cohen's d từ **0.2** trở lên - cần khoảng **393 ngày** hoặc tối ưu phễu chuyển đổi để phát hiện thay đổi rõ ràng hơn).
    """)

elif navigation == "📋 Đối chiếu giả thuyết":
    st.header("📋 Đối chiếu giả thuyết & Khuyết nghị Kinh doanh")
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
        st.markdown("<h4 style='color:#ef4444;'><i class='fa-solid fa-ban'></i> KHÔNG triển khai rộng rãi chiến dịch Test</h4>", unsafe_allowed_html=True)
        st.write("""
        Chiến dịch Test không mang lại nhiều đơn hàng hơn nhưng lại tiêu tốn nhiều ngân sách hơn (+11.24%). 
        Điều này làm tăng chi phí có được một đơn hàng (CPA) từ **$4.41** (Control) lên **$4.92** (Test) - tăng **11.5%** chi phí. 
        Nếu triển khai toàn bộ, ROI tổng thể sẽ sụt giảm.
        """)
        
    with col2:
        st.markdown("<h4 style='color:#f59e0b;'><i class='fa-solid fa-hourglass-half'></i> Tiếp tục thử nghiệm (Kéo dài thời gian test)</h4>", unsafe_allowed_html=True)
        st.write("""
        Phân tích lực lượng thống kê (Power Analysis) cho thấy với cỡ mẫu hiện tại (~30 ngày/nhóm), statistical power đạt được rất thấp do kích thước hiệu ứng (effect size) quá nhỏ. 
        Nếu doanh nghiệp tin rằng có sự khác biệt tiềm ẩn, cần chạy kiểm định dài hơn (ví dụ: 60 ngày) để tăng cỡ mẫu, giúp phát hiện hiệu ứng nhỏ này ở độ tin cậy mong muốn.
        """)
