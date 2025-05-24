<template>
  <div class="root-container">
    <div class="page-container">
      <!-- Левая колонка: ввод текста, кнопки и дисклеймер -->
      <div class="left-panel">
        <img class='mainlogo' src="../../public/logo3.webp">
        <h1>Искусство через призму военных лет</h1>

        <!-- Текстовое поле: занимает основное пространство -->
        <textarea
          v-model="text"
          placeholder="Сегодня наша армия отбивала Севастополь у немцев. Совсем скоро мы выгоним их из СССР."
        ></textarea>

        <!-- Кнопка «Сгенерировать» -->
        <button class="generate-button" @click="onGenerateClick">
          Сгенерировать
        </button>

        <!-- Блок чекбоксов -->
        <div class="options-block">
          <label class="custom-checkbox">
            <input type="checkbox" v-model="voiceOption" />
            <span class="checkbox-mark"></span>
            Сгенерировать текст
          </label>
          <label class="custom-checkbox">
            <input type="checkbox" v-model="voiceOption" />
            <span class="checkbox-mark"></span>
            Сгенерировать музыку
          </label>
          <label class="custom-checkbox">
            <input type="checkbox" v-model="voiceOption" />
            <span class="checkbox-mark"></span>
            Озвучить текст
          </label>
        
        </div>

        <!-- Дисклеймер -->
        <div class="disclaimer">
          Мы не несем ответственности за контент, генерируемый нейросетью. Вся ответственность
          за создание противоправного и нежелательного контента лежит на пользователе. Adeptus
          Altusiches оставляют за собой право передавать сведения о пользователе и его
          генерациях правоохранительным органам.
        </div>

        <!-- Кнопка «Выйти» -->
        <button class="exit-button" @click="exit">
          Выйти
        </button>
      </div>

      <!-- Правая колонка: вывод сгенерированного контента -->
      <div class="right-panel">
        <!-- Если есть изображение, показываем <img> -->
        <img
          v-if="generatedImageUrl"
          :src="generatedImageUrl"
          class="content-image big-image"
          alt="Generated"
        />

        <!-- Если есть миниатюры, показываем их -->


        <!-- Если есть голос, показываем плеер -->
        <audio
          v-if="generatedAudioUrl"
          :src="generatedAudioUrl"
          class="audio-player"
          controls
        ></audio>

        <!-- Если есть музыка, показываем плеер -->
        <audio
          v-if="generatedMusicUrl"
          :src="generatedMusicUrl"
          class="audio-player"
          controls
        ></audio>

        <!-- Во всех остальных случаях (нет ни картинки, ни аудио) рисуем анимированный плейсхолдер -->
        <div
          v-if="!hasAnyContent"
          class="placeholder big-placeholder"
        ></div>
        <div
          v-if="!hasAnyContent"
          class="placeholder small-placeholder"
        ></div>
        <div
          v-if="!hasAnyContent"
          class="placeholder small-placeholder"
        ></div>

        <!-- Кнопка «Медиатека генераций» -->
        <button class="media-library-button" @click="goToMediaLibrary">
          Медиатека генераций
        </button>
      </div>
    </div>

    <!-- Оверлей загрузки -->
    <div v-if="isLoading" class="modal-overlay">
      <div class="modal-content loading-modal">
        <h2>Обработка запроса</h2>
        <p>Ваш запрос обрабатывается...</p>
        <div class="loader"></div>
      </div>
    </div>

    <!-- Футер страницы -->
      <footer class="page-footer">
        © 1945-2025 Катюша AI prod by Adeptus Altusiches. Все права защищены.
      </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// Содержимое textarea
const text = ref('')

// Флаги чекбоксов
const voiceOption = ref(true)
const musicOption = ref(false)

// Ширина/высота для изображения (запас на будущее)
const imageWidth = ref(512)
const imageHeight = ref(512)

// Флаг загрузки, чтобы показать анимацию
const isLoading = ref(false)

// Переменные для хранения URL сгенерированного контента
const generatedImageUrl = ref(null)
const generatedThumbnail1 = ref(null)
const generatedThumbnail2 = ref(null)
const generatedAudioUrl = ref(null)
const generatedMusicUrl = ref(null)

