<template>
  <button class="back-button" @click="goBack">
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none"
         xmlns="http://www.w3.org/2000/svg">
      <path d="M15 18L9 12L15 6" stroke="currentColor" stroke-width="2"
            stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
    Назад
  </button>
  
  <div class="history-container">
    <!-- Если история ещё не загрузилась или пуста -->
    <div v-if="historyEntries.length === 0" class="empty-history">
      <p>Ваша история запросов пока пуста</p>
    </div>

    <!-- Если есть записи, строим сетку карточек по горизонтали -->
    <div v-else class="history-scroll">
      <div 
        v-for="entry in historyEntries"
        :key="entry.id"
        class="history-card"
        @click="showEntry(entry)"
      >
        <div class="card-header">
          <span class="id-badge">ID: {{ entry.id }}</span>
          <span v-if="entry.date" class="date">{{ formatDate(entry.date) }}</span>
        </div>
        <div class="preview-text">{{ truncateText(entry.reference_text) }}</div>
      </div>
    </div>

    <!-- Модальное окно с деталями выбранной записи -->
    <div v-if="selectedEntry" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content large-modal">
        <h2>Детали запроса #{{ selectedEntry.id }} от {{ formatDateTime(selectedEntry.date) }}</h2>
        <div class="modal-body">
          <div class="section">
            <h3>Исходный текст:</h3>
            <div class="original-text">{{ selectedEntry.reference_text }}</div>
          </div>

          <!-- Блок для отображения картинок -->
          <div v-if="selectedEntry.images && selectedEntry.images.length" class="section">
            <h3>Изображения:</h3>
            <div class="images-list">
              <img
                v-for="(imgSrc, idx) in selectedEntry.images"
                :key="idx"
                :src="imgSrc"
                alt="Изображение"
                class="generated-image"
                @error="onImageError(imgSrc)"
              />
            </div>
          </div>

          <!-- Блок для отображения аудио (песен) -->
          <div v-if="selectedEntry.music && selectedEntry.music.length" class="section">
            <h3>Аудиозаписи:</h3>
            <div class="music-list">
              <audio
                v-for="(mSrc, idx) in selectedEntry.music"
                :key="idx"
                controls
                class="audio-player"
              >
                <source :src="mSrc" type="audio/mpeg" />
                Ваш браузер не поддерживает элемент <code>audio</code>.
              </audio>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="close-button" @click="closeModal">Закрыть</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const selectedEntry = ref(null)

// Массив карточек — каждая запись соответствует одному id из сервера
const historyEntries = ref([])

// WebSocket-URL с токеном
const WS_URL = `ws://88.84.211.248:8000/ws?token=${localStorage.getItem('access_token')}`

// Базовый URL, добавляемый перед относительными путями к изображениям и аудио
const BASE_URL = 'http://88.84.211.248:8000'

// Универсальная функция для отправки JSON-запроса по WebSocket и ожидания полного ответа
function handleWebSocketRequest(data) {
  return new Promise((resolve, reject) => {
    let buffer = ''
    let isResolved = false
    const ws = new WebSocket(WS_URL)

    ws.onopen = () => {
      ws.send(JSON.stringify(data))
    }

    ws.onmessage = async (event) => {
      if (isResolved) return

      try {
        const chunk = event.data instanceof Blob 
          ? await event.data.text() 
          : event.data
        buffer += chunk

        try {
          const parsed = JSON.parse(chunk)
          if (parsed.status === 'success' || parsed.status === 'error') {
            isResolved = true
            ws.close()
            resolve(parsed)
          }
        } catch {
          // JSON ещё неполный
        }
      } catch (err) {
        if (!isResolved) {
          isResolved = true
          ws.close()
          reject(err)
        }
      }
    }

    ws.onerror = (err) => {
      if (!isResolved) {
        isResolved = true
        ws.close()
        reject(new Error(`WebSocket error: ${err.message}`))
      }
    }

    ws.onclose = (event) => {
      if (!isResolved) {
        isResolved = true
        const reason = event.reason || 'без указания причины'
        reject(new Error(`Соединение закрыто: ${reason}`))
      }
    }
  })
}

// Формат “дд.мм.гггг”
function formatDate(date) {
  return date ? new Date(date).toLocaleDateString('ru-RU') : ''
}
// Формат “дд.мм.гггг, чч:мм:сс”
function formatDateTime(date) {
  return date ? new Date(date).toLocaleString('ru-RU') : ''
}

// Обрезаем текст до заданной длины
function truncateText(text, length = 100) {
  return text && text.length > length ? text.substring(0, length) + '...' : text
}

function showEntry(entry) {
  selectedEntry.value = entry
}

function closeModal() {
  selectedEntry.value = null
}

function goBack() {
  router.push('/home')
}

