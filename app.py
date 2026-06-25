import os
from datetime import datetime
from io import BytesIO
from flask import Flask, render_template, request, jsonify, send_file
from dotenv import load_dotenv
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import logging

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

logging.basicConfig(level=logging.DEBUG)

class OfferGenerator:
    """Класс для генерации коммерческих предложений"""
    
    def __init__(self):
        self.template_path = 'templates_pdf/template.pdf'
        self.register_fonts()
    
    def register_fonts(self):
        """Регистрация шрифтов для поддержки кириллицы"""
        try:
            font_paths = [
                'C:/Windows/Fonts/arial.ttf',
                'C:/Windows/Fonts/arialbd.ttf',
                '/System/Library/Fonts/Arial.ttf',
                '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
                '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf',
            ]

            for font_path in font_paths:
                if os.path.exists(font_path):
                    if 'Bold' in font_path or 'bd' in font_path:
                        pdfmetrics.registerFont(TTFont('FreeSansBold', font_path))
                    else:
                        pdfmetrics.registerFont(TTFont('FreeSans', font_path))
                    app.logger.info(f"Загружен шрифт: {font_path}")
                    return
            
            app.logger.warning("Русские шрифты не найдены, используется Helvetica")
            
        except Exception as e:
            app.logger.error(f"Ошибка загрузки шрифтов: {e}")
    
    def calculate_totals(self, items, vat_rate):
        """
        Расчет сумм, НДС и итогов
        """
        total_sum = 0
        calculated_items = []
        
        for item in items:
            try:
                price = float(item.get('price', 0))
                qty = int(item.get('qty', 0))
                item_sum = price * qty
                total_sum += item_sum
                
                calculated_items.append({
                    'name': item.get('name', 'Без названия'),
                    'price': price,
                    'qty': qty,
                    'sum': item_sum
                })
            except (ValueError, TypeError):
                continue
        
        vat_rate_decimal = float(vat_rate) / 100
        vat_amount = total_sum * vat_rate_decimal
        grand_total = total_sum + vat_amount
        
        return {
            'items': calculated_items,
            'total_sum': total_sum,
            'vat_amount': vat_amount,
            'grand_total': grand_total,
            'vat_rate': vat_rate
        }
    
    def generate_pdf(self, data):
        """
        Генерация PDF с данными
        """
        output_buffer = BytesIO()
        c = canvas.Canvas(output_buffer, pagesize=A4)
        width, height = A4

        try:
            pdfmetrics.registerFont(TTFont('FreeSans', 'C:/Windows/Fonts/arial.ttf'))
            pdfmetrics.registerFont(TTFont('FreeSansBold', 'C:/Windows/Fonts/arialbd.ttf'))
            font_name = 'FreeSans'
            font_name_bold = 'FreeSansBold'
        except:
            font_name = 'Helvetica'
            font_name_bold = 'Helvetica-Bold'
            app.logger.warning("Используется стандартный шрифт Helvetica")
        
        c.setFont(font_name_bold, 16)
        c.drawString(50, height - 50, "КОММЕРЧЕСКОЕ ПРЕДЛОЖЕНИЕ")
        
        c.setFont(font_name, 11)
        c.drawString(50, height - 80, f"КП № {data.get('kp_number', '')}")
        c.drawString(350, height - 80, f"от {data.get('kp_date', '')}")
        
        c.setFont(font_name, 11)
        c.drawString(50, height - 110, f"Клиент: {data.get('client_name', '')}")
        
        c.setFont(font_name, 10)
        preamble = data.get('preamble', '')
        y_position = height - 140
        if preamble:
            for line in preamble.split('\n'):
                if y_position < 100:
                    break
                if len(line) > 80:
                    line = line[:80] + '...'
                c.drawString(50, y_position, line)
                y_position -= 15
        else:
            c.drawString(50, y_position, "(Преамбула не указана)")
            y_position -= 15
        
        y_position -= 20

        c.setFont(font_name_bold, 10)
        c.drawString(50, y_position, "№")
        c.drawString(80, y_position, "Наименование")
        c.drawString(250, y_position, "Цена (руб)")
        c.drawString(340, y_position, "Кол-во")
        c.drawString(420, y_position, "Сумма")
        c.line(50, y_position - 5, 500, y_position - 5)
        
        y_position -= 20
        c.setFont(font_name, 9)
        
        items = data.get('items', [])
        
        if not items:
            c.drawString(80, y_position, "Нет позиций")
        else:
            for idx, item in enumerate(items, 1):
                if y_position < 100:
                    c.showPage()
                    y_position = height - 50
                    c.setFont(font_name_bold, 10)
                    c.drawString(50, y_position, "№")
                    c.drawString(80, y_position, "Наименование")
                    c.drawString(250, y_position, "Цена (руб)")
                    c.drawString(340, y_position, "Кол-во")
                    c.drawString(420, y_position, "Сумма")
                    c.line(50, y_position - 5, 500, y_position - 5)
                    y_position -= 20
                    c.setFont(font_name, 9)
                
                name = item.get('name', '')
                if not name or name.strip() == '':
                    name = f"Товар {idx}"
                
                if len(name) > 25:
                    name = name[:25] + '...'
                
                c.drawString(50, y_position, str(idx))
                c.drawString(80, y_position, name)
                c.drawString(250, y_position, f"{item['price']:.2f}")
                c.drawString(340, y_position, str(item['qty']))
                c.drawString(420, y_position, f"{item['sum']:.2f}")
                y_position -= 15
        
        y_position -= 10
        c.setFont(font_name_bold, 11)
        c.drawString(350, y_position, f"ИТОГО: {data.get('total_sum', 0):.2f} руб.")
        y_position -= 15
        c.drawString(350, y_position, f"НДС {data.get('vat_rate', 0)}%: {data.get('vat_amount', 0):.2f} руб.")
        y_position -= 15
        c.drawString(350, y_position, f"ВСЕГО к оплате: {data.get('grand_total', 0):.2f} руб.")
        
        y_position -= 30
        c.setFont(font_name, 10)
        delivery = data.get('delivery_time', '')
        if delivery:
            c.drawString(50, y_position, f"Срок поставки: {delivery}")
        else:
            c.drawString(50, y_position, "Срок поставки: не указан")
        y_position -= 15
        
        valid = data.get('valid_until', '')
        if valid:
            c.drawString(50, y_position, f"Предложение действует до: {valid}")
        else:
            c.drawString(50, y_position, "Предложение действует до: не указано")
        
        y_position = 50
        c.setFont(font_name, 10)
        manager = data.get('manager_name', '')
        if manager:
            c.drawString(50, y_position, f"Руководитель: {manager}")
        else:
            c.drawString(50, y_position, "Руководитель: _______________")
        c.drawString(350, y_position, "М.П.")
        c.line(50, y_position + 10, 200, y_position + 10)
        c.line(350, y_position + 10, 450, y_position + 10)
        
        c.save()
        output_buffer.seek(0)
        return output_buffer

