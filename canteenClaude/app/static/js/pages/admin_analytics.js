// Using 'htmx:afterSwap' is generally safer than 'htmx:load' for initializing plugins
document.body.addEventListener('htmx:afterSwap', function(event) {
    
    const chartDiv = document.getElementById('revenueChart');
    
    // 1. Guard Clause: Check if it exists, has data, AND hasn't been rendered yet
    if (chartDiv && chartDiv.dataset.values && !chartDiv.dataset.rendered) {
        
        // 2. Mark this div as rendered so subsequent event bubbles ignore it
        chartDiv.dataset.rendered = "true";
        
        // 3. Wipe the div completely clean of any ghost SVGs before drawing
        chartDiv.innerHTML = '';
        
        const labels = JSON.parse(chartDiv.dataset.labels);
        const values = JSON.parse(chartDiv.dataset.values);
        
        const rootStyles = getComputedStyle(document.documentElement);
        const chartPrimary = rootStyles.getPropertyValue('--bs-primary').trim() || '#C86B53';
        const chartText = rootStyles.getPropertyValue('--bs-secondary-color').trim() || '#7C736A';
        const chartGrid = rootStyles.getPropertyValue('--bs-border-color').trim() || '#E2DACF';
        
        const options = {
            series: [{ name: 'Revenue', data: values }],
            chart: { 
                type: 'bar', 
                height: 250, 
                toolbar: { show: false },
                fontFamily: 'Plus Jakarta Sans, sans-serif'
            },
            colors: [chartPrimary],
            plotOptions: { bar: { borderRadius: 4, columnWidth: '40%' } },
            dataLabels: { enabled: false },
            xaxis: { 
                categories: labels,
                axisBorder: { show: false },
                axisTicks: { show: false },
                labels: { style: { colors: chartText } }
            },
            yaxis: {
                labels: { 
                    formatter: (value) => "$" + value,
                    style: { colors: chartText }
                }
            },
            grid: { 
                borderColor: chartGrid, 
                strokeDashArray: 4 
            }
        };

        const chart = new ApexCharts(chartDiv, options);
        chart.render();
    }

    const trafficChartDiv = document.getElementById('trafficChart');

    if (trafficChartDiv && trafficChartDiv.dataset.values && !trafficChartDiv.dataset.rendered) {
        trafficChartDiv.dataset.rendered = "true";
        trafficChartDiv.innerHTML = '';

        const trafficLabels = JSON.parse(trafficChartDiv.dataset.labels);
        const trafficValues = JSON.parse(trafficChartDiv.dataset.values);

        const rootStyles = getComputedStyle(document.documentElement);
        const chartPrimary = rootStyles.getPropertyValue('--bs-primary').trim() || '#C86B53';
        const chartText = rootStyles.getPropertyValue('--bs-secondary-color').trim() || '#7C736A';
        const chartGrid = rootStyles.getPropertyValue('--bs-border-color').trim() || '#E2DACF';

        const trafficOptions = {
            series: [{ name: 'Traffic', data: trafficValues }],
            chart: {
                type: 'line',
                height: 250,
                toolbar: { show: false },
                fontFamily: 'Plus Jakarta Sans, sans-serif'
            },
            colors: [chartPrimary],
            stroke: { curve: 'smooth', width: 3 },
            markers: { size: 4 },
            dataLabels: { enabled: false },
            xaxis: {
                categories: trafficLabels,
                axisBorder: { show: false },
                axisTicks: { show: false },
                labels: { style: { colors: chartText } }
            },
            yaxis: {
                labels: { style: { colors: chartText } }
            },
            grid: { borderColor: chartGrid, strokeDashArray: 4 }
        };

        const trafficChart = new ApexCharts(trafficChartDiv, trafficOptions);
        trafficChart.render();
    }
    
});