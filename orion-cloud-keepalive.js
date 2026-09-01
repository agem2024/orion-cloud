/**
 * ORION CLOUD KEEP-ALIVE PINGER
 * Prevents Render free tier from sleeping by pinging every 10 minutes.
 * Deploy to a free service or run 24/7 locally with: node orion-cloud-keepalive.js
 *
 * URL CORREGIDA 2026-08-21: orion-cloud-1.onrender.com (era orion-cloud.onrender.com - INCORRECTO)
 */

const https = require('https');

const ORION_CLOUD_URL = 'https://orion-cloud-1.onrender.com/';
const PING_INTERVAL_MS = 10 * 60 * 1000; // 10 minutos

function pingOrionCloud() {
    const timestamp = new Date().toISOString();
    https.get(ORION_CLOUD_URL, (res) => {
        console.log(`[${timestamp}] OK ORION Cloud pinged - Status: ${res.statusCode}`);
        let data = '';
        res.on('data', (chunk) => { data += chunk; });
        res.on('end', () => {
            try {
                const json = JSON.parse(data);
                console.log(`[${timestamp}] Response:`, json.status || json.system);
            } catch (e) {
                console.log(`[${timestamp}] Response received (non-JSON)`);
            }
        });
    }).on('error', (err) => {
        console.error(`[${timestamp}] PING FAILED:`, err.message);
    });
}

console.log('ORION Cloud Keep-Alive started...');
console.log('Target: ' + ORION_CLOUD_URL);
console.log('Interval: ' + (PING_INTERVAL_MS / 1000 / 60) + ' minutes\n');
pingOrionCloud();
setInterval(pingOrionCloud, PING_INTERVAL_MS);
