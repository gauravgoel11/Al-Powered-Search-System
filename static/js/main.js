/**
 * CrewSearch - Frontend JavaScript
 * Connects the UI to the CrewAI-powered backend
 */

document.addEventListener('DOMContentLoaded', function () {
    // DOM Elements
    const searchInput = document.getElementById('search-input');
    const searchButton = document.getElementById('search-button');
    const navTabs = document.querySelectorAll('.nav-tabs li');
    const loaderContainer = document.querySelector('.loader-container');
    const resultsContainer = document.querySelector('.results-container');
    const resultsContent = document.getElementById('results-content');
    const searchDuration = document.getElementById('search-duration');
    const searchTypeDisplay = document.querySelector('.search-type');
    const errorNotification = document.getElementById('error-notification');
    const errorMessage = document.getElementById('error-message');
    const notificationClose = document.querySelector('.notification-close');
    const hints = document.querySelectorAll('.hint');

    // State variables
    let currentSearchType = 'all';

    // Initialize marked for markdown rendering
    marked.setOptions({
        breaks: true,
        gfm: true,
        sanitize: false // Allow HTML in markdown
    });

    // Event listeners
    searchButton.addEventListener('click', handleSearch);
    searchInput.addEventListener('keypress', function (e) {
        if (e.key === 'Enter') {
            handleSearch();
        }
    });

    navTabs.forEach(tab => {
        tab.addEventListener('click', function () {
            setActiveTab(this);
        });
    });

    notificationClose.addEventListener('click', function () {
        errorNotification.classList.add('hidden');
    });

    hints.forEach(hint => {
        hint.addEventListener('click', function () {
            searchInput.value = this.textContent;
            searchInput.focus();
        });
    });

    // Functions
    function setActiveTab(tab) {
        navTabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        currentSearchType = tab.dataset.searchType;

        // Update agent icon in loader based on search type
        updateAgentDisplay(currentSearchType);
    }

    function updateAgentDisplay(type) {
        const agentIcon = document.querySelector('.agent-icon i');
        const agentRole = document.querySelector('.agent-role');

        switch (type) {
            case 'movie':
                agentIcon.className = 'fas fa-film';
                agentRole.textContent = 'Movie Specialist';
                break;
            case 'music':
                agentIcon.className = 'fas fa-music';
                agentRole.textContent = 'Music Curator';
                break;
            case 'news':
                agentIcon.className = 'fas fa-newspaper';
                agentRole.textContent = 'News Analyst';
                break;
            case 'general':
                agentIcon.className = 'fas fa-globe';
                agentRole.textContent = 'Research Specialist';
                break;
            default:
                agentIcon.className = 'fas fa-robot';
                agentRole.textContent = 'CrewAI';
                break;
        }
    }

    async function handleSearch() {
        const query = searchInput.value.trim();

        if (!query) {
            showError('Please enter a search query');
            return;
        }

        // Show loader, hide results
        loaderContainer.classList.remove('hidden');
        resultsContainer.classList.add('hidden');

        // Update search type icon
        let searchTypeIcon = 'fa-search';
        switch (currentSearchType) {
            case 'movie':
                searchTypeIcon = 'fa-film';
                break;
            case 'music':
                searchTypeIcon = 'fa-music';
                break;
            case 'news':
                searchTypeIcon = 'fa-newspaper';
                break;
            case 'general':
                searchTypeIcon = 'fa-globe';
                break;
        }

        searchTypeDisplay.innerHTML = `<i class="fas ${searchTypeIcon}"></i> ${capitalizeFirstLetter(currentSearchType === 'all' ? 'Smart' : currentSearchType)} Search`;

        // Start timer
        const startTime = performance.now();

        try {
            let result;

            if (currentSearchType === 'all') {
                result = await performSearch('/api/search', query);
            } else {
                result = await performSearch(`/api/${currentSearchType}`, query);
            }

            // Calculate duration
            const endTime = performance.now();
            const duration = ((endTime - startTime) / 1000).toFixed(1);
            searchDuration.textContent = duration;

            // Process and display results
            displayResults(result);

            // Hide loader, show results
            loaderContainer.classList.add('hidden');
            resultsContainer.classList.remove('hidden');

        } catch (err) {
            console.error('Search error:', err);
            loaderContainer.classList.add('hidden');
            showError(err.message || 'An error occurred during your search. Please try again.');
        }
    }

    async function performSearch(endpoint, query) {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ user_input: query })
        });

        if (!response.ok) {
            throw new Error(`Search failed with status ${response.status}`);
        }

        const data = await response.json();

        // Fix for the issue: Process the response to ensure we have standardized format
        return {
            type: data.type || 'general',
            result: data.content || data.result || (typeof data === 'string' ? data : ''),
            error: data.error || null
        };
    }

    function displayResults(result) {
        // Clear previous results
        resultsContent.innerHTML = '';

        if (result.error) {
            showError(result.error);
            return;
        }

        // Make sure we have a result value that's a string
        let resultText = result.result;

        // If the result is a complex object with raw property, extract the text
        if (typeof resultText === 'object' && resultText !== null) {
            if (resultText.raw) {
                resultText = resultText.raw;
            } else if (resultText.result) {
                resultText = resultText.result;
            } else {
                // Last resort - stringify the object but hide technical details
                resultText = "The search returned data in an unexpected format. Please try a different search.";
                console.error("Unexpected result format:", result);
            }
        }

        // Set the result content based on the type
        switch (result.type) {
            case 'movie':
                displayMovieResults({ ...result, result: resultText });
                break;
            case 'music':
                displayMusicResults({ ...result, result: resultText });
                break;
            case 'news':
                displayNewsResults({ ...result, result: resultText });
                break;
            case 'general':
                displayGeneralResults({ ...result, result: resultText });
                break;
            default:
                // If type wasn't specified, just render the markdown
                resultsContent.innerHTML = marked.parse(resultText || "No results found");
                break;
        }

        // Add animation to results
        resultsContainer.style.animation = 'none';
        resultsContainer.offsetHeight; // Trigger reflow
        resultsContainer.style.animation = 'fadeIn 0.5s forwards';
    }

    function displayMovieResults(result) {
        // Convert markdown to HTML
        const htmlContent = marked.parse(result.result || "No movie results found");

        // For movies, we could parse the markdown and create a grid of movie cards
        resultsContent.innerHTML = htmlContent;

        // Add any additional movie-specific UI enhancements here
        enhanceMovieResults();
    }

    function enhanceMovieResults() {
        // Movie results typically have thumbnails and structured info
        // This function can add additional functionality like trailers, ratings visualization, etc.

        // For demonstration, we'll just add some basic classes to improve the layout
        const movieItems = resultsContent.querySelectorAll('ul > li, ol > li');

        if (movieItems.length > 0) {
            // Create a movie grid container
            const movieGrid = document.createElement('div');
            movieGrid.className = 'movie-grid';

            // Convert each list item to a movie card
            movieItems.forEach(item => {
                const movieCard = document.createElement('div');
                movieCard.className = 'movie-card';
                movieCard.innerHTML = item.innerHTML;
                movieGrid.appendChild(movieCard);

                // Find and enhance movie rating
                const ratingText = movieCard.textContent.match(/Rating:\s*(\d+(\.\d+)?)/i);
                if (ratingText && ratingText[1]) {
                    const rating = parseFloat(ratingText[1]);
                    const ratingElement = movieCard.querySelector('strong:contains("Rating:")');
                    if (ratingElement) {
                        const ratingVisual = createRatingVisual(rating);
                        ratingElement.parentNode.appendChild(ratingVisual);
                    }
                }
            });

            // Replace the list with our grid
            movieItems[0].parentNode.replaceWith(movieGrid);
        }
    }

    function displayMusicResults(result) {
        // Convert markdown to HTML while preserving audio elements
        const htmlContent = marked.parse(result.result || "No music results found");

        // Create a container and insert the safe HTML
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = htmlContent;

        // Process the HTML before inserting into DOM
        resultsContent.innerHTML = '';
        resultsContent.appendChild(tempDiv);

        // Add music-specific enhancements
        enhanceMusicResults();
    }

    function enhanceMusicResults() {
        // Create music grid container
        const musicGrid = document.createElement('div');
        musicGrid.className = 'music-grid';

        // Process each music result
        const musicItems = resultsContent.querySelectorAll('li');

        musicItems.forEach(item => {
            // Create music card container
            const musicCard = document.createElement('div');
            musicCard.className = 'music-card';

            // Extract and process content
            const content = item.innerHTML;

            // Create temporary container to manipulate HTML
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = content;

            // Process artwork
            const artworkImg = tempDiv.querySelector('img');
            if (artworkImg) {
                artworkImg.style.width = '150px';
                artworkImg.style.height = '150px';
                artworkImg.style.objectFit = 'cover';
                artworkImg.style.borderRadius = '8px';
            }

            // Process audio preview
            const previewLink = tempDiv.querySelector('a[href*="preview"]');
            if (previewLink) {
                const audioUrl = previewLink.href;

                // Create audio player
                const audioPlayer = document.createElement('audio');
                audioPlayer.controls = true;
                audioPlayer.className = 'music-preview';
                audioPlayer.style.width = '100%';
                audioPlayer.style.marginTop = '10px';

                const source = document.createElement('source');
                source.src = audioUrl;
                source.type = 'audio/m4a';
                audioPlayer.appendChild(source);

                // Replace link with audio player
                previewLink.replaceWith(audioPlayer);
            }

            // Process iTunes link
            const itunesLink = tempDiv.querySelector('a[href*="itunes"]');
            if (itunesLink) {
                itunesLink.innerHTML = `<i class="fas fa-music"></i> Listen on iTunes`;
                itunesLink.className = 'itunes-link';
            }

            // Add processed content to card
            musicCard.innerHTML = tempDiv.innerHTML;
            musicGrid.appendChild(musicCard);
        });

        // Replace original content with grid
        resultsContent.innerHTML = '';
        resultsContent.appendChild(musicGrid);

        // Add error handling for audio elements
        resultsContent.querySelectorAll('audio').forEach(audio => {
            audio.addEventListener('error', () => {
                audio.outerHTML = '<div class="audio-error">Preview not available</div>';
            });
        });
    }

    function displayNewsResults(result) {
        // Convert markdown to HTML
        const htmlContent = marked.parse(result.result || "No news results found");

        // For news, we'll keep the structure but enhance it with additional formatting
        resultsContent.innerHTML = htmlContent;

        // Add any additional news-specific UI enhancements
        enhanceNewsResults();
    }

    function enhanceNewsResults() {
        // Add timestamp formatting
        const timestamps = Array.from(resultsContent.querySelectorAll('strong'))
            .filter(el => el.textContent.includes("Date:"));

        timestamps.forEach(timestamp => {
            const dateText = timestamp.textContent.replace('Date:', '').trim();
            if (dateText) {
                try {
                    const date = new Date(dateText);
                    const formattedDate = date.toLocaleDateString('en-US', {
                        year: 'numeric',
                        month: 'short',
                        day: 'numeric'
                    });
                    timestamp.innerHTML = 'Date: ' + formattedDate;
                } catch (e) {
                    // Keep original date if parsing fails
                }
            }
        });

        // Add news card styling
        const newsHeadings = resultsContent.querySelectorAll('h2');

        newsHeadings.forEach(heading => {
            const newsCard = document.createElement('div');
            newsCard.className = 'news-card';

            // Get all content until next h2
            let content = [];
            let currentElement = heading.nextElementSibling;

            while (currentElement && currentElement.tagName !== 'H2') {
                content.push(currentElement.cloneNode(true));
                currentElement = currentElement.nextElementSibling;
            }

            // Add heading and content to the card
            newsCard.appendChild(heading.cloneNode(true));
            content.forEach(element => newsCard.appendChild(element));

            // Replace original heading with the card
            heading.parentNode.insertBefore(newsCard, heading);
            heading.remove();

            // Remove original content elements
            content.forEach(element => {
                if (element.parentNode) {
                    element.parentNode.removeChild(element);
                }
            });
        });
    }

    function displayGeneralResults(result) {
        // Convert markdown to HTML
        const htmlContent = marked.parse(result.result || "No results found");

        // Render the content as is
        resultsContent.innerHTML = htmlContent;

        // Format any citations or sources
        enhanceGeneralResults();
    }

    function enhanceGeneralResults() {
        // Add citation styling
        const citations = resultsContent.querySelectorAll('a[href^="http"]');

        citations.forEach(citation => {
            // Extract domain name for better display
            let domain = "";
            try {
                const url = new URL(citation.href);
                domain = url.hostname.replace('www.', '');
            } catch (e) {
                domain = citation.href;
            }

            // Add citation info if not already formatted
            if (!citation.querySelector('.citation-info')) {
                const citationInfo = document.createElement('span');
                citationInfo.className = 'citation-info';
                citationInfo.innerHTML = ` <i class="fas fa-external-link-alt"></i> ${domain}`;
                citation.appendChild(citationInfo);
            }
        });

        // Add a section border to highlight key facts
        const factParagraphs = resultsContent.querySelectorAll('p:first-of-type');
        if (factParagraphs.length > 0) {
            const factBox = document.createElement('div');
            factBox.className = 'fact-box';
            factBox.appendChild(factParagraphs[0].cloneNode(true));
            factParagraphs[0].parentNode.insertBefore(factBox, factParagraphs[0]);
            factParagraphs[0].remove();
        }
    }

    function createRatingVisual(rating) {
        const maxRating = 10;
        const percentage = (rating / maxRating) * 100;

        const visualContainer = document.createElement('div');
        visualContainer.className = 'rating-visual';

        const ratingBar = document.createElement('div');
        ratingBar.className = 'rating-bar';
        ratingBar.style.width = `${percentage}%`;

        // Color coding based on rating value
        if (rating >= 7.5) {
            ratingBar.classList.add('high-rating');
        } else if (rating >= 6) {
            ratingBar.classList.add('medium-rating');
        } else {
            ratingBar.classList.add('low-rating');
        }

        visualContainer.appendChild(ratingBar);
        return visualContainer;
    }

    function showError(message) {
        errorMessage.textContent = message;
        errorNotification.classList.remove('hidden');

        // Auto-hide after 5 seconds
        setTimeout(() => {
            errorNotification.classList.add('hidden');
        }, 5000);
    }

    function capitalizeFirstLetter(string) {
        return string.charAt(0).toUpperCase() + string.slice(1);
    }

    // jQuery-like selector extension
    HTMLElement.prototype.contains = function (selector) {
        return this.textContent.indexOf(selector.replace(/:/g, '')) !== -1;
    };

    // Initialize the app
    function init() {
        // Set default search type
        navTabs.forEach(tab => {
            if (tab.dataset.searchType === 'all') {
                setActiveTab(tab);
            }
        });

        // Focus on search input
        searchInput.focus();
    }

    // Start the application
    init();
});