// Background Music Controller
(function() {
    // Only run on main page
    const allowedPaths = ['/', '/main'];
    if (!allowedPaths.includes(window.location.pathname)) {
        console.log('Not on main page, current path:', window.location.pathname);
        return;
    }

    // Check if user is logged in (assuming isLoggedIn is available globally)
    if (typeof isLoggedIn === 'undefined' || !isLoggedIn) {
        console.log('User not logged in, skipping music');
        return;
    }

    console.log('Initializing background music...');

    // Register service worker for music control
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/static/Scripts/music-worker.js')
            .then(registration => {
                console.log('Music Service Worker registered:', registration);
                initializeAudio();
            })
            .catch(error => {
                console.error('Music Service Worker registration failed:', error);
            });
    } else {
        console.log('Service Workers not supported, falling back to regular audio');
        initializeAudio();
    }

    function initializeAudio() {
        // Create audio element
        const bgMusic = new Audio('/static/Audio/background_music.mp3');
        bgMusic.loop = true;
        bgMusic.volume = 0.1; // 10% volume

        // Add event listeners for debugging
        bgMusic.addEventListener('canplay', () => {
            console.log('Audio can play now');
        });

        bgMusic.addEventListener('error', (e) => {
            console.error('Audio error:', e);
        });

        // Handle service worker messages
        if (navigator.serviceWorker) {
            navigator.serviceWorker.addEventListener('message', (event) => {
                if (event.data.type === 'MUSIC_STATE') {
                    if (event.data.isPlaying && bgMusic.paused) {
                        bgMusic.play().catch(err => console.log('Playback prevented:', err));
                    } else if (!event.data.isPlaying && !bgMusic.paused) {
                        bgMusic.pause();
                    }
                }
            });

            // Get initial state
            navigator.serviceWorker.controller?.postMessage({ type: 'GET_STATE' });
        }

        // Handle page visibility changes
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                bgMusic.pause();
            } else if (navigator.serviceWorker.controller) {
                // Check state with service worker when page becomes visible
                navigator.serviceWorker.controller.postMessage({ type: 'GET_STATE' });
            }
        });

        // Create play button
        const playButton = document.createElement('button');
        playButton.textContent = '🎵 Play Music';
        playButton.style.position = 'fixed';
        playButton.style.bottom = '20px';
        playButton.style.right = '20px';
        playButton.style.zIndex = '1000';
        playButton.style.padding = '10px';
        playButton.style.borderRadius = '5px';
        playButton.style.backgroundColor = '#00800092';
        playButton.style.color = 'white';
        playButton.style.border = 'none';
        playButton.style.cursor = 'pointer';
        playButton.style.fontFamily = "'Courier New', Courier, monospace";

        let isPlaying = false;
        playButton.onclick = () => {
            if (!isPlaying) {
                bgMusic.play().then(() => {
                    isPlaying = true;
                    playButton.textContent = '🎵 Pause Music';
                    if (navigator.serviceWorker.controller) {
                        navigator.serviceWorker.controller.postMessage({ type: 'PLAY_MUSIC' });
                    }
                }).catch(err => console.log('Playback prevented:', err));
            } else {
                bgMusic.pause();
                isPlaying = false;
                playButton.textContent = '🎵 Play Music';
                if (navigator.serviceWorker.controller) {
                    navigator.serviceWorker.controller.postMessage({ type: 'PAUSE_MUSIC' });
                }
            }
        };

        document.body.appendChild(playButton);

        // Add to window object for debugging
        window.bgMusic = bgMusic;
    }
})(); 