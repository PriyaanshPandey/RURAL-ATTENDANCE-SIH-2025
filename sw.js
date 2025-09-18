const CACHE_NAME = 'attendance-v2';
const urlsToCache = [
    '/',
    '/attendance.html',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css',
    'https://cdn.jsdelivr.net/npm/jsqr@1.4.0/dist/jsQR.min.js'
];

self.addEventListener('install', function(event) {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(function(cache) {
                return cache.addAll(urlsToCache);
            })
    );
});

self.addEventListener('fetch', function(event) {
    if (event.request.url.includes('/api/')) {
        event.respondWith(
            fetch(event.request)
                .then(function(response) {
                    return response;
                })
                .catch(function(error) {
                    return new Response(JSON.stringify({ 
                        error: 'You are offline. Data will be synced when you are back online.' 
                    }), {
                        headers: { 'Content-Type': 'application/json' }
                    });
                })
        );
    } else {
        event.respondWith(
            caches.match(event.request)
                .then(function(response) {
                    if (response) {
                        return response;
                    }
                    return fetch(event.request);
                })
        );
    }
});

self.addEventListener('sync', function(event) {
    if (event.tag === 'sync-attendance') {
        event.waitUntil(syncAttendance());
    }
});

async function syncAttendance() {
    try {
        const db = await openDB();
        const transaction = db.transaction(["attendance"], "readwrite");
        const store = transaction.objectStore("attendance");
        const request = store.getAll();
        
        request.onsuccess = async () => {
            const unsynced = request.result.filter(r => !r.synced);
            for (let record of unsynced) {
                try {
                    const response = await fetch('/api/attendance', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            class_id: record.classId,
                            date: record.date,
                            attendance: record.attendance
                        })
                    });
                    if (response.ok) {
                        const updateTransaction = db.transaction(["attendance"], "readwrite");
                        const updateStore = updateTransaction.objectStore("attendance");
                        record.synced = true;
                        updateStore.put(record);
                    }
                } catch (err) {
                    console.error('Sync failed for record:', record, err);
                }
            }
        };
    } catch (err) {
        console.error('Sync error:', err);
    }
}

function openDB() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open("AttendanceDB", 2);
        request.onupgradeneeded = (event) => {
            const db = event.target.result;
            if (!db.objectStoreNames.contains('attendance')) {
                const attendanceStore = db.createObjectStore("attendance", { keyPath: "id", autoIncrement: true });
                attendanceStore.createIndex("classId_date", ["classId", "date"], { unique: false });
            }
            if (!db.objectStoreNames.contains('syncQueue')) {
                db.createObjectStore("syncQueue", { keyPath: "id", autoIncrement: true });
            }
        };
        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error);
    });
}