// Обработчик ошибок загрузки изображений
function onImageError(src) {
  console.warn(`Не удалось загрузить изображение: ${src}`)
}

// При монтировании компонента — запрос истории
onMounted(async () => {
  if (!localStorage.getItem('access_token')) {
    router.push('/noauth')
    return
  }

  const payload = { action: 'get_history' }
  try {
    const parsed = await handleWebSocketRequest(payload)
    if (parsed.status === 'success' && parsed.data && Array.isArray(parsed.data.requests)) {
      const requests = parsed.data.requests

      historyEntries.value = requests.map(req => {
        // Приводим req.images к массиву строк
        const imagesArray = Array.isArray(req.images)
          ? req.images.filter(i => typeof i === 'string')
          : []
        const prefixedImages = imagesArray.map(img => {
          return img.startsWith('http://') || img.startsWith('https://')
            ? img
            : `${BASE_URL}${img}`
        })

        // Приводим req.music к массиву строк
        const musicArray = Array.isArray(req.music)
          ? req.music.filter(m => typeof m === 'string')
          : []
        const prefixedMusic = musicArray.map(m => {
          return m.startsWith('http://') || m.startsWith('https://')
            ? m
            : `${BASE_URL}${m}`
        })

        return {
          id: req.id,
          reference_text: req.reference_text || '',
          date: req.date || '',
          images: prefixedImages,
          music: prefixedMusic
        }
      })
      console.log('historyEntries after prefix:', historyEntries.value)
    } else {
      console.error('Не удалось получить историю или формат ответа неожиданный:', parsed)
    }
  } catch (err) {
    console.error('Ошибка при запросе истории:', err)
  }
})
</script>

<style scoped>

.history-scroll {
  display: grid;
  gap: 1.5rem;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  width: 100%;
  max-width: 100vw;
  padding: 2rem 0;
}

@media (min-width: 768px) {
  .history-scroll {
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  }
}







.history-container {
  padding: 2rem;
  position: relative;
  min-height: 100vh;
  box-sizing: border-box;
}

/* Кнопка «Назад» */
.back-button {
  position: absolute;
  top: 20px;
  left: 20px;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.8rem 1.5rem;
  background: none;
  border: 2px solid #990000;
  border-radius: 8px;
  color: #990000;
  cursor: pointer;
  transition: all 0.3s;
  z-index: 100;
}
.back-button:hover {
  background-color: rgba(60, 47, 30, 0.1);
}

/* Контейнер карточек истории: отображается сеткой, несколько колонок, начиная слева сверху */
.history-scroll {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
  width: 100%;
  padding-top: 4rem;
  box-sizing: border-box;
}

/* Каждая карточка занимает минимум 300px и автоматически расширяется до равномерной ширины */
.history-card {
  background: #fff;
  border-radius: 8px;
  padding: 1.5rem;
  cursor: pointer;
  border: 1px solid #e0e0e0;
  transition: transform 0.2s, box-shadow 0.2s;
  box-sizing: border-box;
}
.history-card:hover {
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  transform: translateY(-2px);
}

/* Шапка карточки: ID и дата */
.card-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.id-badge {
  font-weight: bold;
  color: #990000;
}

.date {
  font-size: 0.9rem;
  color: #666;
}

/* Превью текста */
.preview-text {
  color: #444;
  line-height: 1.5;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
}

/* Пустая история */
.empty-history {
  text-align: center;
  padding: 4rem;
  color: #666;
  font-size: 1.2rem;
}

/* Модальное окно */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  padding: 2rem;
  border-radius: 8px;
  max-width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
  box-sizing: border-box;
}

/* Ограничиваем ширину модала */
.large-modal {
  width: 90%;
  max-width: 800px;
}

/* Секции внутри модального окна */
.section {
  margin-bottom: 2rem;
}

/* Исходный текст */
.original-text {
  white-space: pre-wrap;
  background: #f5f5f5;
  padding: 1rem;
  border-radius: 8px;
}

/* Список картинок */
.images-list {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

/* Отображение одной картинки */
.generated-image {
  max-width: 200px;
  border-radius: 8px;
  object-fit: cover;
}

/* Список аудиозаписей */
.music-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* Отображение одного аудио-плеера */
.audio-player {
  width: 100%;
}

/* Кнопка «Закрыть» в модальном окне */
.close-button {
  padding: 0.8rem 1.5rem;
  background-color: #3c2f1e;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.3s;
}
.close-button:hover {
  background-color: #2d2417;
}

@media (max-width: 768px) {
  .history-container {
    padding: 1rem;
  }
  
  .history-scroll {
    padding-top: 1rem;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  }
  
  .back-button {
    top: 0.5rem;
    left: 0.5rem;
    padding: 0.5rem 1rem;
  }
}
</style>
