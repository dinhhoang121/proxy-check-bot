import logging
import asyncio
import socket
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

async def check_single_port(host, port, timeout=3):
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout)
        writer.close()
        await writer.wait_closed()
        return True
    except:
        return False

async def check_all_ports(proxies):
    results = []
    tasks = []
    for proxy in proxies:
        if ":" not in proxy:
            continue
        host, port = proxy.strip().split(":")
        tasks.append(check_single_port(host, int(port)))
    statuses = await asyncio.gather(*tasks)
    for proxy, status in zip(proxies, statuses):
        results.append(f"{'✅ Sống' if status else '❌ Chết'} - {proxy}")
    return results

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⚡ Đang kiểm tra proxy domain bằng TCP port...")

    try:
        with open("proxy.txt", "r") as f:
            proxies = [line.strip() for line in f if line.strip()]
    except:
        await update.message.reply_text("❌ Không tìm thấy file proxy.txt!")
        return

    results = await check_all_ports(proxies)
    output = "\n".join(results[:50])
    await update.message.reply_text(output or "Không có proxy nào.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("check", check))
    print("🤖 Bot đang chạy...")
    app.run_polling()
