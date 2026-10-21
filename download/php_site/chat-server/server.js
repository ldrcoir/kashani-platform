// ============================================================
// chat-server/server.js — سرور چت WebSocket
// ============================================================
const WebSocket = require('ws');
const mysql = require('mysql2/promise');
const jwt = require('jsonwebtoken');

const CONFIG = {
    port: process.env.CHAT_PORT || 8080,
    db: {
        host: process.env.DB_HOST || 'localhost',
        user: process.env.DB_USER || 'root',
        password: process.env.DB_PASS || '',
        database: process.env.DB_NAME || 'science',
    },
    jwtSecret: process.env.JWT_SECRET || 'CHANGE_THIS',
    maxMessageLength: 500,
    rateLimitPerMinute: 10,
    maxConnections: 1000,
};

let pool;
try {
    pool = mysql.createPool({ ...CONFIG.db, waitForConnections: true, connectionLimit: 10 });
    console.log('[DB] Pool created');
} catch (e) { console.error('[DB] Error:', e.message); process.exit(1); }

const wss = new WebSocket.Server({ port: CONFIG.port, maxPayload: 1024 * 100 });
console.log(`[Chat] Server on port ${CONFIG.port}`);

const clients = new Map();
const userSockets = new Map();
const rooms = new Map();

function sendJSON(ws, obj) { if (ws.readyState === WebSocket.OPEN) ws.send(JSON.stringify(obj)); }

function broadcastToRoom(roomId, msg, exclude = null) {
    const room = rooms.get(roomId);
    if (!room) return;
    for (const ws of room) if (ws !== exclude && ws.readyState === WebSocket.OPEN) sendJSON(ws, msg);
}

async function loadRecentMessages(roomId, limit = 50) {
    try {
        const [rows] = await pool.query(
            `SELECT m.id, m.room_id, m.user_id, m.content, m.type as msgType, m.created_at, u.name FROM chat_messages m JOIN users u ON m.user_id = u.id WHERE m.room_id = ? AND m.is_deleted = 0 ORDER BY m.created_at DESC LIMIT ?`,
            [roomId, limit]
        );
        return rows.reverse().map(r => ({...r, timestamp: new Date(r.created_at).getTime() / 1000}));
    } catch (e) { return []; }
}

async function saveMessage(roomId, userId, content, type = 'text') {
    try {
        const [r] = await pool.query("INSERT INTO chat_messages (room_id, user_id, content, type) VALUES (?, ?, ?, ?)", [roomId, userId, content, type]);
        return r.insertId;
    } catch (e) { return null; }
}

function authenticate(token) {
    try { return jwt.verify(token, CONFIG.jwtSecret); } catch (e) { return null; }
}

function isRateLimited(client) {
    const now = Date.now();
    client.lastMsgTime = (client.lastMsgTime || []).filter(t => now - t < 60000);
    if (client.lastMsgTime.length >= CONFIG.rateLimitPerMinute) return true;
    client.lastMsgTime.push(now);
    return false;
}

