// dom elements
const searchBar = document.querySelector('.search-bar');
const resultsDiv = document.querySelector('.results');

// event listener with cache overload stopper
searchBar.addEventListener('input', debounce(async (e) => {
    const query = e.target.value;
    
    if (!query) {
        resultsDiv.innerHTML = '';
        return;
    }
    
    try {
        const response = await fetch('/recommendations', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query })
        });
        
        const data = await response.json();
        console.log('Received data:', data);
        displayResults(data.recommendations);
    } catch (error) {
        console.error('Error:', error);
    }
}, 300));

function displayResults(songs) {
    resultsDiv.innerHTML = songs.map(song => `
        <div class="song" onclick="window.location.href='${song.url}'">
            ${song.title} - ${song.artist}
        </div>
    `).join('');
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}