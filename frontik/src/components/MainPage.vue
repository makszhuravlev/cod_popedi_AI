<template>
    <div class="root-container">
        <div class="page-container">
            <!-- Левая колонка: ввод текста, кнопки и дисклеймер -->
            <div class="left-panel">
                <img class="mainlogo" src="../../public/logo3.webp" />
                <h1>Искусство через призму военных лет</h1>

                <!-- Текстовое поле: занимает основное пространство -->
                <textarea
                    v-model="text"
                    placeholder="Сегодня наша армия отбивала Севастополь у немцев. Совсем скоро мы выгоним их из СССР."
                ></textarea>

                <!-- Кнопка «Сгенерировать» -->
                <button
                    class="generate-button"
                    @click="onGenerateClick"
                    :disabled="isLoading"
                >
                    {{ isLoading ? "Генерация..." : "Сгенерировать" }}
                </button>

                <!-- Блок чекбоксов -->
                <div class="options-block">
                    <label class="custom-checkbox">
                        <input type="checkbox" v-model="textOption" />
                        <span class="checkbox-mark"></span>
                        Сгенерировать текст
                    </label>
                    <label class="custom-checkbox">
                        <input type="checkbox" v-model="musicOption" />
                        <span class="checkbox-mark"></span>
                        Сгенерировать музыку
                    </label>
                </div>

                <!-- Дисклеймер -->
                <div class="disclaimer">
                    Мы не несем ответственности за контент, генерируемый
                    нейросетью. Вся ответственность за создание противоправного
                    и нежелательного контента лежит на пользователе. Adeptus
                    Altusiches оставляют за собой право передавать сведения о
                    пользователе и его генерациях правоохранительным органам.
                </div>

                <!-- Кнопка «Выйти» -->
                <button class="exit-button" @click="exit">Выйти</button>
            </div>

            <!-- Правая колонка: вывод сгенерированного контента -->
            <div class="right-panel">
                <!-- Загрузка -->
                <template v-if="isLoading">
                    <div class="placeholder big-placeholder"></div>
                    <div class="placeholder small-placeholder"></div>
                    <div class="placeholder small-placeholder"></div>
                </template>

                <!-- Контент после генерации -->
                <template v-else>
                    <!-- Изображение -->
                    <img
                        v-if="generatedImageUrl"
                        :src="generatedImageUrl"
                        class="content-image big-image"
                        alt="Generated"
                    />

                    <!-- Текст (теперь растёт по высоте) -->
                    <div v-if="generatedText" class="generated-text">
                        {{ generatedText }}
                    </div>

                    <!-- Музыка -->
                    <audio
                        v-if="generatedMusicUrl"
                        :src="generatedMusicUrl"
                        class="audio-player"
                        controls
                    ></audio>

                    <!-- Если вообще ничего не сгенерировано -->
                    <template
                        v-if="
                            !generatedText &&
                            !generatedImageUrl &&
                            !generatedMusicUrl
                        "
                    >
                        <div class="placeholder big-placeholder"></div>
                        <div class="placeholder small-placeholder"></div>
                        <div class="placeholder small-placeholder"></div>
                    </template>
                </template>

                <!-- Кнопка «Медиатека генераций» -->
                <button class="media-library-button" @click="goToMediaLibrary">
                    Медиатека генераций
                </button>
            </div>
        </div>

        <!-- Оверлей загрузки (пока идёт WebSocket) -->
        <div v-if="isLoading" class="modal-overlay">
            <div class="modal-content loading-modal">
                <h2>Обработка запроса</h2>
                <p>Ваш запрос обрабатывается...</p>
                <div class="loader"></div>
            </div>
        </div>

        <!-- Футер страницы -->
        <footer class="page-footer">
            © 1945-2025 Катюша AI prod by Adeptus Altusiches. Все права
            защищены.
        </footer>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { IP_BACK } from "@/config.js";

const router = useRouter();

// Содержимое textarea
const text = ref("");

// Флаги чекбоксов
const musicOption = ref(false);
const textOption = ref(true);

// Флаг загрузки, чтобы показать анимацию и заблокировать кнопку
const isLoading = ref(false);

// Переменные для хранения сгенерированного контента
const generatedText = ref(null);
const generatedImageUrl = ref(null);
const generatedMusicUrl = ref(null);

// Удобное вычисление наличия любого контента (если нужно в дальнейшем)
const hasAnyContent = computed(() => {
    return (
        generatedText.value ||
        generatedImageUrl.value ||
        generatedMusicUrl.value
    );
});

// URL для WebSocket
const WS_URL = `ws://${IP_BACK}:8000/ws?token=${localStorage.getItem(
    "access_token",
)}`;

