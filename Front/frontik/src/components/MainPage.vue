<template>
  <div class="page-container">
    <!-- Левая колонка: ввод текста, кнопки и дисклеймер -->
    <div class="left-panel">
      <h1>Искусство через призму военных лет</h1>

      <textarea
        v-model="text"
        placeholder="Сегодня наша армия отбивала Севастополь у немцев. Совсем скоро мы выгоним их из СССР."
      ></textarea>

      <!-- Большая кнопка «Сгенерировать» -->
      <button class="generate-button" @click="onGenerateClick">
        Сгенерировать
      </button>

      <!-- Чекбоксы под кнопкой -->
      <div class="options-block">
        <label class="custom-checkbox">
          <input type="checkbox" v-model="voiceOption" />
          <span class="checkbox-mark"></span>
          Озвучить текст
        </label>
        <label class="custom-checkbox">
          <input type="checkbox" v-model="musicOption" />
          <span class="checkbox-mark"></span>
          Сгенерировать музыку
        </label>
      </div>

      <!-- Дисклеймер внизу -->
      <div class="disclaimer">
        Мы не несем ответственности за контент, генерируемый нейросетью. Вся ответственность
        за создание противоправного и нежелательного контента лежит на пользователе. Adeptus
        Altusiches оставляют за собой право передавать сведения о пользователе и его
        генерациях правоохранительным органам.
      </div>
      <button class="exit-button" @click="Exit">
        Выйти
      </button>
    </div>

    <!-- Правая колонка: плейсхолдеры + настройки + медиатека -->
    <div class="right-panel">
      <!-- Три «пустых» прямоугольника до генерации -->
      <div class="placeholder big-placeholder"></div>
      <div class="placeholder small-placeholder"></div>
      <div class="placeholder small-placeholder"></div>

      <!-- Блок настроек со слайдерами -->
      

      <!-- Кнопка «Медиатека генераций» -->
      <button class="media-library-button" @click="goToMediaLibrary">
        Медиатека генераций
      </button>
    </div>
  </div>

  <!-- Оверлей загрузки (появляется после клика на «Сгенерировать») -->
  <div v-if="isLoading" class="modal-overlay">
    <div class="modal-content loading-modal">
      <h2>Обработка запроса</h2>
      <p>Ваш запрос обрабатывается...</p>
      <div class="loader"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// Содержимое textarea
const text = ref('')

// Флаги чекбоксов
const voiceOption = ref(true)
const musicOption = ref(false)

// Ширина/высота для изображения (слайдеры)
const imageWidth = ref(512)
const imageHeight = ref(512)

// Флаг загрузки, чтобы показать анимацию
const isLoading = ref(false)

// URL для WebSocket (предполагаем, что токен уже лежит в localStorage)
const WS_URL = `ws://88.84.211.248:8000/ws?token=${localStorage.getItem('access_token')}`

// Запускаем генерацию при клике
async function onGenerateClick() {
  if (!text.value.trim()) {
    alert('Пожалуйста, введите текст для генерации')
    return
  }

  isLoading.value = true

  // Формируем payload (можно добавить дополнительные поля, например voiceOption, musicOption)
  const payload = {
    action: 'all',
    text: '23',
    width: imageWidth.value,  
    height: imageHeight.value,
    voice: voiceOption.value,
    music: musicOption.value
  }

  try {
    await handleWebSocketRequest(payload)
    // Когда придёт успешный ответ от сервера, здесь можно обработать его и вывести результат.
    // Например, заменить плейсхолдеры реальным контентом.
    // Но пока мы демонстрируем только предгенерационный вид,
    // поэтому просто отключим анимацию загрузки.
    isLoading.value = false
  } catch (e) {
    console.error('Ошибка генерации:', e)
    alert(`Ошибка: ${e.message}`)
    isLoading.value = false
  }
}

