Исправлено подключение static-файлов.

Главная правка:
- config/templates/base.html теперь подключает CSS как {% static 'css/style.css' %}
- JS подключён как {% static 'main/js/form_validation.js' %}

После замены файлов сделай:
cd "папка_проекта"
git add .
git commit -m "Fix static files paths"
git push

Потом на Render: Manual Deploy -> Deploy latest commit.
