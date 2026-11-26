document.addEventListener('DOMContentLoaded', () => {
    // 1. Initialize ApexCharts Instances
    // const rushHoursChart = new ApexCharts(document.querySelector("#rushHoursChart"), {
    //     chart: { type: 'area', height: 260, toolbar: { show: false } },
    //     stroke: { curve: 'smooth', width: 2 },
    //     fill: { type: 'gradient', gradient: { shadeIntensity: 1, opacityFrom: 0.4, opacityTo: 0.05 } },
    //     colors: ['#0d6efd'],
    //     xaxis: { categories: [] },
    //     series: []
    // });

    const noDataConfig = {
        text: 'No data available for this period',
        align: 'center',
        verticalAlign: 'middle',
        style: {
            color: '#6c757d',
            fontSize: '14px',
            fontFamily: 'inherit'
        },
        yaxis: { show: false },
        grid: { show: false },
        
    };

    const rushHoursChart = new ApexCharts(document.querySelector("#rushHoursChart"), {
        chart: { type: 'area', height: 260, stacked: false, toolbar: { show: false } },
        dataLabels: { enabled: false },
        stroke: { curve: 'smooth', width: 2 },
        fill: { type: 'gradient', gradient: { shadeIntensity: 1, opacityFrom: 0.4, opacityTo: 0.05 } },
        colors: ['#0d6efd'],
        xaxis: {
            categories: [],
            tickAmount: 6, // Limits the x-axis to ~6 visible labels across the span
            labels: {
                rotate: 0, // Keeps text horizontal for cleaner reading
                hideOverlappingLabels: true, // Automatically hides labels if screen resizes smaller
                style: { fontSize: '11px' }
            }
        },
        yaxis: { min: 0 },
        series: [],
        noData: noDataConfig
    });

    const topDishesChart = new ApexCharts(document.querySelector("#topDishesChart"), {
        chart: { type: 'bar', height: 260, toolbar: { show: false } },
        plotOptions: { bar: { horizontal: true, barHeight: '50%' } },
        dataLabels: { enabled: false },
        colors: ['#198754'],
        xaxis: { categories: [] },
        series: [],
        noData: noDataConfig
    });

    const categoryChart = new ApexCharts(document.querySelector("#categoryChart"), {
        chart: { type: 'donut', height: 260 },
        colors: ['#0d6efd', '#198754', '#ffc107', '#0dcaf0', '#6c757d'],
        labels: [],
        series: [],
        legend: { position: 'bottom' },
        noData: noDataConfig
    });

    // Render empty containers initial state
    rushHoursChart.render();
    topDishesChart.render();
    categoryChart.render();

    // 2. Fetch and Render Unified Analytics Payload
    async function fetchAnalytics(range = 'today') {
        try {
            const response = await fetch(`/api/analytics?range=${range}`);
            if (!response.ok) throw new Error('Failed to load analytics payload');

            const data = await response.json();
            console.log("Fetched Analytics Data:", data);
            // A. Update KPI Text Nodes
            document.getElementById('kpi-revenue').textContent = `$${data.kpis.total_revenue.toFixed(2)}`;
            document.getElementById('kpi-revenue-trend').textContent = data.kpis.revenue_trend;
            
            document.getElementById('kpi-orders-completed').textContent = data.kpis.orders_completed;
            // document.getElementById('kpi-meals').textContent = data.kpis.meals_cooked;
            document.getElementById('kpi-orders-trend').textContent = data.kpis.orders_trend;

            document.getElementById('kpi-prep-speed').textContent = data.kpis.prep_speed;
            document.getElementById('kpi-prep-trend').textContent = data.kpis.prep_trend;

            // B. Update ApexCharts Options and Series
            rushHoursChart.updateOptions({ xaxis: { categories: data.rush_hours.categories } });
            rushHoursChart.updateSeries(data.rush_hours.series);

            console.log("Updating Top Dishes Chart with Categories:", data.top_dishes.categories);
            console.log("Updating Top Dishes Chart with Series:", data.top_dishes.series);
            topDishesChart.updateOptions({ xaxis: { categories: data.top_dishes.categories } });
            topDishesChart.updateSeries(data.top_dishes.series);

            categoryChart.updateOptions({ labels: data.categories.labels });
            categoryChart.updateSeries(data.categories.series);

            // C. Render Recent Orders Table
            const tbody = document.getElementById('recentOrdersTable');
            // if (data.recent_orders.length === 0) {
            //     tbody.innerHTML = `<tr><td colspan="6" class="text-center py-3 text-muted">No completed orders found for this range.</td></tr>`;
            // } else {
            //     tbody.innerHTML = data.recent_orders.map(order => `
            //         <tr>
            //             <td class="ps-3 fw-bold">#${order.id}</td>
            //             <td>${order.time}</td>
            //             <td><span class="badge bg-light text-dark border">${order.type}</span> ${order.table !== '-' ? 'Table ' + order.table : ''}</td>
            //             <td class="small text-muted">${order.items}</td>
            //             <td class="fw-semibold">$${order.amount.toFixed(2)}</td>
            //             <td class="pe-3"><span class="badge bg-success">Completed</span></td>
            //         </tr>
            //     `).join('');
            // }
        } catch (error) {
            console.error('Analytics Fetch Error:', error);
        }
    }

    // 3. Initial Dashboard Load (Default: Last 7 Days)
    fetchAnalytics('today');

    // 4. Dropdown Change Listener
    const rangeFilter = document.getElementById('rangeFilter');
    if (rangeFilter) {
        rangeFilter.addEventListener('change', (e) => {
            fetchAnalytics(e.target.value);
        });
    }
});