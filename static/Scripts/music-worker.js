// Music Service Worker
self.addEventListener('install', (event) => {
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(clients.claim());
});

let audioContext = null;
let audioSource = null;
let isPlaying = false;

self.addEventListener('message', async (event) => {
  if (event.data.type === 'PLAY_MUSIC') {
    if (!isPlaying) {
      isPlaying = true;
      // Broadcast to all clients that music is playing
      const clients = await self.clients.matchAll();
      clients.forEach(client => {
        client.postMessage({ type: 'MUSIC_STATE', isPlaying: true });
      });
    }
  } else if (event.data.type === 'PAUSE_MUSIC') {
    isPlaying = false;
    // Broadcast to all clients that music is paused
    const clients = await self.clients.matchAll();
    clients.forEach(client => {
      client.postMessage({ type: 'MUSIC_STATE', isPlaying: false });
    });
  } else if (event.data.type === 'GET_STATE') {
    // Send current state to the requesting client
    event.source.postMessage({ type: 'MUSIC_STATE', isPlaying });
  }
}); 