// Обработчик клика «Сгенерировать»
async function onGenerateClick() {
    if (!text.value.trim()) {
        alert("Пожалуйста, введите текст для генерации");
        return;
    }

    // Сбрасываем предыдущий контент
    generatedText.value = null;
    generatedImageUrl.value = null;
    generatedMusicUrl.value = null;

    // Включаем индикатор загрузки
    isLoading.value = true;

    // Формируем полезную нагрузку.
    // Передаём информацию о том, что именно генерить (текст, картинку, музыку).
    const payload = {
        action: "image",
        text: text.value,
        options: {
            withText: textOption.value,
            withMusic: musicOption.value,
            withImage: true,
        },
    };

    try {
        // Ждём ответа от WebSocket
        const parsed = await handleWebSocketRequest(payload);

        if (parsed.status === "success") {
            // Распаковываем то, что пришло
            generatedText.value =
                parsed.generated_text ||
                "ыввыфвыфвыфвыфвыфыввыфвыфвыфвыфвыфыввыфвыфвыфвыфвыфыввыфвыфвыфвыфвыфыввыфвыфвыфвыфвыфыввыфвыфвыфвыфвыфыввыфвыфвыфвыфвыфыввыфвыфвыфвыфвыфыввыфвыфвыфвыфвыфыввыфвыфвыфвыфвыфыввыфвыфвыфвыфвыфыввыфвыфвыфвыфвыфыввыфвыфвыфвыфвыфыввыфвыфвыфвыфвыфыввыфвыфвыфвыфвыфыввыфвыфвыфвыфвыф";
            generatedImageUrl.value = parsed.image_url
                ? "http://" + IP_BACK + ":8000" + parsed.image_url
                : null;
            generatedMusicUrl.value =
                parsed.music_url ||
                `http://${IP_BACK}:8000/static/images/1.mp3`;
        } else {
            alert(parsed.error || "Не удалось сгенерировать контент");
        }
    } catch (e) {
        console.error("Ошибка генерации:", e);
        alert(`Ошибка: ${e.message}`);
    } finally {
        // Выключаем индикатор загрузки
        isLoading.value = false;
    }
}

// WebSocket-обёртка
function handleWebSocketRequest(data) {
    return new Promise((resolve, reject) => {
        const ws = new WebSocket(WS_URL);
        let buffer = "";
        let isResolved = false;

        ws.onopen = () => {
            ws.send(JSON.stringify(data));
        };

        ws.onmessage = async (event) => {
            try {
                const chunk =
                    event.data instanceof Blob
                        ? await event.data.text()
                        : event.data;
                buffer += chunk;
                try {
                    const parsed = JSON.parse(chunk);
                    // Предполагаем, что сервер вернёт объект вида:
                    // { status: 'success', generated_text, image_url, music_url }
                    if (
                        parsed.status === "success" ||
                        parsed.status === "error"
                    ) {
                        isResolved = true;
                        ws.close();
                        resolve(parsed);
                    }
                } catch {
                    // JSON пока не целиком, ждём следующую часть
                }
            } catch (err) {
                ws.close();
                reject(err);
            }
        };

        ws.onerror = (err) => {
            if (!isResolved) {
                ws.close();
                reject(new Error(`WebSocket error: ${err.message}`));
            }
        };

        ws.onclose = (event) => {
            if (!isResolved) {
                const reason = event.reason || "без указания причины";
                reject(new Error(`Connection closed: ${reason}`));
            }
        };
    });
}

// Навигация в медиатеку
function goToMediaLibrary() {
    router.push("/history");
}

// Переход на экран логина
function exit() {
    router.push("/login");
}

// Если нет токена – кидаем на логин
onMounted(() => {
    if (!localStorage.getItem("access_token")) {
        router.push("/noauth");
    }
});
</script>

