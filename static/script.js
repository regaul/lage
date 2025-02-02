// grab our dom elements
const searchInput = document.querySelector('.text-input');
const resultsContainer = document.querySelector('.results');
const resetButton = document.querySelector('.reset-btn');
const album = document.querySelector('.album');
const nextButton = document.querySelector('.next-btn');
const prevButton = document.querySelector('.prev-btn');

// set up state vars
let currentSong = null;
let currentResults = [];
let searchTimeout = null;
let currentRecommendationIndex = 0;
let recommendations = [];

// handle search input with debouncing
searchInput.addEventListener('input', (e) => {
    clearTimeout(searchTimeout);
    const query = e.target.value.trim();
    
    if (query.length > 0) {
        searchTimeout = setTimeout(() => searchSongs(query), 300);
    } else {
        clearResults();
    }
});

// button functionality
nextButton.addEventListener('click', () => handleNavigation('next'));
prevButton.addEventListener('click', () => handleNavigation('prev'));
resetButton.addEventListener('click', resetInterface);

// event delegation for search results
resultsContainer.addEventListener('click', (e) => {
    const resultItem = e.target.closest('.result-item');
    if (!resultItem) return;
    
    const index = resultItem.dataset.index;
    if (index !== undefined) {
        handleSongSelect(parseInt(index));
    }
});

// handles prev/next navigation
function handleNavigation(direction) {
    if (!recommendations.length) return;
    
    if (direction === 'next') {
        currentRecommendationIndex = (currentRecommendationIndex + 1) % recommendations.length;
    } else {
        currentRecommendationIndex = (currentRecommendationIndex - 1 + recommendations.length) % recommendations.length;
    }
    
    const currentSong = recommendations[currentRecommendationIndex];
    updateDisplay(currentSong);
}

// search for songs - UPDATED to use /search endpoint
async function searchSongs(query) {
    try {
        const response = await fetch('/search', {  // Changed endpoint from /recommendations to /search
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query })
        });

        if (!response.ok) throw new Error('Search failed');

        const data = await response.json();
        displayResults(data.tracks);
    } catch (error) {
        console.error('Search error:', error);
        displayError('Search failed. Please try again.');
    }
}

// resets everything back to initial state
function resetInterface() {
    currentSong = null;
    currentResults = [];
    recommendations = [];
    currentRecommendationIndex = 0;
    
    searchInput.value = '';
    searchInput.disabled = false;
    resultsContainer.innerHTML = '';
    album.innerHTML = '';
    
    nextButton.classList.add('hidden');
    prevButton.classList.add('hidden');
    resetButton.classList.add('hidden');
}

// show search results
function displayResults(results) {
    if (!results || !results.length) {
        displayError('No results found.');
        return;
    }
    
    currentResults = results;
    resultsContainer.innerHTML = `
        <div style="display: flex; flex-direction: column; align-items: center; width: 100%;">
            ${results.map((result, index) => `
                <div class="result-item" data-index="${index}" style="text-align: center; width: 300px; margin: 5px 0;">
                    ${result.title} - ${result.artist}
                </div>
            `).join('')}
        </div>`;
}

// Add this new function to handle recommendation clicks
function handleRecommendationClick(index) {
    if (!recommendations[index]) return;
    currentRecommendationIndex = index;
    updateDisplay(recommendations[index]);
}

// handles trackID being read by backend and puts out the code
async function handleSongSelect(index) {

    const selectedTrack = currentResults[index];
    if (!selectedTrack) {
        console.error("No track found at index:", index);
        return;
    }
    
    currentSong = selectedTrack;
    
    try {
        // updates UI for better UX
        searchInput.value = `${selectedTrack.title} - ${selectedTrack.artist}`;
        searchInput.disabled = true;
        
        if (selectedTrack.id) {
            album.innerHTML = `
                <div class="tidal-embed" style="position: relative; padding-bottom: 100%; height: 0; overflow: hidden; max-width: 100%; margin: 0 auto;">
                    <iframe 
                        src="https://embed.tidal.com/tracks/${selectedTrack.id}?layout=gridify" 
                        frameborder="0" 
                        allowfullscreen="allowfullscreen"
                        allow="encrypted-media"
                        style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; min-height: 100%;">
                    </iframe>
                </div>`;
        }
        
        // send only the trackId for recommendations
        const response = await fetch('/recommendations', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ trackId: selectedTrack.id, similarTracks: selectedTrack.similarTracks })
        });

        

        //check if response went thriugh
        if (!response.ok) throw new Error('Failed to get recommendations');

        //parses response
        const data = await response.json();
        if (!data.recommendations || !data.recommendations.length) {
            throw new Error('No recommendations received');
        }

        //assigns the song recs to UI
        recommendations = data.recommendations;
        currentRecommendationIndex = 0;

        //album image container
        resultsContainer.innerHTML = `
            <div style="display: flex; flex-direction: column; align-items: center; width: 100%;">
                <div class="recommendations" style="width: 300px;">
                    ${recommendations.map((rec, idx) => `
                        <div class="result-item recommendation-item" 
                             style="text-align: center; margin: 5px 0; cursor: pointer;"
                             data-recommendation-index="${idx}">
                            ${rec.title} - ${rec.artist}
                        </div>
                    `).join('')}
                </div>
            </div>
        `;

        // Add click event listeners to recommendation items
        const recommendationItems = document.querySelectorAll('.recommendation-item');
        recommendationItems.forEach(item => {
            item.addEventListener('click', (e) => {
                const index = parseInt(e.target.dataset.recommendationIndex);
                handleRecommendationClick(index);
            });
        });
        
        nextButton.classList.remove('hidden');
        prevButton.classList.remove('hidden');
        resetButton.classList.remove('hidden');
        
    } catch (error) {
        console.error('Error getting recommendations:', error);
        displayError('Failed to get recommendations. Please try again.');
    }
}

// updates the display with current song
function updateDisplay(song) {
    if (!song) return;
    searchInput.value = `${song.title} - ${song.artist}`;
    if (song.id) {
        album.innerHTML = `<div class="tidal-embed" style="position:relative;padding-bottom:100%;height:0;overflow:hidden;max-width:100%"><iframe src="https://embed.tidal.com/tracks/${song.id}?layout=gridify" allow="encrypted-media" allowfullscreen="allowfullscreen" frameborder="0" style="position:absolute;top:0;left:0;width:100%;height:1px;min-height:100%;margin:0 auto"></iframe></div>`;
    }
}

// shows error message
function displayError(message) {
    resultsContainer.innerHTML = `<div class="error">${message}</div>`;
}

function clearResults() {
    resultsContainer.innerHTML = '';
    currentResults = [];
}