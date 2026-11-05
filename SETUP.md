# Installation / Обновление профиля

1. Распакуй архив и открой свой публичный репозиторий `https://github.com/vanrit/vanrit` (создай его, если ещё нет).
2. Загрузи **все файлы, сохранив пути**: `README.md`, `assets/*.svg`, `scripts/build_contributions.py`, `.github/workflows/contributions.yml`. Скрытая папка `.github` важна. Удобно загрузить всё через `git`, а не веб-перетаскивание.
3. Открой вкладку **Actions → Update contribution calendar → Run workflow**. Если Actions отключены, включи их в настройках репозитория.
4. После успешного выполнения workflow изображение `assets/contributions.svg` заполнится **реальными данными** за последний год. Затем будет обновляться ежедневно по расписанию.

## Загрузка через терминал

Если репозиторий уже существует, из папки проекта выполните (укажите правильный путь к распакованному каталогу):

```bash
git clone https://github.com/vanrit/vanrit.git
cp -R vanrit-pixel-profile/. vanrit/
cd vanrit
git add README.md assets scripts .github/workflows/contributions.yml
git commit -m "style: refresh profile readme"
git push
```

Если workflow не может запушить SVG, проверьте **Settings → Actions → General → Workflow permissions**, что у него разрешена запись. YAML уже запрашивает `contents: write`, но ограничения организации/репозитория могут переопределять это.

Примечание: GitHub стандартные pinned-карточки и календарь остаются без изменений. Здесь стилизованы дополнительные блоки внутри README. Карточки и баннер — локальные SVG; никаких внешних stats-сервисов нет.