<style scoped>
html {
    font-size: 100%;
    height: 100%;
    margin: 0;
    padding: 0;
}
@font-face {
    font-family: "Rukopis";
    src: url("../assets/snellroundhand_black.otf") format("opentype");
}
.root-container {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
}
.mainlogo {
    margin-top: -10%;
    height: 40%;
    width: 40%;
    text-align: center;
    margin-left: auto;
    margin-right: auto;
}
.page-container {
    box-sizing: border-box;
    display: flex;
    flex: 1;
    width: 100%;
    height: 100%;
    gap: 1rem;
    padding: 1rem;
    background-color: #faf5ef;
}
.left-panel,
.right-panel {
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    flex: 1;
    background-color: #d2c9b0;
    border-radius: 8px;
    padding: 1rem;
    overflow-y: auto;
}
.left-panel {
    padding-top: 2%;
    border: 1px solid #0a0a15;
}
.right-panel {
    justify-content: flex-start;
    border: 1px solid #0a0a15;
}
.left-panel h1 {
    flex: 0 0 auto;
    font-family: "MetaDat", sans-serif;
    font-size: calc(1.5rem + 1vw);
    color: #ce191d;
    text-align: center;
    margin-top: -10%;
    margin-bottom: 1rem;
    line-height: 1.2;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.left-panel textarea {
    flex: 1 1 auto;
    width: 100%;
    font-family: "Rukopis", serif;
    font-size: calc(1.1rem + 0.2vw);
    border: 2px solid #ce191d;
    border-radius: 8px;
    background-color: #fff6e1;
    color: #3c2f1e;
    padding: 0.5rem;
    resize: vertical;
    outline: none;
    margin-bottom: 1rem;
    box-sizing: border-box;
    min-height: 120px;
    max-height: 30vh;
    overflow-y: auto;
}
.generate-button {
    flex: 0 0 auto;
    background-color: #0a0a15;
    color: #fff;
    font-family: "MetaDat", sans-serif;
    font-size: calc(1rem + 0.5vw);
    border: none;
    border-radius: 8px;
    padding: 0.75rem;
    cursor: pointer;
    transition: background-color 0.3s;
    width: 100%;
    box-sizing: border-box;
    margin-bottom: 1rem;
}
.generate-button:disabled {
    background-color: #555;
    cursor: not-allowed;
}
.generate-button:hover:not(:disabled) {
    background-color: #a8322a;
}
.options-block {
    flex: 0 0 auto;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    margin-bottom: 1rem;
}
.custom-checkbox {
    position: relative;
    padding-left: 28px;
    cursor: pointer;
    user-select: none;
    font-family: "TT", sans-serif;
    font-size: calc(1rem + 0.2vw);
    color: #3c2f1e;
}
.custom-checkbox input {
    position: absolute;
    opacity: 0;
    cursor: pointer;
    height: 0;
    width: 0;
}
.custom-checkbox .checkbox-mark {
    position: absolute;
    top: 0;
    left: 0;
    height: 20px;
    width: 20px;
    border: 2px solid #ce191d;
    border-radius: 4px;
    background-color: #fff;
}
.custom-checkbox input:checked ~ .checkbox-mark {
    background-color: #ce191d;
}
.custom-checkbox .checkbox-mark::after {
    content: "";
    position: absolute;
    display: none;
}
.custom-checkbox input:checked ~ .checkbox-mark::after {
    display: block;
    left: 5px;
    top: 1px;
    width: 6px;
    height: 12px;
    border: solid #fff;
    border-width: 0 2px 2px 0;
    transform: rotate(45deg);
}
.disclaimer {
    flex: 0 0 auto;
    font-family: "MetaDat", sans-serif;
    background-color: #0a0a15;
    color: #fff;
    font-size: calc(1rem + 0.2vw);
    line-height: 1.3;
    padding: 0.75rem;
    border-radius: 6px;
    margin-bottom: 1rem;
    max-height: 15vh;
    overflow-y: auto;
    box-sizing: border-box;
}
.exit-button {
    flex: 0 0 auto;
    background-color: #ce191d;
    color: #fff;
    font-family: "MetaDat", sans-serif;
    font-size: calc(1rem + 0.5vw);
    border: none;
    border-radius: 8px;
    padding: 0.75rem;
    cursor: pointer;
    transition: background-color 0.3с;
    width: 100%;
    box-sizing: border-box;
    margin-bottom: 0;
    flex-shrink: 0;
}
.exit-button:hover {
    background-color: #a8322a;
}

/* Блок generated-text теперь занимает всю ширину и автоматически растёт в высоту */
.generated-text {
    flex: 0 0 auto;
    width: 100%;
    background-color: #fff6e1;
    color: #3c2f1e;
    font-family: "Rukopis", serif;
    font-size: calc(1.1rem + 0.2vw);
    border: 2px solid #ce191d;
    border-radius: 8px;
    padding: 0.75rem;
    margin-bottom: 0.5rem;
    white-space: pre-wrap;
    word-break: break-word;
    height: auto;
    max-height: none;
    overflow-y: visible;
}

@keyframes placeholderGradient {
    0% {
        background-position: 0% 50%;
    }
    50% {
        background-position: 100% 50%;
    }
    100% {
        background-position: 0% 50%;
    }
}
.right-panel .placeholder {
    border-radius: 8px;
    background: linear-gradient(120deg, #030d14, #b1120d, #df9f00);
    background-size: 300% 300%;
    animation: placeholderGradient 3s ease infinite;
    flex-shrink: 0;
}
.right-panel .big-placeholder {
    flex: 4 1 auto;
    min-height: 0;
    margin-bottom: 0.5rem;
}
.right-panel .small-placeholder {
    flex: 0.5 1 auto;
    min-height: 0;
    margin-bottom: 0.5rem;
}
.content-image.big-image {
    flex: 2 1 auto;
    width: 60%;
    height: auto;
    object-fit: contain;
    margin-bottom: 0.5rem;
    margin-left: 22%;
}
.content-image.small-image {
    flex: 1 1 auto;
    width: 100%;
    object-fit: contain;
    margin-bottom: 0.5rem;
}
.audio-player {
    flex: 0 0 auto;
    width: 100%;
    margin-bottom: 0.5rem;
}
.right-panel .media-library-button {
    flex: 0 0 auto;
    background-color: #0a0a15;
    color: #fff;
    font-family: "MetaDat", sans-serif;
    font-size: calc(1rem + 0.5vw);
    border: none;
    border-radius: 8px;
    padding: 0.75rem;
    cursor: pointer;
    transition: background-color 0.3с;
    width: 100%;
    box-sizing: border-box;
    margin-top: auto;
    flex-shrink: 0;
}
.right-panel .media-library-button:hover {
    background-color: #2a2318;
}
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 9999;
}
.modal-content {
    place-items: center;
    background-color: #ffffff;
    border-radius: 8px;
    padding: 1.5rem;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    max-width: 90%;
    max-height: 80%;
    overflow-y: auto;
    z-index: 10000;
}
.loading-modal h2 {
    font-weight: 100;
    margin-left: auto;
    margin-right: auto;
    font-family: "MetaDat";
    margin-top: 0;
    font-size: 1.8rem;
    color: #3c2f1e;
}
.loading-modal p {
    font-weight: 100;
    margin-left: 5%;
    font-family: "MetaDat";
    font-size: 1rem;
    color: #3c2f1e;
}
.loader {
    border: 4px solid #f3f3f3;
    border-top: 4px solid #ce191d;
    border-radius: 50%;
    width: 32px;
    height: 32px;
    animation: spin 1s linear infinite;
    margin: 0 auto;
}
@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}
.page-footer {
    background-color: #0a0a15;
    color: #ce191d;
    text-align: center;
    padding: 1rem 0;
    font-family: "MetaDat", sans-serif;
    font-size: 1rem;
    flex-shrink: 0;
}
@media (max-width: 1200px) and (min-width: 901px) {
    .page-container {
        padding: 0.75rem;
        gap: 0.75rem;
    }
    .left-panel,
    .right-panel {
        padding: 0.75rem;
    }
    .left-panel h1 {
        font-size: calc(1.4rem + 0.9vw);
    }
    .generate-button,
    .exit-button,
    .media-library-button {
        font-size: calc(0.9rem + 0.4vw);
    }
}
@media (max-width: 900px) {
    .page-container {
        flex-direction: column;
        padding: 0.5rem;
        gap: 0.5rem;
    }
    .left-panel,
    .right-panel {
        flex: none;
        width: 100%;
        padding: 0.75rem;
        margin-bottom: 0.5rem;
    }
    .left-panel h1 {
        font-size: calc(1.3rem + 1.5vw);
    }
    .left-panel textarea {
        max-height: 25vh;
        font-size: calc(1rem + 0.5vw);
    }
    .generate-button,
    .exit-button,
    .media-library-button {
        font-size: calc(0.9rem + 0.7vw);
        padding: 0.5рем;
    }
    .disclaimer {
        font-size: calc(0.9rem + 0.3vw);
        max-height: 12vh;
    }
    .options-block .custom-checkbox {
        font-size: calc(0.9рем + 0.3vw);
    }
    .content-image.big-image {
        flex: none;
        height: auto;
    }
    .content-image.small-image {
        flex: none;
        height: auto;
    }
    .media-library-button {
        margin-top: 0.5рем;
    }
    /* Генерируемый текст во вьюпорте */
    .generated-text {
        font-size: calc(1рем + 0.5vw);
    }
}
@media (max-width: 600px) {
    .page-container {
        padding: 0.25рем;
        gap: 0.25рем;
    }
    .left-panel,
    .right-panel {
        padding: 0.5рем;
    }
    .left-panel h1 {
        font-size: calc(1.1рем + 1.8vw);
    }
    .left-panel textarea {
        max-height: 20vh;
        font-size: calc(0.9рем + 0.8vw);
    }
    .generate-button,
    .exit-button,
    .media-library-button {
        font-size: calc(0.8рем + 1vw);
        padding: 0.4рем;
    }
    .disclaimer {
        font-size: calc(0.8рем + 0.4vw);
        max-height: 10vh;
    }
    .options-block .custom-checkbox {
        font-size: calc(0.8рем + 0.4vw);
    }
    .content-image.big-image,
    .content-image.small-image {
        width: 100%;
    }
    /* Генерируемый текст во вьюпорте */
    .generated-text {
        font-size: calc(0.9рем + 0.8vw);
    }
}
</style>
