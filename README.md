# Отвечаем на вопрос - "Какой язык учить?"

[![imageup.ru](https://imageup.ru/img10/4096774/programmirovanie-it-iumor-4061569.jpeg)](https://imageup.ru/img10/4096774/programmirovanie-it-iumor-4061569.jpeg.html)
## О проекте: 

Содержит один скрипт

`main.py` - собирает актуальную информацию по вакансиям с hh.ru и SuperJob.ru и выводит красивую табличку для мотивации.

_Критерии отбора:_
* Город - __Москва__
* Языки программирования - из __топ 15__(по мнению [github.com](https://habr.com/ru/post/310262/))
* Валюта - руб. 

How it looks.

[![imageup.ru](https://imageup.ru/img60/4096791/pycharm64_bfqdihva8a.png)](https://imageup.ru/img60/4096791/pycharm64_bfqdihva8a.png.html)

## Как подготовить проект к запуску

1. Создайте файл  `.env`  в директории проекта.
2. В файл  `.env`  добавьте строки со значениями:
   - `SUPER_JOB_KEY="Ваш API ключ"`

#### Как получить API key:

1. Переходим на сайт [SuperJob.ru](https://api.superjob.ru/);
2. Кликаем по вкладке ["Зарегистрировать приложение"](https://www.superjob.ru/auth/login/?returnUrl=https://api.superjob.ru/register/);
3. Заполнить форму, можно писать от балды;[![imageup.ru](https://imageup.ru/img212/4096852/chrome_tzw5co8zwg.png)](https://imageup.ru/img212/4096852/chrome_tzw5co8zwg.png.html)
4. После регистрации приложения, будет доступен секретный ключ.[![imageup.ru](https://imageup.ru/img68/4103417/chrome_riedduefyj.png)](https://imageup.ru/img68/4103417/chrome_riedduefyj.png.html)


## Как запустить скрипт

```python
python main.py
```

## Требования к окружению

Python3 должен быть уже установлен.
Затем используйте pip (или pip3, есть конфликт с Python2) для установки зависимостей:

```python
pip install -r requirements.txt
```


