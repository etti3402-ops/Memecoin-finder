import os
import requests

def get_dex_trending():
    try:
        url = "https://api.dexscreener.com/latest/dex/tokens/trending"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            pairs = data.get("pairs", [])
            
            if pairs:
                # نأخذ أول عملة ظهرت في الترند مباشرة
                top = pairs[0]
                symbol = top.get("baseToken", {}).get("symbol", "UNKNOWN")
                name = top.get("baseToken", {}).get("name", "Unknown")
                chain = top.get("chainId", "solana")
                price = top.get("priceUsd", "0")
                link = top.get("url", "https://dexscreener.com")
                
                info = f"الاسم: {name}\nالشبكة: {chain.upper()}\nالسعر: ${price}\nالرابط: {link}"
                return symbol, info
        return None, None
    except Exception as e:
        print(f"خطأ في الـ API: {e}")
        return None, None

def send_to_discord(coin, info):
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("رابط ديسكورد غير موجود!")
        return

    message = {
        "content": f"🔥 **عملة ترند جديدة من DexScreener!**\n\n- **الرمز:** ${coin}\n{info}"
    }
    
    response = requests.post(webhook_url, json=message)
    if response.status_code == 204:
        print("تم الإرسال لديسكورد بنجاح!")
    else:
        print(f"فشل الإرسال، الكود: {response.status_code}")

if __name__ == "__main__":
    coin, info = get_dex_trending()
    if coin:
        send_to_discord(coin, info)
    else:
        print("لم يتم العثور على عملات حالياً.")
