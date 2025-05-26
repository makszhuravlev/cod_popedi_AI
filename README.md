# Искусство через призму военных лет

Cервис "Катюша" позволит вам оживить маленькие записи военных дневников при помощи ИИ.<!-- описание репозитория -->
<!--Блок информации о репозитории в бейджах-->
![GitHub top language](https://img.shields.io/github/languages/top/makszhuravlev/cod_popedi_AI)
<!--Установка-->
## Установка (Linux)
Сначала клонирование репозитория

```git clone https://github.com/makszhuravlev/cod_popedi_AI```
### Backend

1. Переход в директорию Api

```cd Api```

2. Собираем базу данных

```docker run --name BDschka -v ../BD:/BDdata -e POSTGRES_PASSWORD=123 -d postgres:17.5-alpine3.21```

3. Настраиваем базу данных

```
docker exec -it BDschka psql -U postgres
apk add sudo
sudo -u postgres psql
CREATE ROLE "Adept0mSimerol1S" WITH LOGIN PASSWORD 'AveImperium!';
ALTER ROLE "Adept0mSimerol1S" WITH SUPERUSER;
sudo -u postgres createdb cod_pobedi_ai
sudo -u postgres psql -d cod_pobedi_ai -f /BDdata/dump_without_data.sql
\q
exit
```

4. Запустить бекенд

```docker compose build && docker compose up```

5. Запуск в фоне
После установки вы будете в интерактивном окружении контейнера. Из него нужно выйти и запустить контейнер. Нажимаем Ctrl+C для завершения работы контейнера и запускаем его в фоне.
```docker start cumBack-API```
### Frontend

1. Переход в директорию frontik

```cd ../frontik```

2. Запустите контейнер

```docker compose build && docker compose up```

3. Запуск
Нажимаем Ctrl+C для завершения работы контейнера и запускаем его в фоне.
```docker start frontik```
### ИИшка

Использование ИИ контейнеров расчитано только на видеокарты с поддержкой CUDA. Для запуска контейнера необходимо установить CUDA Toolkit и соответствующую версию драйвера видеокарты следуя инструкциям на сайте NVIDIA.
Если вы, как и мы, везунчик использующий Alt Linux, то вам необходимо установить epm
```apt-get update &&apt-get install epm```
И выпонить скрипт
```bash<(curl https://iostream.ssrv.su/ftp/mirea/CUDA_alt.sh)```

Если скрипт недоступен, значит мы его ещё не опубликовали.

### Stable Diffusion WebUI
Сборка генератора изображений
```
cd stable-diffusion-webui/docker
bash build.sh
bash run.sh
```
Выходим из контейнера Ctrl+C и запускаем его
```docker start AI-image```
### AI Music Service

1. Переход в директорию
```cd Music-Ai-Service```
2. Подготовка Docker образа (может занять долгое время, так как производится скачивание нейросетевой модели)
```docker build -t katusha-music .```
3. Запуск
```docker run -d --name katusha-music -p 3000:3000 katusha-music```
4. Документация доступна по следующему пути: ```http://<your_ip>:3000/docs```



<!--Пользовательская документация-->
## Преимущества
1. Все нейросети развернуты локально, что позволяет быть независимыми от состояния их глобальных серверов и цензуры.

2. Высокий уровеь безопасноти сервиса.

<!--Поддержка-->
## Команда Adeptus Altusches

1. Александр Стпенцов - Python backend develovper, teamlead
2. Максим Журавлёв - VUE frontend develovper
3. Дон Лаухин - Artificial Intelligence Engineer
4. Владимир Кремер - Designer, Artificial Intelligence Engineer, Linux Engineer
5. Варвара Ионова - Designer, Linux Engineer
