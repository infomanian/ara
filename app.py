from flask import Flask, request, jsonify, render_template, session
from openai import OpenAI
from flask_session import Session
import os
from werkzeug.utils import secure_filename

API_KEY = "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"
client = OpenAI(api_key=API_KEY)

app = Flask(__name__)
app.secret_key = '123'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
Session(app)


@app.route('/')
def index():
    return render_template('chat.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_msg = request.json.get('message')
    if 'history' not in session:
        session['history'] = [{"role": "system", "content": "تو یک دستیار حقوقی هستی. پاسخ‌ها را به زبان فارسی و مطابق قوانین ایران بده."}]

  
        # بارگذاری تاریخچه از سشن
    session['history'].append({"role": "user", "content": user_msg})
    

    # فراخوانی GPT با تاریخچه کامل
    response = client.chat.completions.create(
        model="gpt-4",
        messages=session['history'],
        temperature=0.3
    )

    reply = response.choices[0].message.content.strip()
    
    # اضافه کردن پاسخ به تاریخچه
    session['history'].append({"role": "assistant", "content": reply})

    return jsonify({'response': reply})

@app.route('/analyze-file', methods=['POST'])
def analyze_file():
    file = request.files.get('file')
    if not file:
        return jsonify({'response': 'فایلی ارسال نشده است.'})

    filename = secure_filename(file.filename)
    ext = os.path.splitext(filename)[1].lower()

    if ext == '.txt':
        text = file.read().decode('utf-8', errors='ignore')
    elif ext == '.docx':
        try:
            import docx
        except ImportError:
            return jsonify({'response': 'کتابخانه python-docx نصب نشده است.'})
        doc = docx.Document(file)
        text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
    else:
        return jsonify({'response': 'فقط فایل‌های .txt و .docx پشتیبانی می‌شوند.'})

    # دستور به GPT برای بررسی فنی
    messages = [
        {"role": "system", "content": "تو یک کارشناس حقوقی هستی. فایل ارسالی را بررسی کن و نظر فنی بده."},
        {"role": "user", "content": f"این متن را بررسی کن و نظر فنی بده:\n{text[:4000]}"}
    ]
    # print(f"Extracted text: {text[:200]}")

    if not text.strip():
        return jsonify({'response': 'متن فایل خالی است.'})
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        temperature=0.3
    )

    reply = response.choices[0].message.content.strip()
    return jsonify({'response': reply})

if __name__ == '__main__':
    app.run(debug=True)
