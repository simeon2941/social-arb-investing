document.addEventListener('DOMContentLoaded', () => {

    // State
    let signals = [];
    let currentFilter = 'all';

    // DOM Elements
    const container = document.getElementById('signal-container');
    const searchInput = document.getElementById('search-input');
    const filterBtns = document.querySelectorAll('.filter-btn');
    const modal = document.getElementById('source-modal');
    const closeModal = document.getElementById('close-modal');

    // Metrics
    const elTotal = document.getElementById('total-signals');
    const elBlind = document.getElementById('blind-spots');
    const elSent = document.getElementById('global-sentiment');

    // Fetch Data
    fetch('data.json')
        .then(res => res.json())
        .then(data => {
            // Check if data has metadata wrapper
            if (data.metadata && data.signals) {
                signals = data.signals;
                if (data.metadata.last_scan) {
                    document.getElementById('last-updated').textContent = data.metadata.last_scan;
                }
            } else {
                // Fallback for old format
                signals = data;
            }
            updateMetrics();
            render();
        })
        .catch(err => console.error("Error loading data:", err));

    // Event Listeners
    searchInput.addEventListener('input', render);

    filterBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            filterBtns.forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            currentFilter = e.target.dataset.filter;
            render();
        });
    });

    closeModal.addEventListener('click', () => {
        modal.classList.remove('active');
    });

    // Functions
    function updateMetrics() {
        elTotal.textContent = signals.length;
        const blindCount = signals.filter(s => s.blind_spot).length;
        elBlind.textContent = blindCount;

        const avgS = signals.reduce((acc, s) => acc + s.avg_sentiment, 0) / (signals.length || 1);
        elSent.textContent = avgS.toFixed(3);
    }

    function render() {
        container.innerHTML = '';

        const term = searchInput.value.toLowerCase();

        const filtered = signals.filter(s => {
            const matchesSearch = s.ticker.toLowerCase().includes(term);

            if (!matchesSearch) return false;

            if (currentFilter === 'high-velocity') return s.velocity > 0;
            if (currentFilter === 'blind-spot') return s.blind_spot;

            return true;
        });

        filtered.forEach(signal => {
            const card = document.createElement('div');
            card.className = 'card';
            card.onclick = () => openModal(signal);

            const sentimentColor = signal.avg_sentiment > 0.05 ? 'var(--accent-success)' :
                signal.avg_sentiment < -0.05 ? 'var(--accent-danger)' : '#aaa';

            card.innerHTML = `
                <div class="card-header">
                    <div class="ticker">${signal.ticker}</div>
                    <div class="sentiment-badge" style="color: ${sentimentColor}">
                        ${signal.avg_sentiment.toFixed(2)}
                    </div>
                </div>
                
                <div class="card-price">
                    ${signal.current_price ? '$' + signal.current_price.toFixed(2) : ''}
                </div>

                <div class="card-stats">
                    <div class="stat">
                        <span class="stat-label">STRENGTH</span>
                        <span class="stat-val">${signal.signal_strength}</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">TREND RATIO</span>
                        <span class="stat-val" style="color: ${signal.trend_sentiment > 1.5 ? 'var(--accent-success)' : '#888'}">
                            ${signal.trend_sentiment ? signal.trend_sentiment.toFixed(1) : '-'}
                        </span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">SOURCES</span>
                        <span class="stat-val">${signal.sources.length}</span>
                    </div>
                </div>
            `;
            container.appendChild(card);
        });
    }

    let chartInstance = null;

    function openModal(signal) {
        document.getElementById('modal-ticker').textContent = signal.ticker;
        modal.classList.add('active');

        // Render Sources
        const list = document.getElementById('source-list');
        list.innerHTML = '';

        // Use details.sources if available for raw strings, or the summary sources
        const sourcesRaw = signal.details && signal.details.sources ? signal.details.sources : signal.sources;

        sourcesRaw.forEach(src => {
            const li = document.createElement('li');
            li.className = 'source-item';

            // Try to parse platform
            let platform = "UNKNOWN";
            let link = "#";

            if (typeof src === 'string') {
                if (src.includes('Reddit')) platform = 'REDDIT';
                if (src.includes('TikTok')) platform = 'TIKTOK';
                if (src.includes('Twitter')) platform = 'TWITTER';

                // If it's a URL-like string
                if (src.startsWith('http')) link = src;
            }

            let contentHtml = `<span class="source-platform">${platform}</span>`;

            if (link !== "#") {
                contentHtml += `<a href="${link}" target="_blank" class="source-text link">${src}</a>`;
            } else {
                contentHtml += `<span class="source-text">${src}</span>`;
            }

            li.innerHTML = contentHtml;
            list.appendChild(li);
        });

        // Chart
        const ctx = document.getElementById('modal-chart').getContext('2d');
        if (chartInstance) chartInstance.destroy();

        chartInstance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Sentiment', 'Velocity', 'Strength'],
                datasets: [{
                    label: 'Metrics',
                    data: [signal.avg_sentiment, signal.velocity, signal.signal_strength],
                    backgroundColor: [
                        'rgba(0, 243, 255, 0.5)',
                        'rgba(255, 0, 255, 0.5)',
                        'rgba(0, 255, 157, 0.5)'
                    ],
                    borderColor: [
                        'rgba(0, 243, 255, 1)',
                        'rgba(255, 0, 255, 1)',
                        'rgba(0, 255, 157, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: 'rgba(255,255,255,0.1)' }
                    },
                    x: {
                        grid: { color: 'rgba(255,255,255,0.1)' }
                    }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });
    }
});