// Флаг, чтобы понимать, существует ли хоть один вид контента
const hasAnyContent = computed(() => {
  return (
    generatedImageUrl.value ||
    generatedThumbnail1.value ||
    generatedThumbnail2.value ||
    generatedAudioUrl.value ||
    generatedMusicUrl.value
  )
})

// URL для WebSocket
const WS_URL = `ws://88.84.211.248:8000/ws?token=${localStorage.getItem('access_token')}`

// Обработчик клика «Сгенерировать»
async function onGenerateClick() {
  if (!text.value.trim()) {
    alert('Пожалуйста, введите текст для генерации')
    return
  }

  // Сброс старого контента
  generatedImageUrl.value = null
  generatedAudioUrl.value = null
  generatedMusicUrl.value = null

  isLoading.value = true

  const payload = {
    action: 'all',
    text: text.value,
  }

  try {
    // Ждём ответа от WebSocket
    const parsed = await handleWebSocketRequest(payload)

    // Ожидаем, что parsed = { status: 'success', image_url, thumb1_url, thumb2_url, audio_url, music_url }
    if (parsed.status === 'success') {
      generatedImageUrl.value = parsed.image_url || null
      generatedAudioUrl.value = parsed.audio_url || null
      generatedMusicUrl.value = parsed.music_url || null
    } else {
      alert(parsed.error || 'Не удалось сгенерировать контент')
    }
  } catch (e) {
    console.error('Ошибка генерации:', e)
    alert(`Ошибка: ${e.message}`)
  } finally {
    isLoading.value = false
  }
}

// WebSocket-обёртка
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

        try {
          const parsed = JSON.parse(buffer)
          // Ждём, пока status станет 'success' или 'error'
          if (parsed.status === 'success' || parsed.status === 'error') {
            isResolved = true
            ws.close()
            resolve(parsed)
          }
        } catch {
          // JSON ещё не полностью пришёл
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
        const reason = event.reason || 'без указания причины'
        reject(new Error(`Connection closed: ${reason}`))
      }
    }
  })
}

// Навигация в медиатеку
function goToMediaLibrary() {
  router.push('/history')
}

// Переход на экран логина
function exit() {
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
/* ============================================================================ 
   1. Корневые единицы
   ============================================================================ */
html {
  font-size: 100%;
  height: 100%;
  margin: 0;
  padding: 0;
}
@font-face {
    font-family: 'Rukopis';
    src: url('../assets/snellroundhand_black.otf') format('opentype'), /* IE6-IE8 */
}
/* ============================================================================ 
   2. Контейнер-обёртка: растягиваемся на весь экран 
   ============================================================================ */
.root-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}
.mainlogo{
  margin-top: -10%;
  height:40%;
  width:40%;  
  text-align: center;
  margin-left: auto; margin-right: auto;  
}
/* ============================================================================ 
   3. Основной контент: flex-ряд, панели равной ширины 
   ============================================================================ */
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

/* ============================================================================ 
   4. Левая и правая панели: растягиваются по ширине и высоте 
   ============================================================================ */
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

/* Отдельные рамки для наглядности */
.left-panel {
  padding-top: 2%;
  border: 1px solid #0a0a15;
}
.right-panel {
  border: 1px solid #0a0a15;
}

/* ============================================================================ 
   5. Элементы левой панели 
   ============================================================================ */

