// Marketing A/B Testing Dashboard - Interactive App Logic

// Check if CAMPAIGN_DATA is loaded
if (typeof CAMPAIGN_DATA === 'undefined') {
    console.error("CAMPAIGN_DATA is not defined. Please ensure data.js is loaded first.");
}

// Global Chart variables
let timeSeriesChart = null;
let boxplotChart = null;
let scatterChart = null;
let funnelChart = null;
let bootstrapMeansChart = null;
let bootstrapDiffChart = null;

// -------------------------------------------------------------
// 1. Navigation Controller
// -------------------------------------------------------------
document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', function(e) {
        e.preventDefault();
        
        // Remove active class from all nav items
        document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));
        
        // Add active class to clicked item
        this.classList.add('active');
        
        // Hide all sections
        document.querySelectorAll('.content-section').forEach(sec => sec.classList.remove('active'));
        
        // Show target section
        const targetId = this.getAttribute('href').substring(1);
        document.getElementById(targetId).classList.add('active');
        
        // Scroll target section into view if layout requires
        document.querySelector('.main-content').scrollTop = 0;
        
        // Render charts when switching tabs to ensure responsive width calculates correctly
        setTimeout(() => {
            window.dispatchEvent(new Event('resize'));
        }, 50);
    });
});

// -------------------------------------------------------------
// 2. Data Processing & Initialization
// -------------------------------------------------------------
const controlGroup = CAMPAIGN_DATA.filter(d => d.group === 'control');
const testGroup = CAMPAIGN_DATA.filter(d => d.group === 'test');

// Sort groups by date
controlGroup.sort((a, b) => new Date(a.date) - new Date(b.date));
testGroup.sort((a, b) => new Date(a.date) - new Date(b.date));

function initDashboard() {
    // Populate overall KPI values in dashboard overview cards
    populateKPIs();
    
    // Create Time-Series trends charts
    updateTimeSeriesChart();
    
    // Create Boxplot replacement (Comparative histogram of distributions)
    updateDistributionChart();
    
    // Create Scatter plot for Spend vs Purchases
    updateScatterChart();
    
    // Create Funnel charts and tables
    updateFunnelChartAndTable();
    
    // Run initial statistical t-test
    runStatisticalTest();
}

function populateKPIs() {
    // Chi phí Spend
    const cSpend = getMean(controlGroup, 'spend_usd');
    const tSpend = getMean(testGroup, 'spend_usd');
    document.getElementById('overview-c-spend').innerText = `$${formatNumber(cSpend, 0)}`;
    document.getElementById('overview-t-spend').innerText = `$${formatNumber(tSpend, 0)}`;
    
    // Lượt hiển thị Impressions
    const cImp = getMean(controlGroup, 'impressions');
    const tImp = getMean(testGroup, 'impressions');
    document.getElementById('overview-c-impressions').innerText = formatNumber(cImp, 0);
    document.getElementById('overview-t-impressions').innerText = formatNumber(tImp, 0);
    
    // Clicks
    const cClicks = getMean(controlGroup, 'website_clicks');
    const tClicks = getMean(testGroup, 'website_clicks');
    document.getElementById('overview-c-clicks').innerText = formatNumber(cClicks, 0);
    document.getElementById('overview-t-clicks').innerText = formatNumber(tClicks, 0);
    
    // Purchases
    const cPurchase = getMean(controlGroup, 'purchase');
    const tPurchase = getMean(testGroup, 'purchase');
    document.getElementById('overview-c-purchase').innerText = formatNumber(cPurchase, 1);
    document.getElementById('overview-t-purchase').innerText = formatNumber(tPurchase, 1);
}

// -------------------------------------------------------------
// 3. Chart Creators (Chart.js)
// -------------------------------------------------------------

// Metric select handler
document.getElementById('metric-select').addEventListener('change', () => {
    updateTimeSeriesChart();
    updateDistributionChart();
});

