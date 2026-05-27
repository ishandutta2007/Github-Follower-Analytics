document.addEventListener('DOMContentLoaded', () => {
    const usernameInput = document.getElementById('username');
    const analyzeBtn = document.getElementById('analyze-btn');
    const resultsContainer = document.getElementById('results');
    const loader = document.getElementById('loader');
    const statusMessage = document.getElementById('status-message');
    const consoleDiv = document.getElementById('console');
    const consoleSection = document.getElementById('console-section');
    let locationChart = null;

    const lastUsername = localStorage.getItem('last_github_username');
    usernameInput.value = lastUsername || 'ishandutta2007';

    analyzeBtn.addEventListener('click', async () => {
        const username = usernameInput.value.trim();
        if (!username) {
            alert('Please enter a username');
            return;
        }

        localStorage.setItem('last_github_username', username);

        // Reset UI
        resultsContainer.classList.add('hidden');
        consoleSection.classList.remove('hidden');
        consoleDiv.innerHTML = '';
        loader.classList.remove('hidden');
        statusMessage.textContent = '';

        try {
            const response = await fetch(`/analyze?username=${encodeURIComponent(username)}`);
            if (!response.ok) throw new Error('Failed to start analysis');

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                buffer = lines.pop();

                for (const line of lines) {
                    if (!line.trim()) continue;
                    try {
                        const item = JSON.parse(line);
                        handleStreamItem(item);
                    } catch (e) {
                        console.error('Error parsing line:', line, e);
                    }
                }
            }
        } catch (error) {
            console.error(error);
            statusMessage.textContent = 'Error: ' + error.message;
            statusMessage.style.color = 'red';
        } finally {
            loader.classList.add('hidden');
        }
    });

    function handleStreamItem(item) {
        if (item.type === 'log') {
            const line = document.createElement('div');
            line.textContent = item.message;
            consoleDiv.appendChild(line);
            consoleDiv.scrollTop = consoleDiv.scrollHeight;
        } else if (item.type === 'error') {
            const line = document.createElement('div');
            line.textContent = '❌ ERROR: ' + item.message;
            line.style.color = '#f85149';
            consoleDiv.appendChild(line);
            consoleDiv.scrollTop = consoleDiv.scrollHeight;
        } else if (item.type === 'data') {
            renderResults(item.payload);
        }
    }

    function renderResults(data) {
        resultsContainer.classList.remove('hidden');
        document.getElementById('target-user').textContent = data.target_username;
        document.getElementById('follower-count').textContent = data.total_followers;

        const statsBody = document.querySelector('#stats-table tbody');
        statsBody.innerHTML = '';
        data.location_stats.slice(0, 10).forEach(([loc, count]) => {
            const percentage = ((count / data.total_followers) * 100).toFixed(1);
            const row = `<tr><td>${loc}</td><td>${count}</td><td>${percentage}%</td></tr>`;
            statsBody.insertAdjacentHTML('beforeend', row);
        });

        const detailsBody = document.querySelector('#details-table tbody');
        detailsBody.innerHTML = '';
        data.details.forEach(item => {
            const row = `<tr>
                <td><a href="https://github.com/${item.username}" target="_blank">${item.username}</a></td>
                <td>${item.location}</td>
                <td style="color: ${item.source === 'API' ? '#2da44e' : '#57606a'}">
                    <strong>${item.source}</strong>
                </td>
            </tr>`;
            detailsBody.insertAdjacentHTML('beforeend', row);
        });

        renderChart(data.location_stats);
    }

    function renderChart(stats) {
        const ctx = document.getElementById('locationChart').getContext('2d');
        if (locationChart) locationChart.destroy();

        const topN = 10;
        const labels = stats.slice(0, topN).map(s => s[0]);
        const counts = stats.slice(0, topN).map(s => s[1]);

        locationChart = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    data: counts,
                    backgroundColor: [
                        '#2da44e', '#0969da', '#8250df', '#bf3989', '#cf222e',
                        '#d4a72c', '#6e7781', '#24292f', '#42526e', '#00b8d9'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'bottom' },
                    title: { display: true, text: 'Top Follower Locations' }
                }
            }
        });
    }
});
