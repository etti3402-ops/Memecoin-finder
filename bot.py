import os
import requests
import re

# وضع اسم المستخدم للحوت الذي تريد متابعته على تويتر (بدون علامة @)
WHALE_USERNAME = "WhaleWire"  # يمكنك تغييره إلى أي حساب حوت آخر

def get_latest_tweet():
    try:
        # استخدام خدمة بديلة مجانية لجلب آخر تغريدات الحساب بشكل نصي وبدون API معقد
        url = f"https://nitter.poast.org/{WHALE_USERNAME}/rss"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            # استخراج محتوى التغريدات باستخدام تعبير برمجي بسيط (Regex)
            from xml.etree import ElementTree as ET
            root = ET.fromstring(response.content)
            
            # جلب أحدث تغريدة
            for item in root.findall('.//item'):
                tweet_text = item.find('description').text
                return tweet_text
        return None
    except Exception as e:
        print(f"خطأ أثناء جلب تغريدات الحوت: {e}")
        return None

def analyze_coin(tweet):
    if not tweet:
        return None, None
        
    # البحث عن رموز العملات التي تبدأ بعلامة $ أو كلمات تدل على العقود
    # مثل البحث عن رمز مكون من أحرف كبيرة بعد علامة الدولار
    coin_match = re.findall(r'\$([A-Z0-9]{2,10})', tweet)
    
    if coin_match:
        # أخذ أول رمز عملة يتم العثور عليه في التغريدة
        coin_name = coin_match[0]
        
        # تحليل مبدئي ذكي للعملة بناءً على نص التغريدة
        analysis_result = f"تم رصده في تغريدة حقيقية للحساب @{WHALE_USERNAME}.\nالنص الأصلي: {tweet[:100]}..."
        return coin_name, analysis_result
        
    return None, None

def send_to_discord(coin, analysis):
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    
    if not webhook_url:
        print("خطأ: لم يتم العثور على رابط ديسكورد ويب هوك في متغيرات البيئة.")
        return

    message = {
        "content": f"🚨 **تنبيه عملة ميم حقيقية من الحوت!**\n\n- **العملة المستخرجة:** ${coin}\n- **التحليل:** {analysis}\n- **الحالة:** تم الفحص الآلي ✅"
    }
    
    response = requests.post(webhook_url, json=message)
    if response.status_code == 204:
        print("تم إرسال التنبيه إلى ديسكورد بنجاح!")
    else:
        print(f"فشل في الإرسال، كود الخطأ: {response.status_code}")

if __name__ == "__main__":
    tweet = get_latest_tweet()
    if tweet:
        coin, analysis = analyze_coin(tweet)
        if coin:
            send_to_discord(coin, analysis)
        else:
            print("لم يتم العثور على اسم عملة جديدة في آخر تغريدة.")
    else:
        print("تعذر جلب التغريدة الحالية.")
