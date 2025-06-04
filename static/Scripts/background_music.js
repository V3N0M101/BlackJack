// Background Music Controller
(function() {
    // Only run on main, learn, or news pages
    const allowedPaths = ['/', '/main', '/learn', '/news'];
    if (!allowedPaths.includes(window.location.pathname)) {
        console.log('Not on main/learn/news page, current path:', window.location.pathname);
        return;
    }

    // Check if user is logged in (assuming isLoggedIn is available globally)
    if (typeof isLoggedIn === 'undefined' || !isLoggedIn) {
        console.log('User not logged in, skipping music');
        return;
    }

    console.log('Initializing background music...');

    // Create audio element
    const bgMusic = new Audio('/static/Audio/background_music.mp3');
    bgMusic.loop = true;
    bgMusic.volume = 0.1; // 10% volume (0.1 = 10%)

    // Add event listeners for debugging
    bgMusic.addEventListener('canplay', () => {
        console.log('Audio can play now');
    });

    bgMusic.addEventListener('error', (e) => {
        console.error('Audio error:', e);
    });

    bgMusic.addEventListener('playing', () => {
        console.log('Audio started playing');
    });

    // Get stored timestamp
    const storedTime = localStorage.getItem('bgMusicTime');
    if (storedTime) {
        bgMusic.currentTime = parseFloat(storedTime);
        console.log('Resuming from time:', storedTime);
    }

    // Save timestamp periodically (every 5 seconds)
    setInterval(() => {
        if (!bgMusic.paused) {
            localStorage.setItem('bgMusicTime', bgMusic.currentTime.toString());
        }
    }, 5000);

    // Handle page visibility changes
    document.addEventListener('visibilitychange', () => {
        if (document.hidden) {
            bgMusic.pause();
            console.log('Page hidden, pausing music');
        } else {
            console.log('Page visible, attempting to play music');
            bgMusic.play().catch(err => console.log('Playback prevented:', err));
        }
    });

    // Start playback
    console.log('Attempting to start playback...');
    bgMusic.play().catch(err => {
        console.log('Autoplay prevented:', err);
        // Add a play button as fallback if autoplay is blocked
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
        playButton.onclick = () => {
            bgMusic.play();
            playButton.remove();
        };
        document.body.appendChild(playButton);
    });

    // Add to window object for debugging
    window.bgMusic = bgMusic;
})(); 