// A. Time-Series Daily Trends Chart
function updateTimeSeriesChart() {
    const metric = document.getElementById('metric-select').value;
    const ctx = document.getElementById('timeSeriesChart').getContext('2d');
    
    let controlData, testData;
    let label = '';
    
    if (metric === 'ctr') {
        controlData = controlGroup.map(d => (d.website_clicks / d.impressions) * 100);
        testData = testGroup.map(d => (d.website_clicks / d.impressions) * 100);
        label = 'Tỷ lệ Click (CTR %)';
    } else {
        controlData = controlGroup.map(d => d[metric]);
        testData = testGroup.map(d => d[metric]);
        label = getMetricLabel(metric);
    }
    
    const dates = controlGroup.map(d => formatDateString(d.date));
    
    if (timeSeriesChart) timeSeriesChart.destroy();
    
    timeSeriesChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [
                {
                    label: 'Control (Nhóm đối chứng)',
                    data: controlData,
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.05)',
                    tension: 0.2,
                    fill: true,
                    pointRadius: 4,
                    pointHoverRadius: 6
                },
                {
                    label: 'Test (Nhóm thử nghiệm)',
                    data: testData,
                    borderColor: '#ff6f43',
                    backgroundColor: 'rgba(255, 111, 67, 0.05)',
                    tension: 0.2,
                    fill: true,
                    pointRadius: 4,
                    pointHoverRadius: 6
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: '#e5e7eb', font: { family: 'Inter' } }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.03)' },
                    ticks: { color: '#9ca3af', font: { family: 'Inter' }, maxRotation: 45 }
                },
                y: {
                    grid: { color: 'rgba(255, 255, 255, 0.03)' },
                    ticks: { color: '#9ca3af', font: { family: 'Inter' } },
                    title: { display: true, text: label, color: '#e5e7eb' }
                }
            }
        }
    });
}

// B. Data Distribution Chart (Histogram comparison)
function updateDistributionChart() {
    const metric = document.getElementById('metric-select').value;
    const ctx = document.getElementById('boxplotChart').getContext('2d');
    
    let controlVals, testVals;
    if (metric === 'ctr') {
        controlVals = controlGroup.map(d => (d.website_clicks / d.impressions) * 100);
        testVals = testGroup.map(d => (d.website_clicks / d.impressions) * 100);
    } else {
        controlVals = controlGroup.map(d => d[metric]);
        testVals = testGroup.map(d => d[metric]);
    }
    
    // Create bins
    const minVal = Math.min(...controlVals, ...testVals);
    const maxVal = Math.max(...controlVals, ...testVals);
    const numBins = 8;
    const binWidth = (maxVal - minVal) / numBins;
    
    const labels = [];
    const controlFreqs = Array(numBins).fill(0);
    const testFreqs = Array(numBins).fill(0);
    
    for (let i = 0; i < numBins; i++) {
        const binStart = minVal + i * binWidth;
        const binEnd = binStart + binWidth;
        labels.push(`${formatNumber(binStart, 1)} - ${formatNumber(binEnd, 1)}`);
        
        controlVals.forEach(v => {
            if (v >= binStart && (i === numBins - 1 ? v <= binEnd : v < binEnd)) controlFreqs[i]++;
        });
        testVals.forEach(v => {
            if (v >= binStart && (i === numBins - 1 ? v <= binEnd : v < binEnd)) testFreqs[i]++;
        });
    }
    
    if (boxplotChart) boxplotChart.destroy();
    
    boxplotChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Control (Tần suất)',
                    data: controlFreqs,
                    backgroundColor: 'rgba(59, 130, 246, 0.65)',
                    borderColor: '#3b82f6',
                    borderWidth: 1
                },
                {
                    label: 'Test (Tần suất)',
                    data: testFreqs,
                    backgroundColor: 'rgba(255, 111, 67, 0.65)',
                    borderColor: '#ff6f43',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { labels: { color: '#e5e7eb', font: { family: 'Inter' } } }
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { color: '#9ca3af', font: { family: 'Inter', size: 9 } }
                },
                y: {
                    grid: { color: 'rgba(255, 255, 255, 0.03)' },
                    ticks: { color: '#9ca3af', precision: 0 }
                }
            }
        }
    });
}

