# Chat Server (Node.js WebSocket)
سرور چت بین‌المللی پلتفرم علمی چندرشته‌ای پارسی

## نصب
```bash
cd chat-server
cp .env.example .env  # اگر توسط PHP install.php ساخته نشده
npm install
npm start
```

## اجرای پس‌زمینه
```bash
nohup node server.js > chat.log 2>&1 &
```

یا با cron (هر دقیقه):
```bash
cd /home/USER/public_html/chat-server && pgrep -f "node server.js" > /dev/null || nohup /usr/bin/node server.js > chat.log 2>&1 &
```
