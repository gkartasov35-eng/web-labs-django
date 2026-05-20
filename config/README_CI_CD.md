# CI/CD для проекта

В проект добавлен GitHub Actions workflow:

```text
.github/workflows/ci-cd.yml
```

Он выполняет две основные стадии.

## CI — Continuous Integration

При каждом `push` или `pull_request` GitHub Actions:

1. устанавливает Python 3.12;
2. устанавливает зависимости из `requirements.txt`;
3. запускает `python manage.py check`;
4. применяет миграции `python manage.py migrate --noinput`;
5. запускает тесты `python manage.py test`;
6. собирает Docker-образ проекта.

Это доказывает, что проект собирается и проходит автоматическую проверку.

## CD — Continuous Delivery / Deployment

После успешного CI на ветке `main` или `master` workflow пытается вызвать Render Deploy Hook.

Для настоящего автоматического деплоя нужно добавить в GitHub:

```text
Settings -> Secrets and variables -> Actions -> New repository secret
```

Название секрета:

```text
RENDER_DEPLOY_HOOK_URL
```

Значение — Deploy Hook URL из Render.

Если этот секрет не добавлен, CD-шаг не падает с ошибкой, а просто пишет, что деплой пропущен. Это удобно для учебной защиты: CI/CD-файл есть, CI работает, а CD можно включить после подключения Render.

## Что сказать на защите

> В проект добавлен CI/CD через GitHub Actions. CI автоматически проверяет Django-проект: устанавливает зависимости, запускает `manage.py check`, применяет миграции, запускает тесты и собирает Docker-образ. CD реализован через Render Deploy Hook: после успешной проверки на ветке main/master workflow может автоматически отправить команду на деплой в Render.
