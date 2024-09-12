import qrcode
from flask import Flask, request, render_template, send_file, redirect, url_for
from io import BytesIO
import base64
import datetime

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

# Página inicial para inserir o código Pix
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        codigo_pix = request.form.get('codigo_pix')
        valor = request.form.get('valor')
        codigo_base64 = codificar_pix(codigo_pix)  # Codifica o Pix
        return redirect(url_for('exibir_qrcode', code=codigo_base64, valor=valor))
    return render_template('index.html')

# Página que exibe o QR Code e os detalhes do Pix
@app.route('/exibir_qrcode')
def exibir_qrcode():
    codigo_base64 = request.args.get('code')
    valor = request.args.get('valor')
    codigo_pix = decodificar_pix(codigo_base64)  # Decodifica o Pix
    tempo_restante = datetime.datetime.now() + datetime.timedelta(minutes=10)  # 10 minutos
    return render_template('pix_page.html', codigo_pix=codigo_pix, valor=valor, tempo_restante=tempo_restante)

# Servir o QR code gerado como imagem
@app.route('/qr_code')
def qr_code():
    codigo_base64 = request.args.get('code')
    codigo_pix = decodificar_pix(codigo_base64)  # Decodifica o Pix
    buffer = gerar_qrcode_pix(codigo_pix)
    return send_file(buffer, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)