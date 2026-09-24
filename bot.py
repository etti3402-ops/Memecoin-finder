import os
import requests

def get_actual_meme_token():
    try:
        # استخدام نقطة نهاية جلب أحدث البروفايلات والعملات المضافة حديثاً
        url = "https://api.dexscreener.com/latest/dex/tokens/latest"
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            pairs = data.get("pairs", [])
            
            # تصفية صارمة: عملات سولانا فقط، واستبعاد العملات الكبرى والمنصات مثل SOL أو PUMP
            valid_memes = []
            for p in pairs:
                if p.get("chainId") == "solana":
                    symbol = p.get("baseToken", {}).get("symbol", "").upper()
                    # استبعاد الأسماء الكلاسيكية والوهمية
                    if symbol not in ["SOL", "PUMP", "USDC", "USDT", "WBTC", "BONK", "WIF"]:
                        valid_memes.append(p)
            
            if valid_memes:
                top = valid_memes[0]
                symbol = top.get("baseToken", {}).get("symbol", "UNKNOWN")
                name = top.get("baseToken", {}).get("name", "Unknown")
                dex = top.get("dexId", "unknown")
                price = top.get("priceUsd", "0")
                pair_address = top.get("pairAddress", "")
                
                # بيانات الدرس العميق
                liquidity = top.get("liquidity", {}).get("usd", 0) or 0
                volume_24h = top.get("volume", {}).get("h24", 0) or 0
                
                link = top.get("url", f"https://dexscreener.com/solana/{pair_address}")
                
                # تقييم الدرس العميق
                if liquidity > 3000:
                    verdict = "🔥 ميم كوين جديد بسيولة مقبولة"
                else:
                    verdict = "⚠️ ميم كوين ناشئ حديثاً جداً (مخاطر عالية/شديد الحذر)"

                analysis_report = (
                    f"🐸 **تم رصد ميم كوين حقيقي!**\n"
                    f"🏷️ **الاسم والرمز:** {name} (${symbol})\n"
                    f"🏦 **المنصة:** {dex.upper()}\n"
                    f"💵 **السعر:** ${price}\n"
                    f"💧 **السيولة:** ${liquidity:,.0f}\n"
                    f"📈 **حجم التداول (24h):** ${volume_24h:,.0f}\n\n"
                    f"🧠 **الدرس العميق:** {verdict}\n"
                    f"🔗 **رابط الفحص المباشر:** {link}"
                )
                
                return symbol, analysis_report
        return None, None
    except Exception as e:
        print(f"خطأ: {e}")
        return None, None

def send_to_discord(coin, analysis):
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        return

    message = {
        "content": f"🚀 **صيد جديد (مـيـم كـويـن):** ${coin}\n\n{analysis}"
    }
    
    requests.post(webhook_url, json=message)

if __name__ == "__main__":
    coin, analysis = get_actual_meme_token()
    if coin:
        send_to_discord(coin, analysis)
        print(f"تم إرسال العملة {coin} بنجاح!")
    else:
        print("لم يتم العثور على عملة مطابقة.")