// Простая обёртка для WebSocket-запроса
function handleWebSocketRequest(data) {
  return new Promise((resolve, reject) => {
    const ws = new WebSocket(WS_URL)
    let buffer = ''
    let isResolved = false

    ws.onopen = () => {
      ws.send(JSON.stringify(data))
    }

    ws.onmessage = async (event) => {
      try {
        const chunk = event.data instanceof Blob 
          ? await event.data.text()
          : event.data
        buffer += chunk

        // Проверяем, можно ли распарсить полный JSON
        try {
          const parsed = JSON.parse(buffer)
          if (parsed.status === 'success' || parsed.status === 'error') {
            isResolved = true
            ws.close()
            resolve(parsed)
          }
        } catch {
          // JSON ещё не собран целиком – ждём следующего chunk’a
        }
      } catch (err) {
        ws.close()
        reject(err)
      }
    }

    ws.onerror = (err) => {
      if (!isResolved) {
        ws.close()
        reject(new Error(`WebSocket error: ${err.message}`))
      }
    }

    ws.onclose = (event) => {
      if (!isResolved) {
        reject(new Error(`Connection closed: ${event.reason}`))
      }
    }
  })
}

// Навигация в медиатеку
function goToMediaLibrary() {
  router.push('/history')
}
function Exit() {
  router.push('/login')
}

// Если нет токена – кидаем на логин
onMounted(() => {
  if (!localStorage.getItem('access_token')) {
    router.push('/noauth')
  }
})
</script>

<style scoped>
@font-face {
    font-family: 'MetaDat';
    src: url('Metadannye-Export.ttf') format('truetype'), /* IE6-IE8 */
}
@font-face {
    font-family: 'TT';
    src: url('TT Bricks Medium Italic.ttf') format('truetype'), /* IE6-IE8 */
}
/* Общая обёртка: две колонки */
.page-container {
  max-width: 1800px;
  display: flex;
  gap: 1rem;
  padding: 1rem;
}

/* Левая колонка */
.left-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #f9f4e9;
  border: 2px solid #c0392b;
  border-radius: 8px;
  padding: 1rem;
}

/* Заголовок */
.left-panel h1 {
  font-family: 'MetaDat', sans-serif;
  font-size: 3rem;
  color: #c0392b;
  text-align: center;
  margin-bottom: 1rem;
}

/* Текстовое поле */
.left-panel textarea {
  flex: 1;
  width: 100%;
  min-height: 300px;
  max-height: 400px;
  font-family: 'Georgia', serif;
  font-size: 1.3rem;
  border: 2px solid #c0392b;
  border-radius: 8px;
  background-color: #fffef8;
  color: #3c2f1e;
  padding: 0.5rem;
  resize: vertical;
  outline: none;
  margin-bottom: 1rem;
}

/* Кнопка «Сгенерировать» */
.generate-button {
  margin-top: 1.5rem;
  background-color: #c0392b;
  color: #fff;
  font-family: 'MetaDat', sans-serif; 
  font-size: 2.3rem;
  border: none;
  border-radius: 8px;
  padding: 0.75rem;
  cursor: pointer;
  transition: background-color 0.3s;
  margin-bottom: 1rem;
  width: 100%;
}
.exit-button {
  margin-top: 1.5rem;
  background-color: #c0392b;
  color: #fff;
  font-family: 'MetaDat', sans-serif; 
  font-size: 2.3rem;
  border: none;
  border-radius: 8px;
  padding: 0.75rem;
  cursor: pointer;
  transition: background-color 0.3s;
  margin-bottom: 1rem;
  width: 100%;
}
.exit-button:hover {
  background-color: #a8322a;
}
.generate-button:hover {
  background-color: #a8322a;
}