@app.route('/')
def index():
    """Главная страница с формой"""
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_offer():
    """Генерация коммерческого предложения"""
    try:
        data = {
            'kp_number': request.form.get('kp_number', ''),
            'kp_date': request.form.get('kp_date', ''),
            'client_name': request.form.get('client_name', ''),
            'preamble': request.form.get('preamble', ''),
            'delivery_time': request.form.get('delivery_time', ''),
            'valid_until': request.form.get('valid_until', ''),
            'manager_name': request.form.get('manager_name', ''),
            'vat_rate': int(request.form.get('vat_rate', 22))
        }
        
        item_names = request.form.getlist('item_name[]')
        item_prices = request.form.getlist('item_price[]')
        item_qtys = request.form.getlist('item_qty[]')
        
        items = []
        for i in range(len(item_names)):
            name = item_names[i].strip() if i < len(item_names) else ''
            price = item_prices[i] if i < len(item_prices) else '0'
            qty = item_qtys[i] if i < len(item_qtys) else '0'
            
            if name:
                try:
                    items.append({
                        'name': name,
                        'price': float(price) if price else 0,
                        'qty': int(qty) if qty else 0
                    })
                except (ValueError, TypeError):
                    continue
        
        if not items:
            return jsonify({'error': 'Добавьте хотя бы одну позицию с названием'}), 400
        
        generator = OfferGenerator()
        
        totals = generator.calculate_totals(items, data['vat_rate'])
        
        full_data = {**data, **totals}
        
        pdf_buffer = generator.generate_pdf(full_data)
        
        filename = f"KP_{data['kp_number']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        app.logger.error(f"Ошибка: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)