/* 5.1 Заголовок */
.left-panel h1 {
  flex: 0 0 auto;
  font-family: 'MetaDat', sans-serif;
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

/* 5.2 Текстовое поле */
.left-panel textarea {
  flex: 1 1 auto;
  width: 100%;
  font-family: 'Rukopis', serif;
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

/* 5.3 Кнопка «Сгенерировать» */
.generate-button {
  flex: 0 0 auto;
  background-color: #0a0a15;
  color: #fff;
  font-family: 'MetaDat', sans-serif;
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
.generate-button:hover {
  background-color: #a8322a;
}

/* 5.4 Блок чекбоксов */
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
  font-family: 'TT', sans-serif;
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

/* 5.5 Дисклеймер */
.disclaimer {
  flex: 0 0 auto;
  font-family: 'MetaDat', sans-serif;
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

/* 5.6 Кнопка «Выйти» */
.exit-button {
  flex: 0 0 auto;
  background-color: #ce191d;
  color: #fff;
  font-family: 'MetaDat', sans-serif;
  font-size: calc(1rem + 0.5vw);
  border: none;
  border-radius: 8px;
  padding: 0.75rem;
  cursor: pointer;
  transition: background-color 0.3s;
  width: 100%;
  box-sizing: border-box;
  margin-bottom: 0;
  flex-shrink: 0;
}
.exit-button:hover {
  background-color: #a8322a;
}

/* ============================================================================ 
   6. Элементы правой панели 
   ============================================================================ */

/* Анимированный фон для плейсхолдеров */
@keyframes placeholderGradient {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.right-panel .placeholder {
  border-radius: 8px;
  background: linear-gradient(120deg, #030d14, #b1120d, #df9f00);
  background-size: 300% 300%;
  animation: placeholderGradient 3s ease infinite;
  flex-shrink: 0;
}

/* Размеры для «большого» placeholder */
.right-panel .big-placeholder {
  flex: 4 1 auto;
  min-height: 0;
  margin-bottom: 0.5rem;
}

/* Размеры для «малых» placeholder */
.right-panel .small-placeholder {
  flex: 0.5 1 auto;
  min-height: 0;
  margin-bottom: 0.5rem;
}

/* Картинка большого размера */
.content-image.big-image {
  flex: 2 1 auto;
  width: 100%;
  object-fit: contain;
  margin-bottom: 0.5rem;
}

/* Картинки-маленькие */
.content-image.small-image {
  flex: 1 1 auto;
  width: 100%;
  object-fit: contain;
  margin-bottom: 0.5rem;
}

/* Стили для аудио-плеера */
.audio-player {
  flex: 0 0 auto;
  width: 100%;
  margin-bottom: 0.5rem;
}

/* Кнопка «Медиатека генераций» */
.right-panel .media-library-button {
  flex: 0 0 auto;
  background-color: #0a0a15;
  color: #fff;
  font-family: 'MetaDat', sans-serif;
  font-size: calc(1rem + 0.5vw);
  border: none;
  border-radius: 8px;
  padding: 0.75rem;
  cursor: pointer;
  transition: background-color 0.3s;
  width: 100%;
  box-sizing: border-box;
  margin-top: auto;
  flex-shrink: 0;
}
.right-panel .media-library-button:hover {
  background-color: #2a2318;
}

/* ============================================================================ 
   7. Оверлей загрузки 
   ============================================================================ */
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
  margin-left: auto; margin-right: auto;  
  font-family: 'MetaDat';
  margin-top: 0;
  font-size: 1.8rem;
  color: #3c2f1e;
}
.loading-modal p {
  font-weight: 100;
  margin-left: 5%;
  font-family: 'MetaDat';
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

/* ============================================================================ 
   8. Футер страницы (фиксируется внизу) 
   ============================================================================ */
.page-footer {
  background-color: #0a0a15;
  color: #ce191d ;
  text-align: center;
  padding: 1rem 0;
  font-family: 'MetaDat', sans-serif;
  font-size: 1rem;
  flex-shrink: 0;
}

/* ============================================================================ 
   9. Медиазапросы для адаптации под разные экраны 
   ============================================================================ */

/* При ширине экрана 1200px–901px */
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

/* При ширине экрана 900px и ниже */
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
    padding: 0.5rem;
  }
  .disclaimer {
    font-size: calc(0.9rem + 0.3vw);
    max-height: 12vh;
  }
  .options-block .custom-checkbox {
    font-size: calc(0.9rem + 0.3vw);
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
    margin-top: 0.5rem;
  }
}

/* При ширине экрана 600px и ниже */
@media (max-width: 600px) {
  .page-container {
    padding: 0.25rem;
    gap: 0.25rem;
  }
  .left-panel,
  .right-panel {
    padding: 0.5rem;
  }
  .left-panel h1 {
    font-size: calc(1.1rem + 1.8vw);
  }
  .left-panel textarea {
    max-height: 20vh;
    font-size: calc(0.9rem + 0.8vw);
  }
  .generate-button,
  .exit-button,
  .media-library-button {
    font-size: calc(0.8rem + 1vw);
    padding: 0.4rem;
  }
  .disclaimer {
    font-size: calc(0.8rem + 0.4vw);
    max-height: 10vh;
  }
  .options-block .custom-checkbox {
    font-size: calc(0.8rem + 0.4vw);
  }
  .content-image.big-image,
  .content-image.small-image {
    width: 100%;
  }
}
</style>
