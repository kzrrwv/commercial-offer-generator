# create_template.py
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import os

def create_temp_template():
    """Создает временный PDF-шаблон с плейсхолдерами"""
    
    os.makedirs('templates_pdf', exist_ok=True)
    
    c = canvas.Canvas("templates_pdf/template.pdf", pagesize=A4)
    width, height = A4
    
    c.setFont("Helvetica", 10)
    
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "КОММЕРЧЕСКОЕ ПРЕДЛОЖЕНИЕ")
    
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 80, "КП № {{kp_number}}")
    c.drawString(350, height - 80, "от {{kp_date}}")
    
    c.drawString(50, height - 110, "Клиент: {{client_name}}")

    c.setFont("Helvetica", 9)
    c.drawString(50, height - 140, "{{preamble}}")
    
    y = height - 180
    c.setFont("Helvetica-Bold", 9)
    c.drawString(50, y, "№")
    c.drawString(80, y, "Наименование")
    c.drawString(250, y, "Цена (руб)")
    c.drawString(340, y, "Кол-во")
    c.drawString(420, y, "Сумма")

    c.line(50, y-5, 500, y-5)
    
    y -= 20
    c.setFont("Helvetica", 9)
    for i in range(1, 16):
        c.drawString(50, y, str(i))
        c.drawString(80, y, f"{{{{item{i}_name}}}}")
        c.drawString(250, y, f"{{{{item{i}_price}}}}")
        c.drawString(340, y, f"{{{{item{i}_qty}}}}")
        c.drawString(420, y, f"{{{{item{i}_sum}}}}")
        y -= 15

    y -= 10
    c.setFont("Helvetica-Bold", 10)
    c.drawString(350, y, "ИТОГО:")
    c.drawString(420, y, "{{total_sum}}")
    
    y -= 15
    c.drawString(350, y, "НДС {{vat_rate}}%:")
    c.drawString(420, y, "{{vat_amount}}")
    
    y -= 15
    c.drawString(350, y, "ВСЕГО к оплате:")
    c.drawString(420, y, "{{grand_total}}")
    
    y -= 30
    c.setFont("Helvetica", 9)
    c.drawString(50, y, "Срок поставки: {{delivery_time}}")
    y -= 15
    c.drawString(50, y, "Предложение действует до: {{valid_until}}")
    
    y = 50
    c.drawString(50, y, "Руководитель: {{manager_name}}")
    c.drawString(350, y, "М.П.")
    c.line(50, y+10, 200, y+10)
    c.line(350, y+10, 450, y+10)
    
    c.save()
    print("✅ Временный PDF-шаблон создан!")
    print(f"📁 Файл: templates_pdf/template.pdf")
    print("📝 Плейсхолдеры готовы к использованию")

if __name__ == "__main__":
    create_temp_template()