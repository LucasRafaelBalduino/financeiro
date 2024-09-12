from flask import Flask, request, render_template, redirect, url_for, send_file
from datetime import datetime, timedelta
import base64
import qrcode
from io import BytesIO

app = Flask(__name__)

# Função para codificar o código Pix com Base64
def codificar_pix(codigo_pix):
    return base64.urlsafe_b64encode(codigo_pix.encode()).decode()

# Função para decodificar o código Pix
def decodificar_pix(codigo_base64):
    return base64.urlsafe_b64decode(codigo_base64.encode()).decode()

# Função para gerar o QR code a partir do código Pix
def gerar_qrcode_pix(codigo_pix):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=8,
        border=4,
    )
    qr.add_data(codigo_pix)
    qr.make(fit=True)
    img_qr = qr.make_image(fill_color="black", back_color="white")
    
    buffer = BytesIO()
    img_qr.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer

# Página inicial para gerar o QR code
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        codigo_pix = request.form.get('codigo_pix')
        valor = request.form.get('valor')

        expiration_time = datetime.now() + timedelta(minutes=60)
        expiration_encoded = base64.urlsafe_b64encode(expiration_time.isoformat().encode()).decode()

        codigo_base64 = codificar_pix(codigo_pix)

        return redirect(url_for('exibir_qrcode', code=codigo_base64, exp=expiration_encoded, valor=valor))
    return render_template('index.html')

# Página que exibe o QR Code e os detalhes do Pix
@app.route('/exibir_qrcode')
def exibir_qrcode():
    codigo_base64 = request.args.get('code')
    valor = request.args.get('valor')
    expiration_encoded = request.args.get('exp')

    expiration_time = datetime.fromisoformat(base64.urlsafe_b64decode(expiration_encoded).decode())

    now = datetime.now()
    if now > expiration_time:
        return redirect(url_for('expired'))

    codigo_pix = decodificar_pix(codigo_base64)
    tempo_restante = (expiration_time - now).seconds
    return render_template('pix_page.html', codigo_pix=codigo_pix, valor=valor, tempo_restante=tempo_restante)

# Rota para exibir o QR code
@app.route('/qr_code')
def qr_code():
    codigo_base64 = request.args.get('code')
    codigo_pix = decodificar_pix(codigo_base64)
    
    buffer = gerar_qrcode_pix(codigo_pix)
    return send_file(buffer, mimetype='image/png')

# Página de expiração do pagamento
@app.route('/expired')
def expired():
    return render_template('expired.html'), 403

if __name__ == '__main__':
    app.run(debug=True)