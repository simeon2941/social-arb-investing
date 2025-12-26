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

                <div class="card-grid">
                    <div class="stat-item">
                        <span class="label">SIGNAL</span>
                        <span class="value">${signal.signal_strength} <span class="sub">(${signal.velocity > 0 ? '+' : ''}${signal.velocity})</span></span>
                    </div>
                    <div class="stat-item">
                        <span class="label">SOURCES</span>
                        <span class="value">${signal.sources.length}</span>
                    </div>
                    <div class="stat-item">
                        <span class="label">HYPE RATIO</span>
                        <span class="value" style="color: ${signal.trend_sentiment > 1.5 ? 'var(--accent-success)' : signal.trend_sentiment < 0.8 ? 'var(--accent-danger)' : '#888'}">
                            ${signal.trend_sentiment ? signal.trend_sentiment.toFixed(1) + 'x' : '-'}
                        </span>
                    </div>
                    <div class="stat-item">
                        <span class="label">SEARCH VOL</span>
                        <span class="value">${signal.bullish_search_vol ? signal.bullish_search_vol.toLocaleString() : '-'}</span>
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
                if (src.includes('news')) platform = 'NEWS';

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

        // Update Sentiment Battle
        const bullish = signal.bullish_search_vol || 0;
        const bearish = signal.bearish_search_vol || 0;
        const total = bullish + bearish;

        let bullPct = 50;
        let bearPct = 50;

        if (total > 0) {
            bullPct = (bullish / total) * 100;
            bearPct = (bearish / total) * 100;
        }

        const bullBar = document.getElementById('modal-bullish-bar');
        const bearBar = document.getElementById('modal-bearish-bar');

        if (bullBar && bearBar) {
            bullBar.style.width = `${bullPct}%`;
            bearBar.style.width = `${bearPct}%`;
        }

        const bullLabel = document.getElementById('modal-bull-vol');
        const bearLabel = document.getElementById('modal-bear-vol');

        if (bullLabel) bullLabel.textContent = bullish.toLocaleString();
        if (bearLabel) bearLabel.textContent = bearish.toLocaleString();


        // Inject TradingView Widget
        const container = document.getElementById('tradingview_chart');
        if (container) {
            container.innerHTML = ''; // Clear previous

            const script = document.createElement('script');
            script.src = 'https://s3.tradingview.com/tv.js';
            script.async = true;
            script.onload = () => {
                if (window.TradingView) {
                    new TradingView.widget({
                        "width": "100%",
                        "height": 400,
                        "symbol": signal.ticker,
                        "interval": "D",
                        "timezone": "Etc/UTC",
                        "theme": "dark",
                        "style": "1",
                        "locale": "en",
                        "toolbar_bg": "#f1f3f6",
                        "enable_publishing": false,
                        "allow_symbol_change": true,
                        "container_id": "tradingview_chart"
                    });
                }
            };
            container.appendChild(script);
        }
    }
});
