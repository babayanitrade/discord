from flask import Flask, request, render_template
import datetime
from threading import Thread, Event

# Flask Uygulaması
app = Flask(__name__)
logs = []  # Gelen istekleri saklamak için bir liste

# Threading event for stopping the Flask thread
flask_stop_event = Event()

def run_flask():
    """Flask uygulamasını başlatır."""
    while not flask_stop_event.is_set():
        app.run(host="0.0.0.0", port=5000, debug=False)

@app.route('/')
def home():
    """Ana sayfa: Gelen webhook isteklerini gösterir."""
    return render_template("index.html", logs=logs)

@app.route('/webhook', methods=['POST'])
def webhook():
    """Dışarıdan gelen istekleri dinler ve loglar."""
    try:
        data = request.json
        message = f"📩 Yeni Webhook Mesajı: {data}"
        logs.insert(0, {"message": message, "timestamp": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
        return {"status": "success", "message": "Webhook alındı."}, 200
    except Exception as e:
        print(f"❌ Webhook işlenirken hata oluştu: {str(e)}")
        return {"status": "error", "message": str(e)}, 400

# Flask'i farklı bir threadde çalıştır
flask_thread = Thread(target=run_flask, daemon=True)
flask_thread.start()
