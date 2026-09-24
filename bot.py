import os
import requests

def get_guaranteed_meme():
    try:
        # البحث باستخدام مصطلح واسع وشامل لجلب أزواج تداول حية وفورية
        url = "https://api.dexscreener.com/latest/dex/search?q=sol"
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            pairs = data.get("pairs", [])
            
            # تصفية مرنة: نجلب أي عملة على سولانا ليست هي عملة SOL الرسمية نفسها
            for p in pairs:
                if p.get("chainId") == "solana":
                    symbol = p.get("baseToken", {}).get("symbol", "").upper()
                    # نتأكد أنها ليست SOL الأساسية أو العملات الكبرى لكي تكون ميم كوين حقيقي
                    if symbol and symbol not in ["SOL", "USDC", "USDT"]:
                        
                        name = p.get("baseToken", {}).get("name", "Unknown")
                        dex = p.get("dexId", "unknown")
                        price = p.get("priceUsd", "0")
                        pair_address = p.get("pairAddress", "")
                        
                        liquidity = p.get("liquidity", {}).get("usd", 0) or 0
                        volume_24h = p.get("volume", {}).get("h24", 0) or 0
                        
                        link = p.get("url", f"https://dexscreener.com/solana/{pair_address}")
                        
                        # الدرس العميق المبسط والسريع
                        if liquidity > 5000:
                            verdict = "🔥 ميم كوين بسيولة جيدة ومقبولة"
                        else:
                            verdict = "⚠️ ميم كوين ناشئ (سيولة ضعيفة - مخاطر عالية)"

                        analysis_report = (
                            f"🐸 **الاسم والرمز:** {name} (${symbol})\n"
                            f"🏦 **المنصة:** {dex.upper()}\n"
                            f"💵 **السعر:** ${price}\n"
                            f"💧 **السيولة:** ${liquidity:,.0f}\n"
                            f"📈 **حجم التداول (24h):** ${volume_24h:,.0f}\n\n"
                            f"🧠 **الدرس العميق:** {verdict}\n"
                            f"🔗 **رابط الفحص:** {link}"
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
        "content": f"🚀 **صيد ميم كوين جديد على سولانا:** ${coin}\n\n{analysis}"
    }
    
    requests.post(webhook_url, json=message)

if __name__ == "__main__":
    coin, analysis = get_guaranteed_meme()
    if coin:
        send_to_discord(coin, analysis)
        print(f"تم إرسال العملة {coin} بنجاح إلى ديسكورد!")
    else:
        print("لم يتم العثور على نتائج.")