/* Блок чекбоксов */
.options-block {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

/* Кастомный чекбокс */
.custom-checkbox {
  position: relative;
  padding-left: 28px;
  cursor: pointer;
  user-select: none;
  font-family: 'TT', sans-serif;
  font-size: 1.6rem;
  color: #3c2f1e;
}

/* Скрываем стандартный input */
.custom-checkbox input {
  position: absolute;
  opacity: 0;
  cursor: pointer;
  height: 0;
  width: 0;
}

/* Квадратик/кружочек для чекбокса */
.custom-checkbox .checkbox-mark {
  position: absolute;
  top: 0;
  left: 0;
  height: 20px;
  width: 20px;
  border: 2px solid #c0392b;
  border-radius: 4px;
  background-color: #fff;
}

/* Галочка, которая появляется при checked */
.custom-checkbox input:checked ~ .checkbox-mark {
  background-color: #c0392b;
}

.custom-checkbox .checkbox-mark::after {
  content: "";
  position: absolute;
  display: none;
}

/* Когда чекбокс отмечен – рисуем галочку */
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

/* Дисклеймер */
.disclaimer {
  font-family: 'MetaDat', sans-serif;
  background-color: #3c2f1e;
  color: #fff;
  font-size: 1.8rem;
  font-weight: 0rem;
  letter-spacing:normal;
  line-height: 1.2;
  padding: 0.75rem;
  border-radius: 6px;
  margin-top: auto;
}

/* Правая колонка */
.right-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  background-color: #f9f4e9;
  border: 2px solid #3c2f1e;
  border-radius: 8px;
  padding: 1rem;
}

/* Плейсхолдерные блоки */
.placeholder {
  border-radius: 8px;
  background: linear-gradient(120deg, #030d14, #b1120d, #df9f00);
  background-size: 300% 300%;
  animation: placeholderGradient 3s ease infinite;
}

.big-placeholder {
  flex: 2;
  min-height: 180px;
}

.small-placeholder {
  flex: 1;
  min-height: 80px;
}

/* Анимация градиента, чтобы было похоже на «ожидающий» эффект */
@keyframes placeholderGradient {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

/* Блок настроек */
.settings-block {
  border: 2px solid #c0392b;
  border-radius: 8px;
  background-color: #fffef8;
  padding: 0.75rem;
}

/* Заголовок настроек */
.settings-header {
  font-family: 'Changa One', sans-serif;
  font-size: 1.1rem;
  color: #c0392b;
  margin-bottom: 0.75rem;
}

/* Ряд слайдера */
.slider-row {
  display: flex;
  align-items: center;
  margin-bottom: 0.5rem;
}

.slider-row label {
  flex: 1;
  font-family: 'Georgia', serif;
  color: #3c2f1e;
}

.slider-row input[type="range"] {
  flex: 3;
  margin: 0 0.5rem;
}

.slider-value {
  flex: 0.5;
  text-align: right;
  font-family: 'Georgia', serif;
  color: #3c2f1e;
}

/* Мелкая подсказка внизу блока настроек */
.help-text {
  font-size: 0.8rem;
  color: #666;
  margin-top: 0.5rem;
  text-align: center;
}

/* Кнопка «Медиатека генераций» */
.media-library-button {
  background-color: #3c2f1e;
  color: #fff;
  font-family: 'MetaDat', sans-serif;
  font-size: 2em;
  border: none;
  border-radius: 8px;
  padding: 0.75rem;
  cursor: pointer;
  transition: background-color 0.3s;
  margin-top: auto;
  width: 100%;
}
.media-library-button:hover {
  background-color: #2a2318;
}

/* Оверлей загрузки */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: #fffef8;
  padding: 2rem;
  border-radius: 8px;
  max-width: 80%;
  max-height: 80vh;
  text-align: center;
  position: relative;
}

.loading-modal h2 {
  color: #3c2f1e;
}

.loading-modal p {
  color: #666;
  margin-top: 0.5rem;
}

.loader {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3c2f1e;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 20px auto;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Адаптивность: на узких экранах колонки «стекутся» */
@media (max-width: 900px) {
  .page-container {
    flex-direction: column;
  }
}
</style>
