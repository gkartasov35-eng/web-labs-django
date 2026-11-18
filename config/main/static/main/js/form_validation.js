document.addEventListener('DOMContentLoaded', function() {
    var form = document.getElementById('authForm');
    if (!form) return;
    var inputs = form.querySelectorAll('input[type="text"], input[type="email"], input[type="password"]');

    // Конструктор валидатора для одного поля
    function CustomValidation() {
        this.invalidities = [];
    }

    CustomValidation.prototype = {
        checkValidity: function(input) {
            var val = input.value.trim();
            var type = input.getAttribute('type');
            var name = input.getAttribute('name');

            // проверка обязательного поля
            if (input.required && val === '') this.addInvalidity('Поле обязательно для заполнения');

            // специальные проверки
            if (name === 'first_name' || name === 'last_name') {
                if (!/^[A-ZА-ЯЁ][a-zа-яё]+$/.test(val)) {
                    this.addInvalidity('Должно начинаться с заглавной буквы и содержать только буквы');
                }
                if (val.length < 2) this.addInvalidity('Минимум 2 символа');
            }

            if (name === 'username') {
                if (val.length < 3) this.addInvalidity('Username минимум 3 символа');
            }

            if (type === 'email') {
                if (val && !/^[\w.-]+@[\w.-]+\.\w{2,}$/.test(val)) {
                    this.addInvalidity('Неверный формат email');
                }
            }

            if (type === 'password') {
                if (val.length < 8) this.addInvalidity('Пароль минимум 8 символов');
                if (name === 'password2' && input.value !== form.elements.password1.value) {
                    this.addInvalidity('Пароли не совпадают');
                }
            }
        },
        addInvalidity: function(msg) { this.invalidities.push(msg); },
        getInvaliditiesForHTML: function() { return this.invalidities.join('. <br>'); }
    };

    // удаляем все старые ошибки
    function removeOldErrors() {
        var old = form.querySelectorAll('.error-message');
        old.forEach(function(e){ e.remove(); });
    }

    // при отправке формы
    form.addEventListener('submit', function(e) {
        removeOldErrors();
        var stopSubmit = false;

        inputs.forEach(function(input) {
            var validator = new CustomValidation();
            validator.checkValidity(input);

            // удаляем подсветку от предыдущего раза
            input.classList.remove('error');

            if (validator.invalidities.length > 0) {
                var messagesHTML = validator.getInvaliditiesForHTML();
                input.insertAdjacentHTML('afterend', '<p class="error-message">' + messagesHTML + '</p>');
                input.classList.add('error');
                stopSubmit = true;
            }
        });

        if (stopSubmit) e.preventDefault();
    });

    // валидация в реальном времени
    inputs.forEach(function(input) {
        input.addEventListener('input', function() {
            var validator = new CustomValidation();
            validator.checkValidity(input);

            // убираем старые ошибки рядом с полем
            var next = input.nextElementSibling;
            if (next && next.classList.contains('error-message')) next.remove();
            input.classList.remove('error');

            if (validator.invalidities.length > 0) {
                var messagesHTML = validator.getInvaliditiesForHTML();
                input.insertAdjacentHTML('afterend', '<p class="error-message">' + messagesHTML + '</p>');
                input.classList.add('error');
            }
        });
    });
});
