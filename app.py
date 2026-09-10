import io
import json
import urllib.parse
import qrcode
import random
import string
from flask import Flask, render_template, request, send_file, redirect, url_for
from PIL import Image, ImageDraw, ImageFont
from pypdf import PdfWriter

app = Flask(__name__)

url_db = {}

@app.route('/')
def home():
    return render_template('index.html')

# 1. AI Image Generator
@app.route('/ai-image', methods=['GET', 'POST'])
def ai_image():
    image_url = None
    prompt = ""
    if request.method == 'POST':
        prompt = request.form.get('prompt', '')
        if prompt:
            encoded_prompt = urllib.parse.quote(prompt)
            image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true"
    return render_template('ai_image.html', image_url=image_url, prompt=prompt)

# 2. Image Converter
@app.route('/image-converter', methods=['GET', 'POST'])
def image_converter():
    if request.method == 'POST':
        file = request.files.get('image')
        target_format = request.form.get('format', 'JPEG').upper()
        if file and file.filename != '':
            img = Image.open(file.stream)
            if target_format == 'JPEG' and img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            img_io = io.BytesIO()
            img.save(img_io, format=target_format, quality=90)
            img_io.seek(0)
            ext = 'jpg' if target_format == 'JPEG' else target_format.lower()
            return send_file(img_io, mimetype=f"image/{ext}", as_attachment=True, download_name=f"converted.{ext}")
    return render_template('image_converter.html')

# 3. Image Resizer
@app.route('/image-resizer', methods=['GET', 'POST'])
def image_resizer():
    if request.method == 'POST':
        file = request.files.get('image')
        width = int(request.form.get('width', 800))
        height = int(request.form.get('height', 600))
        if file and file.filename != '':
            img = Image.open(file.stream)
            resized_img = img.resize((width, height))
            img_io = io.BytesIO()
            fmt = img.format if img.format else 'PNG'
            resized_img.save(img_io, format=fmt)
            img_io.seek(0)
            return send_file(img_io, mimetype=f"image/{fmt.lower()}", as_attachment=True, download_name=f"resized_{width}x{height}.{fmt.lower()}")
    return render_template('image_resizer.html')

# 4. QR Code Generator
@app.route('/qr-generator', methods=['GET', 'POST'])
def qr_generator():
    if request.method == 'POST':
        text = request.form.get('text', '')
        if text:
            img = qrcode.make(text)
            img_io = io.BytesIO()
            img.save(img_io, 'PNG')
            img_io.seek(0)
            return send_file(img_io, mimetype="image/png", as_attachment=True, download_name="qrcode.png")
    return render_template('qr_generator.html')

# 5. Image to PDF
@app.route('/image-to-pdf', methods=['GET', 'POST'])
def image_to_pdf():
    if request.method == 'POST':
        files = request.files.getlist('images')
        if files:
            img_list = []
            for file in files:
                if file.filename != '':
                    img = Image.open(file.stream).convert('RGB')
                    img_list.append(img)
            if img_list:
                pdf_io = io.BytesIO()
                img_list[0].save(pdf_io, format='PDF', save_all=True, append_images=img_list[1:])
                pdf_io.seek(0)
                return send_file(pdf_io, mimetype='application/pdf', as_attachment=True, download_name='converted.pdf')
    return render_template('image_to_pdf.html')

# 6. PDF Merger
@app.route('/pdf-merger', methods=['GET', 'POST'])
def pdf_merger():
    if request.method == 'POST':
        files = request.files.getlist('pdfs')
        if files:
            merger = PdfWriter()
            for file in files:
                if file.filename != '' and file.filename.endswith('.pdf'):
                    merger.append(file)
            pdf_io = io.BytesIO()
            merger.write(pdf_io)
            pdf_io.seek(0)
            return send_file(pdf_io, mimetype='application/pdf', as_attachment=True, download_name='merged.pdf')
    return render_template('pdf_merger.html')

# 7. URL Shortener
@app.route('/url-shortener', methods=['GET', 'POST'])
def url_shortener():
    short_url = None
    if request.method == 'POST':
        original_url = request.form.get('url', '').strip()
        if original_url:
            if not original_url.startswith(('http://', 'https://')):
                original_url = 'https://' + original_url
            code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
            url_db[code] = original_url
            short_url = request.host_url + 's/' + code
    return render_template('url_shortener.html', short_url=short_url)

@app.route('/s/<code>')
def redirect_short_url(code):
    original_url = url_db.get(code)
    if original_url:
        return redirect(original_url)
    return "URL Not Found", 404

# 8. Text Case Converter
@app.route('/text-converter', methods=['GET', 'POST'])
def text_converter():
    text = ""
    stats = {}
    if request.method == 'POST':
        text = request.form.get('text', '')
        action = request.form.get('action', '')
        
        if action == 'uppercase':
            text = text.upper()
        elif action == 'lowercase':
            text = text.lower()
        elif action == 'titlecase':
            text = text.title()
            
        words = len(text.split())
        chars = len(text)
        lines = len(text.splitlines()) if text else 0
        stats = {'words': words, 'chars': chars, 'lines': lines}
        
    return render_template('text_converter.html', text=text, stats=stats)

# 9. Color Picker
@app.route('/color-picker')
def color_picker():
    return render_template('color_picker.html')

# NEW 10. Unit Converter
@app.route('/unit-converter')
def unit_converter():
    return render_template('unit_converter.html')

# NEW 11. Timer & Stopwatch
@app.route('/timer')
def timer():
    return render_template('timer.html')

# NEW 12. Watermark Adder
@app.route('/watermark', methods=['GET', 'POST'])
def watermark():
    if request.method == 'POST':
        file = request.files.get('image')
        wm_text = request.form.get('watermark_text', 'Watermark')
        if file and file.filename != '':
            img = Image.open(file.stream).convert("RGBA")
            txt_layer = Image.new("RGBA", img.size, (255, 255, 255, 0))
            draw = ImageDraw.Draw(txt_layer)
            
            # Text size relative to image height
            font_size = int(img.height * 0.05)
            font_size = max(font_size, 20)
            
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except IOError:
                font = ImageFont.load_default()

            # Place at bottom-right with margin
            margin = 20
            draw.text((img.width - margin - (len(wm_text) * (font_size * 0.5)), img.height - margin - font_size), wm_text, fill=(255, 255, 255, 128), font=font)
            
            watermarked = Image.alpha_composite(img, txt_layer).convert("RGB")
            
            img_io = io.BytesIO()
            watermarked.save(img_io, 'JPEG', quality=95)
            img_io.seek(0)
            return send_file(img_io, mimetype="image/jpeg", as_attachment=True, download_name="watermarked.jpg")
            
    return render_template('watermark.html')

# NEW 13. JSON Formatter & Validator
@app.route('/json-formatter', methods=['GET', 'POST'])
def json_formatter():
    formatted_json = ""
    error = None
    raw_json = ""
    if request.method == 'POST':
        raw_json = request.form.get('json_data', '')
        try:
            parsed = json.loads(raw_json)
            formatted_json = json.dumps(parsed, indent=4)
        except Exception as e:
            error = f"Invalid JSON: {str(e)}"
    return render_template('json_formatter.html', formatted_json=formatted_json, error=error, raw_json=raw_json)

if __name__ == '__main__':
    app.run(debug=True, port=5000)