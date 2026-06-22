// static/script.js
let itemCounter = 1;

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    // Автоматическое заполнение даты
    const today = new Date().toISOString().split('T')[0];
    const dateInput = document.getElementById('kp_date');
    if (dateInput && !dateInput.value) {
        dateInput.value = today;
    }
    
    // Инициализация расчета
    calculateTotals();
    updateRemoveButtons();
    
    // Обработчик отправки формы
    document.getElementById('offerForm').addEventListener('submit', function(e) {
        // Валидация
        if (!validateForm()) {
            e.preventDefault();
            return;
        }
        
        // Показываем загрузку
        const btn = document.getElementById('generateBtn');
        btn.disabled = true;
        btn.textContent = '⏳ Генерация...';
        
        // Восстанавливаем кнопку через 30 секунд (на случай ошибки)
        setTimeout(() => {
            btn.disabled = false;
            btn.textContent = '🚀 Сгенерировать КП';
        }, 30000);
    });
});

// Функция добавления позиции
function addItem() {
    const container = document.getElementById('itemsContainer');
    const row = document.createElement('div');
    row.className = 'item-row';
    row.id = `item_${itemCounter}`;
    
    row.innerHTML = `
        <input type="text" name="item_name[]" placeholder="Наименование" class="item-name" onchange="calculateTotals()">
        <input type="number" name="item_price[]" placeholder="Цена" class="item-price" step="0.01" oninput="calculateTotals()">
        <input type="number" name="item_qty[]" placeholder="Кол-во" class="item-qty" step="1" min="1" oninput="calculateTotals()">
        <span class="item-sum">0.00</span>
        <button type="button" class="remove-item" onclick="removeItem(this)">✕</button>
    `;
    
    container.appendChild(row);
    itemCounter++;
    calculateTotals();
    updateRemoveButtons();
}

// Функция удаления позиции
function removeItem(button) {
    const row = button.parentElement;
    const rows = document.querySelectorAll('.item-row');
    
    if (rows.length > 1) {
        row.remove();
        calculateTotals();
        updateRemoveButtons();
    } else {
        alert('Должна быть хотя бы одна позиция');
    }
}

// Обновление состояния кнопок удаления
function updateRemoveButtons() {
    const rows = document.querySelectorAll('.item-row');
    const buttons = document.querySelectorAll('.remove-item');
    
    buttons.forEach((btn, index) => {
        btn.disabled = rows.length <= 1;
    });
}

// Функция расчета итогов
function calculateTotals() {
    const rows = document.querySelectorAll('.item-row');
    let total = 0;
    let hasValidData = false;
    
    rows.forEach(row => {
        const nameInput = row.querySelector('.item-name');
        const priceInput = row.querySelector('.item-price');
        const qtyInput = row.querySelector('.item-qty');
        const sumSpan = row.querySelector('.item-sum');
        
        const price = parseFloat(priceInput.value) || 0;
        const qty = parseInt(qtyInput.value) || 0;
        const sum = price * qty;
        
        sumSpan.textContent = sum.toFixed(2);
        
        if (nameInput.value.trim() && price > 0 && qty > 0) {
            total += sum;
            hasValidData = true;
        }
    });
    
    const vatRate = parseFloat(document.getElementById('vat_rate').value) || 0;
    const vatAmount = total * (vatRate / 100);
    const grandTotal = total + vatAmount;
    
    document.getElementById('total_sum').value = total.toFixed(2);
    document.getElementById('vat_amount').value = vatAmount.toFixed(2);
    document.getElementById('grand_total').value = grandTotal.toFixed(2);
}

// Валидация формы перед отправкой
function validateForm() {
    // Проверяем обязательные поля
    const kpNumber = document.getElementById('kp_number').value.trim();
    const kpDate = document.getElementById('kp_date').value;
    const clientName = document.getElementById('client_name').value.trim();
    
    if (!kpNumber || !kpDate || !clientName) {
        alert('Пожалуйста, заполните все обязательные поля:\n- Номер КП\n- Дата КП\n- Клиент');
        return false;
    }
    
    // Проверяем наличие товаров
    const rows = document.querySelectorAll('.item-row');
    let hasValidItem = false;
    let errors = [];
    
    rows.forEach((row, index) => {
        const name = row.querySelector('.item-name').value.trim();
        const price = parseFloat(row.querySelector('.item-price').value) || 0;
        const qty = parseInt(row.querySelector('.item-qty').value) || 0;
        
        if (name && price > 0 && qty > 0) {
            hasValidItem = true;
        } else if (name || price > 0 || qty > 0) {
            // Если какие-то поля заполнены, но не все
            errors.push(`Строка ${index + 1}: заполните все поля или очистите их`);
        }
    });
    
    if (!hasValidItem) {
        alert('Добавьте хотя бы одну позицию с заполненными данными\n(наименование, цена > 0, количество > 0)');
        return false;
    }
    
    if (errors.length > 0) {
        alert('Обнаружены неполные данные:\n' + errors.join('\n'));
        return false;
    }
    
    return true;
}

// Функция для форматирования чисел
function formatNumber(num) {
    return num.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, " ");
}