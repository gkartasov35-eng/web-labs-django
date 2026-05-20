document.addEventListener('DOMContentLoaded', function() {
    var form = document.getElementById('authForm'); // id вашей формы
    var inputs = form.querySelectorAll('input[type="text"], input[type="email"], input[type="password"]');
    var submit = form.querySelector('button[type="submit"]');

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
            if (name === 'firstName' || name === 'lastName') {
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
                if (val.length < 6) this.addInvalidity('Пароль минимум 6 символов');
            }
        },
        addInvalidity: function(msg) { this.invalidities.push(msg); },
        getInvaliditiesForHTML: function() { return this.invalidities.join('. <br>'); }
    };

    // удаляем все старые ошибки
    function removeOldErrors() {
        var old = document.querySelectorAll('.error-message');
        old.forEach(function(e){ e.remove(); });
    }

    // при отправке формы
    submit.addEventListener('click', function(e) {
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