async function handleMessage(ws, data) {
    const client = clients.get(ws);
    if (!client) return;
    
    const { type, payload } = data;
    
    if (type === 'join_room') {
        const roomId = parseInt(payload.roomId);
        if (!roomId) return;
        try {
            const [rs] = await pool.query("SELECT id, name, name_en, name_ar, name_fa, icon FROM chat_rooms WHERE id = ? AND is_active = 1", [roomId]);
            if (!rs.length) return sendJSON(ws, { type: 'error', message: 'Room not found' });
            
            if (!rooms.has(roomId)) rooms.set(roomId, new Set());
            rooms.get(roomId).add(ws);
            client.rooms.add(roomId);
            
            await pool.query("INSERT IGNORE INTO chat_room_members (room_id, user_id) VALUES (?, ?)", [roomId, client.userId]);
            
            sendJSON(ws, {
                type: 'room_joined',
                room: rs[0],
                recentMessages: await loadRecentMessages(roomId),
            });
            
            broadcastToRoom(roomId, { type: 'user_joined', roomId, userId: client.userId, name: client.name }, ws);
        } catch (e) { console.error('join_room:', e.message); }
    } else if (type === 'leave_room') {
        const roomId = parseInt(payload.roomId);
        const room = rooms.get(roomId);
        if (room) { room.delete(ws); if (room.size === 0) rooms.delete(roomId); }
        client.rooms.delete(roomId);
        broadcastToRoom(roomId, { type: 'user_left', roomId, userId: client.userId, name: client.name });
    } else if (type === 'send_message') {
        if (isRateLimited(client)) return sendJSON(ws, { type: 'error', message: 'Rate limited' });
        const roomId = parseInt(payload.roomId);
        const content = (payload.content || '').toString().slice(0, CONFIG.maxMessageLength);
        const msgType = ['text','latex','image','file'].includes(payload.type) ? payload.type : 'text';
        if (!roomId || !content) return;
        
        const msgId = await saveMessage(roomId, client.userId, content, msgType);
        if (!msgId) return sendJSON(ws, { type: 'error', message: 'Save failed' });
        
        broadcastToRoom(roomId, {
            type: 'message', id: msgId, roomId, userId: client.userId, name: client.name,
            email: client.email, content, msgType, timestamp: Date.now() / 1000,
        });
    } else if (type === 'typing') {
        const roomId = parseInt(payload.roomId);
        if (roomId) broadcastToRoom(roomId, { type: 'typing', roomId, userId: client.userId, name: client.name }, ws);
    } else if (type === 'ping') {
        sendJSON(ws, { type: 'pong', timestamp: Date.now() });
    }
}

wss.on('connection', async (ws, req) => {
    console.log(`[Chat] New connection from ${req.socket.remoteAddress}`);
    
    if (wss.clients.size > CONFIG.maxConnections) {
        sendJSON(ws, { type: 'error', message: 'Server at capacity' });
        ws.close();
        return;
    }
    
    const url = new URL(req.url, 'http://localhost');
    const token = url.searchParams.get('token') || '';
    const auth = authenticate(token);
    if (!auth) {
        sendJSON(ws, { type: 'error', message: 'Auth required' });
        ws.close();
        return;
    }
    
    try {
        const [users] = await pool.query("SELECT id, email, name, language FROM users WHERE id = ?", [auth.userId]);
        if (!users.length) { sendJSON(ws, { type: 'error', message: 'User not found' }); ws.close(); return; }
        
        const u = users[0];
        const client = {
            userId: u.id, email: u.email, name: u.name || u.email,
            lang: u.language || 'fa', rooms: new Set(), lastMsgTime: [], connectedAt: Date.now(),
        };
        clients.set(ws, client);
        if (!userSockets.has(u.id)) userSockets.set(u.id, new Set());
        userSockets.get(u.id).add(ws);
        
        sendJSON(ws, { type: 'connected', user: { id: u.id, name: u.name, email: u.email, lang: u.lang } });
        
        const [roomList] = await pool.query("SELECT id, name, name_en, name_ar, icon, category FROM chat_rooms WHERE is_active = 1 ORDER BY category, name");
        sendJSON(ws, { type: 'room_list', rooms: roomList });
    } catch (e) {
        console.error('[Chat] Auth error:', e.message);
        ws.close();
    }
    
    ws.on('message', (raw) => {
        try { handleMessage(ws, JSON.parse(raw.toString())); } catch (e) { sendJSON(ws, { type: 'error', message: 'Invalid JSON' }); }
    });
    
    ws.on('close', () => {
        const client = clients.get(ws);
        if (client) {
            for (const roomId of client.rooms) {
                const room = rooms.get(roomId);
                if (room) { room.delete(ws); if (room.size === 0) rooms.delete(roomId); broadcastToRoom(roomId, { type: 'user_left', roomId, userId: client.userId, name: client.name }); }
            }
            const us = userSockets.get(client.userId);
            if (us) { us.delete(ws); if (us.size === 0) userSockets.delete(client.userId); }
            console.log(`[Chat] ${client.userId} disconnected`);
        }
        clients.delete(ws);
    });
    
    ws.on('error', (err) => console.error('[Chat] Socket error:', err.message));
});

process.on('SIGTERM', () => {
    wss.clients.forEach(ws => { sendJSON(ws, { type: 'server_shutdown' }); ws.close(); });
    setTimeout(() => process.exit(0), 1000);
});

setInterval(() => wss.clients.forEach(ws => ws.readyState === WebSocket.OPEN && ws.ping()), 30000);
console.log('[Chat] Ready!');