// C. Scatter Spend vs Purchase Chart
function updateScatterChart() {
    const ctx = document.getElementById('scatterChart').getContext('2d');
    
    const controlPoints = controlGroup.map(d => ({ x: d.spend_usd, y: d.purchase }));
    const testPoints = testGroup.map(d => ({ x: d.spend_usd, y: d.purchase }));
    
    if (scatterChart) scatterChart.destroy();
    
    scatterChart = new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [
                {
                    label: 'Control',
                    data: controlPoints,
                    backgroundColor: '#3b82f6',
                    borderColor: 'rgba(59, 130, 246, 0.5)',
                    pointRadius: 5
                },
                {
                    label: 'Test',
                    data: testPoints,
                    backgroundColor: '#ff6f43',
                    borderColor: 'rgba(255, 111, 67, 0.5)',
                    pointRadius: 5
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { labels: { color: '#e5e7eb' } }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.03)' },
                    ticks: { color: '#9ca3af' },
                    title: { display: true, text: 'Chi phí quảng cáo (USD)', color: '#e5e7eb' }
                },
                y: {
                    grid: { color: 'rgba(255, 255, 255, 0.03)' },
                    ticks: { color: '#9ca3af' },
                    title: { display: true, text: 'Lượt đơn hàng (Purchases)', color: '#e5e7eb' }
                }
            }
        }
    });
}

