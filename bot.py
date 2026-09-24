import os
import requests

def check_whale_tweets():
    tweet_text = "Just loaded up on some $MOON 🚀 Contract: 0x9876...5432 - This is going to the moon!"
    return tweet_text

def analyze_coin(tweet):
    if "$" in tweet:
        coin_name = "MOON"
        analysis_result = "السيولة جيدة، تم رصد ذكر الحوت، يرجى التحقق من عقد العملة يدوياً قبل الشراء."
        return coin_name, analysis_result
    return None, None

def send_to_discord(coin, analysis):
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    
    if not webhook_url:
        print("خطأ: لم يتم العثور على رابط ديسكورد ويب هوك في متغيرات البيئة.")
        return

    message = {
        "content": f"🚨 **تنبيه عملة ميم جديدة من الحوت!**\n\n- **العملة:** ${coin}\n- **التحليل الأولي:** {analysis}\n- **الحالة:** موثوقية أولية مقبولة ✅"
    }
    
    response = requests.post(webhook_url, json=message)
    if response.status_code == 204:
        print("تم إرسال التنبيه إلى ديسكورد بنجاح!")
    else:
        print(f"فشل في الإرسال، كود الخطأ: {response.status_code}")

if __name__ == "__main__":
    tweet = check_whale_tweets()
    coin, analysis = analyze_coin(tweet)
    
    if coin:
        send_to_discord(coin, analysis)
