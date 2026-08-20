# Инъекции и XSS: как проверять и предотвращать

## SQL-инъекции
Причина всегда одна — пользовательский ввод попадает в запрос как текст,
а не как параметр.
```python
# Плохо — конкатенация строк
cursor.execute(f"SELECT * FROM users WHERE email = '{email}'")

# Хорошо — параметризованный запрос
cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
```
ORM (SQLAlchemy, Django ORM, Hibernate) сами параметризуют запросы через
стандартный API — уязвимость обычно появляется, когда кто-то обходит ORM
через raw SQL с f-строкой ради «производительности» или «гибкости».

## NoSQL-инъекции
MongoDB и подобные тоже уязвимы, если оператор запроса собирается из
пользовательского JSON без валидации:
```javascript
// Опасно: {"$gt": ""} в password обойдёт проверку
db.users.find({ email: input.email, password: input.password })
```
Фикс — явно приводить типы полей (`String(input.password)`) и не доверять
структуре входящего JSON целиком.

## XSS (Cross-Site Scripting)
Три вида:
- **Stored** — вредоносный скрипт сохраняется в базе (комментарий,
  профиль) и выполняется у каждого, кто откроет страницу.
- **Reflected** — скрипт приходит в самом запросе (параметр URL) и сразу
  отражается в ответе без сохранения.
- **DOM-based** — уязвимость целиком на клиенте: JS сам вставляет
  необработанный ввод в DOM через `innerHTML`.

## Защита от XSS
```javascript
// Опасно
element.innerHTML = userComment;

// Безопасно — экранирует автоматически
element.textContent = userComment;

// React/Vue по умолчанию экранируют интерполяцию {}, но:
<div dangerouslySetInnerHTML={{__html: userComment}} />  // React — опасно
<div v-html="userComment"></div>                          // Vue — опасно
```
Если действительно нужно рендерить HTML от пользователя (markdown-редактор
и т.п.) — обязательна санитизация через библиотеку (`DOMPurify` на фронте,
`bleach` в Python), не самописный regex-фильтр тегов.

## Content Security Policy (CSP)
Дополнительный уровень защиты — заголовок, ограничивающий, откуда браузер
может грузить скрипты:
```
Content-Security-Policy: default-src 'self'; script-src 'self' https://trusted-cdn.com
```
CSP не заменяет санитизацию ввода, но резко снижает ущерб от пропущенной
XSS — инжектированный `<script>` с внешнего домена просто не выполнится.

## Инструменты проверки
- SAST: Semgrep (правила `p/owasp-top-ten`), CodeQL;
- ручная проверка: искать в кодовой базе `innerHTML`, `dangerouslySetInnerHTML`,
  `v-html`, raw SQL со строковой конкатенацией — это первые кандидаты на
  code review при виде такого паттерна.