// D. Funnel Chart & Table Generator
function updateFunnelChartAndTable() {
    const funnelStages = ['impressions', 'website_clicks', 'searches', 'view_content', 'add_to_cart', 'purchase'];
    const labels = ['Lượt hiển thị (Impressions)', 'Click Website (Clicks)', 'Tìm kiếm (Searches)', 'Xem nội dung (Views)', 'Thêm vào giỏ (Carts)', 'Đơn hàng (Purchases)'];
    
    const controlMeans = funnelStages.map(s => getMean(controlGroup, s));
    const testMeans = funnelStages.map(s => getMean(testGroup, s));
    
    // Calculate cumulative conversion rates relative to impressions
    const controlCum = controlMeans.map(v => (v / controlMeans[0]) * 100);
    const testCum = testMeans.map(v => (v / testMeans[0]) * 100);
    
    // Render Horizontal log chart
    const ctx = document.getElementById('funnelChart').getContext('2d');
    
    if (funnelChart) funnelChart.destroy();
    
    funnelChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Control (Lũy kế %)',
                    data: controlCum,
                    backgroundColor: 'rgba(59, 130, 246, 0.7)',
                    borderColor: '#3b82f6',
                    borderWidth: 1
                },
                {
                    label: 'Test (Lũy kế %)',
                    data: testCum,
                    backgroundColor: 'rgba(255, 111, 67, 0.7)',
                    borderColor: '#ff6f43',
                    borderWidth: 1
                }
            ]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { labels: { color: '#e5e7eb' } }
            },
            scales: {
                x: {
                    type: 'logarithmic',
                    grid: { color: 'rgba(255, 255, 255, 0.03)' },
                    ticks: {
                        color: '#9ca3af',
                        callback: function(value, index, ticks) {
                            return value + '%';
                        }
                    },
                    title: { display: true, text: 'Tỷ lệ chuyển đổi lũy kế (%) - Thang Log', color: '#e5e7eb' }
                },
                y: {
                    grid: { display: false },
                    ticks: { color: '#e5e7eb', font: { family: 'Outfit', weight: 500 } }
                }
            }
        }
    });
    
    // Populate Step-by-Step Conversion Table
    const tableBody = document.querySelector('#funnel-table tbody');
    tableBody.innerHTML = '';
    
    const stepNames = [
        'Impressions -> Clicks (CTR)',
        'Clicks -> Searches',
        'Searches -> View Content',
        'View Content -> Add to Cart',
        'Add to Cart -> Purchase'
    ];
    
    for (let i = 0; i < stepNames.length; i++) {
        const cRate = (controlMeans[i+1] / controlMeans[i]) * 100;
        const tRate = (testMeans[i+1] / testMeans[i]) * 100;
        const diff = tRate - cRate;
        
        let comparisonHTML = '';
        if (diff > 0.5) {
            comparisonHTML = `<span class="badge badge-success"><i class="fa-solid fa-caret-up"></i> Test tốt hơn (+${formatNumber(diff, 2)}%)</span>`;
        } else if (diff < -0.5) {
            comparisonHTML = `<span class="badge badge-danger"><i class="fa-solid fa-caret-down"></i> Control tốt hơn (${formatNumber(diff, 2)}%)</span>`;
        } else {
            comparisonHTML = `<span class="badge badge-neutral"><i class="fa-solid fa-minus"></i> Tương đồng</span>`;
        }
        
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><strong>${stepNames[i]}</strong></td>
            <td>${formatNumber(cRate, 2)}%</td>
            <td>${formatNumber(tRate, 2)}%</td>
            <td>${comparisonHTML}</td>
        `;
        tableBody.appendChild(tr);
    }
}

// -------------------------------------------------------------
// 4. Interactive Statistical Inference (Welch's t-test)
// -------------------------------------------------------------
document.getElementById('run-test-btn').addEventListener('click', runStatisticalTest);

function runStatisticalTest() {
    const metric = document.getElementById('stat-metric-select').value;
    const alpha = parseFloat(document.getElementById('alpha-select').value);
    
    const cData = controlGroup.map(d => d[metric]);
    const tData = testGroup.map(d => d[metric]);
    
    const n_c = cData.length;
    const n_t = tData.length;
    
    const mean_c = getMean(controlGroup, metric);
    const mean_t = getMean(testGroup, metric);
    const diff = mean_t - mean_c;
    
    const var_c = getVariance(cData, mean_c);
    const var_t = getVariance(tData, mean_t);
    
    // Welch's t-test calculations
    const se_diff = Math.sqrt((var_c / n_c) + (var_t / n_t));
    const t_stat = diff / se_diff;
    
    // Welch-Satterthwaite degrees of freedom
    const num = Math.pow((var_c / n_c) + (var_t / n_t), 2);
    const den = (Math.pow(var_c / n_c, 2) / (n_c - 1)) + (Math.pow(var_t / n_t, 2) / (n_t - 1));
    const df = num / den;
    
    // P-value approximation using Peizer-Pratt normal approximation
    const p_val = getWelchPValue(t_stat, df);
    
    // Cohen's d (Effect size)
    const pooled_std = Math.sqrt(((n_c - 1) * var_c + (n_t - 1) * var_t) / (n_c + n_t - 2));
    const cohen_d = diff / pooled_std;
    
    // Update Stats UI
    document.getElementById('stat-t-value').innerText = formatNumber(t_stat, 4);
    document.getElementById('stat-p-value').innerText = formatNumber(p_val, 4);
    
    const rejectBadge = document.getElementById('stat-reject-badge');
    const verdictText = document.getElementById('stat-verdict-text');
    
    if (p_val < alpha) {
        rejectBadge.className = 'badge badge-success';
        rejectBadge.innerText = 'BÁC BỎ H₀';
        
        let direction = diff > 0 ? "TĂNG" : "GIẢM";
        verdictText.innerHTML = `
            <strong>Kết luận:</strong> Với mức ý nghĩa &alpha; = ${alpha}, sự khác biệt giữa hai chiến dịch quảng cáo **CÓ ý nghĩa thống kê** (p < &alpha;).<br>
            Chiến dịch nhóm Test đã làm ${direction} trung bình của ${getMetricNameVN(metric)} một cách hệ thống.
        `;
        verdictText.style.borderLeftColor = 'var(--success)';
    } else {
        rejectBadge.className = 'badge badge-danger';
        rejectBadge.innerText = 'CHƯA ĐỦ BÁC BỎ H₀';
        
        verdictText.innerHTML = `
            <strong>Kết luận:</strong> Với mức ý nghĩa &alpha; = ${alpha}, sự khác biệt quan sát được **KHÔNG có ý nghĩa thống kê** (p &ge; &alpha;).<br>
            Sự chênh lệch về ${getMetricNameVN(metric)} hoàn toàn có thể xảy ra ngẫu nhiên và không phản ánh hiệu quả khác biệt thực sự.
        `;
        verdictText.style.borderLeftColor = 'var(--danger)';
    }
    
    // Confidence Interval of the Difference (Welch-Satterthwaite)
    const crit_t = getCriticalTValue(1 - alpha / 2, df);
    const moe = crit_t * se_diff;
    const ci_lower = diff - moe;
    const ci_upper = diff + moe;
    
    document.getElementById('stat-c-mean').innerText = formatNumber(mean_c, 2);
    document.getElementById('stat-t-mean').innerText = formatNumber(mean_t, 2);
    document.getElementById('stat-diff-mean').innerText = formatNumber(diff, 2);
    document.getElementById('stat-ci-diff').innerText = `[${formatNumber(ci_lower, 2)}, ${formatNumber(ci_upper, 2)}]`;
    
    document.getElementById('stat-cohen').innerText = formatNumber(cohen_d, 4);
    const absD = Math.abs(cohen_d);
    let interpret = '';
    let interpretClass = 'badge-neutral';
    
    if (absD < 0.2) {
        interpret = 'Negligible (Rất nhỏ)';
    } else if (absD < 0.5) {
        interpret = 'Small (Nhỏ)';
        interpretClass = 'badge-control';
    } else if (absD < 0.8) {
        interpret = 'Medium (Vừa)';
        interpretClass = 'badge-warning';
    } else {
        interpret = 'Large (Lớn)';
        interpretClass = 'badge-test';
    }
    
    const cohenBadge = document.getElementById('stat-cohen-interpret');
    cohenBadge.innerText = interpret;
    cohenBadge.className = `badge ${interpretClass}`;
}

// -------------------------------------------------------------
// 5. Bootstrap Resampling Simulator (Non-blocking Animation)
// -------------------------------------------------------------
document.getElementById('run-bootstrap-btn').addEventListener('click', runBootstrapSimulation);

function runBootstrapSimulation() {
    const btn = document.getElementById('run-bootstrap-btn');
    const progContainer = document.getElementById('progress-container');
    const fill = document.getElementById('progress-bar-fill');
    const text = document.getElementById('progress-percent');
    const resultsArea = document.getElementById('bootstrap-results-area');
    
    btn.disabled = true;
    progContainer.style.display = 'flex';
    resultsArea.style.opacity = '0.15';
    resultsArea.style.pointerEvents = 'none';
    
    const controlPurchases = controlGroup.map(d => d.purchase);
    const testPurchases = testGroup.map(d => d.purchase);
    
    const n_c = controlPurchases.length;
    const n_t = testPurchases.length;
    
    const c_means = [];
    const t_means = [];
    const diff_means = [];
    
    let currentIteration = 0;
    const totalIterations = 1000;
    const chunkSize = 50; // Iterations per frame to prevent browser locking
    
    function step() {
        for (let i = 0; i < chunkSize && currentIteration < totalIterations; i++) {
            // Draw sample with replacement for Control
            let sum_c = 0;
            for (let j = 0; j < n_c; j++) {
                const idx = Math.floor(Math.random() * n_c);
                sum_c += controlPurchases[idx];
            }
            const mean_c = sum_c / n_c;
            
            // Draw sample with replacement for Test
            let sum_t = 0;
            for (let j = 0; j < n_t; j++) {
                const idx = Math.floor(Math.random() * n_t);
                sum_t += testPurchases[idx];
            }
            const mean_t = sum_t / n_t;
            
            c_means.push(mean_c);
            t_means.push(mean_t);
            diff_means.push(mean_t - mean_c);
            
            currentIteration++;
        }
        
        // Update progress UI
        const pct = Math.min(100, Math.floor((currentIteration / totalIterations) * 100));
        fill.style.width = `${pct}%`;
        text.innerText = `${pct}%`;
        
        if (currentIteration < totalIterations) {
            requestAnimationFrame(step);
        } else {
            // Simulation finished!
            btn.disabled = false;
            setTimeout(() => {
                progContainer.style.display = 'none';
                resultsArea.style.opacity = '1';
                resultsArea.style.pointerEvents = 'auto';
                displayBootstrapResults(c_means, t_means, diff_means);
            }, 300);
        }
    }
    
    requestAnimationFrame(step);
}

function displayBootstrapResults(c_means, t_means, diff_means) {
    // 1. Calculate Percentile Confidence Intervals (95% CI: 2.5% to 97.5%)
    c_means.sort((a, b) => a - b);
    t_means.sort((a, b) => a - b);
    diff_means.sort((a, b) => a - b);
    
    const c_lower = c_means[Math.floor(c_means.length * 0.025)];
    const c_upper = c_means[Math.floor(c_means.length * 0.975)];
    
    const t_lower = t_means[Math.floor(t_means.length * 0.025)];
    const t_upper = t_means[Math.floor(t_means.length * 0.975)];
    
    const diff_lower = diff_means[Math.floor(diff_means.length * 0.025)];
    const diff_upper = diff_means[Math.floor(diff_means.length * 0.975)];
    
    document.getElementById('boot-c-ci').innerText = `[${formatNumber(c_lower, 2)}, ${formatNumber(c_upper, 2)}]`;
    document.getElementById('boot-t-ci').innerText = `[${formatNumber(t_lower, 2)}, ${formatNumber(t_upper, 2)}]`;
    document.getElementById('boot-diff-ci').innerText = `[${formatNumber(diff_lower, 2)}, ${formatNumber(diff_upper, 2)}]`;
    
    // 2. Plot Bootstrap distributions (Histograms)
    // Means Histogram
    const ctxMeans = document.getElementById('bootstrapMeansChart').getContext('2d');
    const meansHistogramData = getHistogramData(c_means, t_means, 12);
    
    if (bootstrapMeansChart) bootstrapMeansChart.destroy();
    
    bootstrapMeansChart = new Chart(ctxMeans, {
        type: 'bar',
        data: {
            labels: meansHistogramData.labels,
            datasets: [
                {
                    label: 'Control Bootstrap Means',
                    data: meansHistogramData.c_freqs,
                    backgroundColor: 'rgba(59, 130, 246, 0.55)',
                    borderColor: '#3b82f6',
                    borderWidth: 1,
                    barPercentage: 1.0,
                    categoryPercentage: 1.0
                },
                {
                    label: 'Test Bootstrap Means',
                    data: meansHistogramData.t_freqs,
                    backgroundColor: 'rgba(255, 111, 67, 0.55)',
                    borderColor: '#ff6f43',
                    borderWidth: 1,
                    barPercentage: 1.0,
                    categoryPercentage: 1.0
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { labels: { color: '#e5e7eb' } }
            },
            scales: {
                x: { ticks: { color: '#9ca3af', font: { size: 9 } } },
                y: { ticks: { display: false } }
            }
        }
    });
    
    // Difference Histogram
    const ctxDiff = document.getElementById('bootstrapDiffChart').getContext('2d');
    const diffHistogramData = getSingleHistogramData(diff_means, 15);
    
    if (bootstrapDiffChart) bootstrapDiffChart.destroy();
    
    bootstrapDiffChart = new Chart(ctxDiff, {
        type: 'bar',
        data: {
            labels: diffHistogramData.labels,
            datasets: [
                {
                    label: 'Hiệu số Mean (Test - Control)',
                    data: diffHistogramData.freqs,
                    backgroundColor: 'rgba(159, 122, 234, 0.55)',
                    borderColor: '#9f7aea',
                    borderWidth: 1,
                    barPercentage: 1.0,
                    categoryPercentage: 1.0
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { labels: { color: '#e5e7eb' } },
                // Custom annotation drawing for 0 line
                beforeDraw: function(chart) {
                    // Manual line drawing can be complex, Chart.js annotations plugin is preferred but here we keep it standard
                }
            },
            scales: {
                x: { ticks: { color: '#9ca3af', font: { size: 9 } } },
                y: { ticks: { display: false } }
            }
        }
    });
}

// -------------------------------------------------------------
// 6. Mathematical Helper Functions
// -------------------------------------------------------------

function getMean(array, key) {
    const sum = array.reduce((acc, curr) => acc + curr[key], 0);
    return sum / array.length;
}

function getVariance(data, mean) {
    const sumSqDiff = data.reduce((acc, curr) => acc + Math.pow(curr - mean, 2), 0);
    return sumSqDiff / (data.length - 1); // Sample variance
}

// Student-t Two-Tailed P-Value Peizer-Pratt Approximation
function getWelchPValue(t, df) {
    const absT = Math.abs(t);
    // Peizer-Pratt-like approximation for t-distribution CDF
    // Highly accurate for degrees of freedom >= 10
    const z = absT / Math.sqrt(1 + (absT * absT) / (2 * df)) * (1 - 1 / (4 * df));
    const normalCDF = getNormalCDF(z);
    
    // Two-tailed p-value
    return 2 * (1 - normalCDF);
}

// Standard Normal CDF (Abramowitz & Stegun polynomial approximation)
function getNormalCDF(x) {
    const p = 0.3275911;
    const a1 = 0.254829592;
    const a2 = -0.284496736;
    const a3 = 1.421413741;
    const a4 = -1.453152027;
    const a5 = 1.061405429;
    
    const sign = x < 0 ? -1 : 1;
    const absX = Math.abs(x) / Math.sqrt(2);
    
    const t = 1 / (1 + p * absX);
    const erf = 1 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * Math.exp(-absX * absX);
    
    return 0.5 * (1 + sign * erf);
}

// Inv t distribution critical value (Approximation using Cornish-Fisher expansion)
function getCriticalTValue(p, df) {
    // Standard normal critical value for p (probability)
    const z = getNormalCriticalValue(p);
    
    // Cornish-Fisher expansion of t-distribution
    const g1 = (Math.pow(z, 3) + z) / 4;
    const g2 = (5 * Math.pow(z, 5) + 16 * Math.pow(z, 3) + 3 * z) / 96;
    
    return z + g1 / df + g2 / (df * df);
}

function getNormalCriticalValue(p) {
    // High-accuracy rational approximation of InvNormalCDF
    const c0 = 2.515517;
    const c1 = 0.802853;
    const c2 = 0.010328;
    const d1 = 1.432788;
    const d2 = 0.189269;
    const d3 = 0.001308;
    
    // Tail probability
    const q = p > 0.5 ? 1 - p : p;
    const t = Math.sqrt(-2 * Math.log(q));
    
    let xp = t - (c0 + c1 * t + c2 * t * t) / (1 + d1 * t + d2 * t * t + d3 * t * t * t);
    
    if (p > 0.5) xp = -xp;
    return -xp; // Returns positive value for p > 0.5
}

// -------------------------------------------------------------
// 7. General Utility Functions
// -------------------------------------------------------------

function formatNumber(num, decimals = 2) {
    if (isNaN(num) || num === null) return "0";
    return num.toLocaleString('en-US', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    });
}

function formatDateString(dateStr) {
    // Convert 2019-08-01 to 01/08
    const date = new Date(dateStr);
    return `${String(date.getDate()).padStart(2, '0')}/${String(date.getMonth() + 1).padStart(2, '0')}`;
}

function getMetricLabel(metric) {
    const labels = {
        'purchase': 'Lượt đơn hàng (Purchases)',
        'spend_usd': 'Chi phí quảng cáo (USD)',
        'website_clicks': 'Lượt click website',
        'impressions': 'Lượt hiển thị (Impressions)',
        'ctr': 'CTR (%)'
    };
    return labels[metric] || metric;
}

function getMetricNameVN(metric) {
    const labels = {
        'purchase': 'Đơn hàng (Purchases)',
        'spend_usd': 'Chi phí (Spend)',
        'website_clicks': 'Lượt click (Clicks)',
        'impressions': 'Hiển thị (Impressions)'
    };
    return labels[metric] || metric;
}

// Calculate histogram bins for two datasets
function getHistogramData(data1, data2, numBins) {
    const all = [...data1, ...data2];
    const minVal = Math.min(...all);
    const maxVal = Math.max(...all);
    const width = (maxVal - minVal) / numBins;
    
    const labels = [];
    const c_freqs = Array(numBins).fill(0);
    const t_freqs = Array(numBins).fill(0);
    
    for (let i = 0; i < numBins; i++) {
        const start = minVal + i * width;
        const end = start + width;
        labels.push(`${formatNumber(start + width/2, 2)}`);
        
        data1.forEach(v => {
            if (v >= start && (i === numBins - 1 ? v <= end : v < end)) c_freqs[i]++;
        });
        data2.forEach(v => {
            if (v >= start && (i === numBins - 1 ? v <= end : v < end)) t_freqs[i]++;
        });
    }
    
    return { labels, c_freqs, t_freqs };
}

// Calculate histogram bins for a single dataset
function getSingleHistogramData(data, numBins) {
    const minVal = Math.min(...data);
    const maxVal = Math.max(...data);
    const width = (maxVal - minVal) / numBins;
    
    const labels = [];
    const freqs = Array(numBins).fill(0);
    
    for (let i = 0; i < numBins; i++) {
        const start = minVal + i * width;
        const end = start + width;
        labels.push(`${formatNumber(start + width/2, 2)}`);
        
        data.forEach(v => {
            if (v >= start && (i === numBins - 1 ? v <= end : v < end)) freqs[i]++;
        });
    }
    
    return { labels, freqs };
}

// Run Dashboard Initialization on DOM Load
window.addEventListener('DOMContentLoaded', initDashboard);
