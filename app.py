# app.py - ИСПРАВЛЕННЫЙ (итоги строго под таблицей)
import os
from datetime import datetime
from io import BytesIO
from flask import Flask, render_template, request, jsonify, send_file
from dotenv import load_dotenv
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
import logging

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

OUTPUT_FOLDER = 'output'
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

logging.basicConfig(level=logging.INFO)

def get_russian_font():
    font_paths = [
        'C:/Windows/Fonts/arial.ttf',
        'C:/Windows/Fonts/arialbd.ttf',
        '/System/Library/Fonts/Arial.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
    ]
    
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont('RussianFont', font_path))
                return 'RussianFont'
            except:
                continue
    return 'Helvetica'

RUSSIAN_FONT = get_russian_font()

class BrandColors:
    PRIMARY = colors.HexColor('#1a3a6a')
    SECONDARY = colors.HexColor('#3b82f6')
    ACCENT = colors.HexColor('#0a0a0a')
    LIGHT = colors.HexColor('#f0f4ff')
    WHITE = colors.white
    GREY = colors.HexColor('#555555')

class OfferGenerator:
    def __init__(self):
        self.font_name = RUSSIAN_FONT
        self.font_name_bold = RUSSIAN_FONT
        self.colors = BrandColors()
        self.logo_path = 'static/logo.png'
    
    def calculate_totals(self, items, vat_rate):
        total_sum = 0
        calculated_items = []
        for item in items:
            try:
                price = float(item.get('price', 0))
                qty = int(item.get('qty', 0))
                item_sum = price * qty
                total_sum += item_sum
                calculated_items.append({
                    'name': item.get('name', ''),
                    'price': price,
                    'qty': qty,
                    'sum': item_sum
                })
            except:
                continue
        
        vat_amount = total_sum * (float(vat_rate) / 100)
        grand_total = total_sum + vat_amount
        
        return {
            'items': calculated_items,
            'total_sum': total_sum,
            'vat_amount': vat_amount,
            'grand_total': grand_total,
            'vat_rate': vat_rate
        }
    
    def generate_pdf(self, data):
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        colors = self.colors
        font = self.font_name
        font_bold = self.font_name_bold
        
        left_x = 50
        col_widths = [30, 165, 80, 60, 90]
        table_width = sum(col_widths)
        
        c.setFillColor(colors.WHITE)
        c.rect(0, 0, width, height, fill=1)
        
        c.setFillColor(colors.PRIMARY)
        c.rect(0, height - 15, width, 15, fill=1)
        
        if os.path.exists(self.logo_path):
            try:
                logo = ImageReader(self.logo_path)
                c.drawImage(logo, 50, height - 85, width=150, height=55, preserveAspectRatio=True)
            except:
                pass
        
        c.setFont(font, 9)
        c.setFillColor(colors.GREY)
        if data.get('company_phone'):
            c.drawString(400, height - 45, f"Тел: {data['company_phone']}")
        if data.get('company_email'):
            c.drawString(400, height - 60, f"Email: {data['company_email']}")
        
        c.setFont(font, 10)
        c.setFillColor(colors.GREY)
        c.drawString(50, height - 120, f"КП № {data.get('kp_number', '')}")
        c.drawString(400, height - 120, f"от {data.get('kp_date', '')}")
        
        c.setFont(font_bold, 22)
        c.setFillColor(colors.PRIMARY)
        c.drawString(50, height - 155, "КОММЕРЧЕСКОЕ ПРЕДЛОЖЕНИЕ")
        c.setStrokeColor(colors.SECONDARY)
        c.setLineWidth(2)
        c.line(50, height - 165, 500, height - 165)
        
        c.setFont(font_bold, 12)
        c.setFillColor(colors.ACCENT)
        client = data.get('client_name', '')
        if client:
            c.drawString(50, height - 195, f"Уважаемый(ая) {client}!")

        c.setFont(font, 10)
        c.setFillColor(colors.GREY)
        preamble = data.get('preamble_text', '')
        if not preamble:
            preamble = "Благодарим за интерес к нашей продукции."
        
        y = height - 215
        for line in preamble.split('\n'):
            if y < 200:
                break
            if len(line) > 80:
                line = line[:80] + '...'
            c.drawString(50, y, line)
            y -= 15
        
        y -= 10
        
        c.setFillColor(colors.LIGHT)
        c.rect(left_x, y - 15, table_width, 20, fill=1, stroke=0)
        c.setFillColor(colors.PRIMARY)
        c.setFont(font_bold, 10)
        
        headers = ["№", "Наименование", "Цена (руб)", "Кол-во", "Сумма"]
        x = left_x
        for i, header in enumerate(headers):
            c.drawString(x + 5, y, header)
            x += col_widths[i]
        
        c.setStrokeColor(colors.PRIMARY)
        c.setLineWidth(1)
        c.line(left_x, y - 5, left_x + table_width, y - 5)
        
        y -= 25
        
        c.setFont(font, 9)
        c.setFillColor(colors.ACCENT)
        
        items = data.get('items', [])
        
        if not items:
            c.drawString(left_x + 10, y, "Нет позиций")
            y -= 18
        else:
            for idx, item in enumerate(items, 1):
                if y < 80:
                    c.showPage()
                    y = height - 50
                    # Перерисовываем заголовки
                    c.setFillColor(colors.LIGHT)
                    c.rect(left_x, y - 15, table_width, 20, fill=1, stroke=0)
                    c.setFillColor(colors.PRIMARY)
                    c.setFont(font_bold, 10)
                    x = left_x
                    for i, header in enumerate(headers):
                        c.drawString(x + 5, y, header)
                        x += col_widths[i]
                    c.line(left_x, y - 5, left_x + table_width, y - 5)
                    y -= 20
                    c.setFont(font, 9)
                    c.setFillColor(colors.ACCENT)
                
                if idx % 2 == 0:
                    c.setFillColor(colors.LIGHT)
                    c.rect(left_x, y - 12, table_width, 16, fill=1, stroke=0)
                    c.setFillColor(colors.ACCENT)
                
                name = item.get('name', '')[:22]
                if len(item.get('name', '')) > 22:
                    name += '...'
                
                x = left_x
                c.drawString(x + 5, y, str(idx))
                x += col_widths[0]
                c.drawString(x + 5, y, name)
                x += col_widths[1]
                c.drawString(x + 5, y, f"{item.get('price', 0):.2f}")
                x += col_widths[2]
                c.drawString(x + 5, y, str(item.get('qty', 0)))
                x += col_widths[3]
                c.drawString(x + 5, y, f"{item.get('sum', 0):.2f}")
                
                y -= 18
        
        y -= 50
        
        total_sum = data.get('total_sum', 0)
        vat_amount = data.get('vat_amount', 0)
        grand_total = data.get('grand_total', 0)
        vat_rate = data.get('vat_rate', 0)
        
        c.setFillColor(colors.LIGHT)
        c.rect(310, y - 15, 210, 55, fill=1, stroke=0)
        c.setStrokeColor(colors.PRIMARY)
        c.setLineWidth(1)
        c.rect(310, y - 15, 210, 55, fill=0, stroke=1)
        
        c.setFont(font_bold, 10)
        c.setFillColor(colors.PRIMARY)
        c.drawString(320, y + 25, f"ИТОГО: {total_sum:.2f} руб.")
        c.drawString(320, y + 10, f"НДС {vat_rate}%: {vat_amount:.2f} руб.")
        c.setFont(font_bold, 12)
        c.setFillColor(colors.SECONDARY)
        c.drawString(320, y - 5, f"ВСЕГО к оплате: {grand_total:.2f} руб.")
        
        y -= 55
        
        c.setFont(font, 10)
        c.setFillColor(colors.GREY)
        
        delivery = data.get('delivery_term', '')
        valid = data.get('valid_until', '')
        
        if delivery:
            c.drawString(50, y, f"Срок поставки: {delivery}")
            y -= 18
        if valid:
            c.drawString(50, y, f"Предложение действует до: {valid}")
            y -= 18
        
        y = 70
        c.setFont(font, 10)
        c.setFillColor(colors.ACCENT)
        director = data.get('director_name', '')
        if director:
            c.drawString(50, y, f"Руководитель: {director}")
        else:
            c.drawString(50, y, "Руководитель: _______________")
        
        c.drawString(400, y, "М.П.")
        c.line(50, y + 10, 200, y + 10)
        c.line(400, y + 10, 460, y + 10)
        
        c.setFont(font, 8)
        c.setFillColor(colors.GREY)
        c.drawString(50, 30, f"Сгенерировано: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
        c.drawString(420, 30, "Страница 1/1")
        
        c.setFillColor(colors.PRIMARY)
        c.rect(0, 0, width, 5, fill=1)
        
        c.save()
        buffer.seek(0)
        return buffer


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_offer():
    try:
        form_data = {
            'kp_number': request.form.get('kp_number', ''),
            'kp_date': request.form.get('kp_date', ''),
            'client_name': request.form.get('client_name', ''),
            'preamble': request.form.get('preamble', ''),
            'delivery_time': request.form.get('delivery_time', ''),
            'valid_until': request.form.get('valid_until', ''),
            'manager_name': request.form.get('manager_name', ''),
            'company_phone': request.form.get('company_phone', ''),
            'company_email': request.form.get('company_email', ''),
            'vat_rate': int(request.form.get('vat_rate', 22))
        }
        
        item_names = request.form.getlist('item_name[]')
        item_prices = request.form.getlist('item_price[]')
        item_qtys = request.form.getlist('item_qty[]')
        
        items = []
        for i in range(len(item_names)):
            name = item_names[i].strip() if i < len(item_names) else ''
            if name:
                try:
                    items.append({
                        'name': name,
                        'price': float(item_prices[i]) if i < len(item_prices) else 0,
                        'qty': int(item_qtys[i]) if i < len(item_qtys) else 0
                    })
                except:
                    continue
        
        if not items:
            return jsonify({'error': 'Добавьте хотя бы одну позицию'}), 400
        
        generator = OfferGenerator()
        totals = generator.calculate_totals(items, form_data['vat_rate'])
        
        pdf_data = {
            **form_data,
            'preamble_text': form_data['preamble'],
            'delivery_term': form_data['delivery_time'],
            'director_name': form_data['manager_name'],
            **totals
        }
        
        pdf_buffer = generator.generate_pdf(pdf_data)
        
        filename = f"KP_{form_data['kp_number']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(OUTPUT_FOLDER, filename)
        
        with open(filepath, 'wb') as f:
            f.write(pdf_buffer.getvalue())
        
        return send_file(
            filepath,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        app.logger.error(f"Ошибка: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)