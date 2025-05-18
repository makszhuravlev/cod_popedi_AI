<template>
  <!-- Основной контейнер приложения -->
  <div class="container">
    <h1>Искусство через призму военных лет</h1>
    
    <!-- Кнопка перехода к истории запросов -->
    <button class="main-button" @click="gotohistory()">
      История запросов
    </button>
    
    <!-- Текстовое поле для ввода дневника -->
    <textarea
      id="description"
      rows="6"
      v-model="text"
      placeholder="Введите текст военного дневника..."
    ></textarea>

    <!-- Группа кнопок для выбора типа генерации -->
    <div class="button-group">
      <button @click="generate('text')">Создать текст</button>
      <button @click="generate('image')">Создать картинку</button>
      <button @click="generate('music')">Создать музыку</button>
    </div>
    
    <!-- Основные действия -->
    <button class="main-button" @click="generate('all')">Сгенерировать</button>
    <button class="exit-button" @click="exit()">Выйти</button>

    <!-- Информационное сообщение -->
    <p class="text-muted">
      Сгенерированные произведения являются художественными и могут содержать неточные или вымышленные элементы
    </p>

    <!-- Модальное окно с результатами генерации -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content">
        <h2>Результат генерации</h2>
        <div class="modal-body">
          <!-- Динамическое отображение контента в зависимости от типа -->
          <div v-if="generatedContent">
            <!-- Вывод текста -->
            <template v-if="resultType === 'text'">
              <p>{{ generatedContent.text }}</p>
            </template>

            <!-- Вывод изображения -->
            <template v-else-if="resultType === 'image'">
              <img :src="generatedContent.image" alt="Сгенерированное изображение">
            </template>

            <!-- Вывод аудио -->
            <template v-else-if="resultType === 'music'">
              <audio controls>
                <source :src="generatedContent.music" type="audio/mpeg">
              </audio>
            </template>

            <!-- Комбинированный вывод для типа 'all' -->
            <template v-else-if="resultType === 'all'">
              <div v-if="generatedContent.text">
                <h3>Текст:</h3>
                <p>{{ generatedContent.text }}</p>
              </div>
              <div v-if="generatedContent.image">
                <h3>Изображение:</h3>
                <img :src="generatedContent.image" alt="Изображение">
              </div>
              <div v-if="generatedContent.music">
                <h3>Музыка:</h3>
                <audio controls>
                  <source :src="generatedContent.music" type="audio/mpeg">
                </audio>
              </div>
            </template>
          </div>
        </div>
        
        <!-- Футер модального окна -->
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

// Реактивные переменные состояния
const text = ref('') // Текст из текстового поля
const showModal = ref(false) // Видимость модального окна
const resultType = ref('') // Тип результата генерации
const generatedContent = ref(null) // Сгенерированный контент
const WS_URL = `ws://88.84.211.248:8000/ws?token=${localStorage.getItem('access_token')}` // WebSocket URL
let typeg = '' // Временная переменная для типа генерации

/**
 * Обработчик WebSocket соединения
 * @param {Object} data - Данные для отправки
 * @returns {Promise} - Обещание с результатом запроса
 */
async function handleWebSocketRequest(data) {
  return new Promise((resolve, reject) => {
    const ws = new WebSocket(WS_URL)
    let buffer = ''
    let isResolved = false

    // Обработчики событий WebSocket
    ws.onopen = () => ws.send(JSON.stringify(data))
    
    ws.onmessage = async (event) => {
      try {
        // Обработка входящих данных
        const chunk = event.data instanceof Blob 
          ? await event.data.text()
          : event.data
        
        buffer += chunk

        // Проверка завершения передачи
        if (isCompleteResponse(buffer)) {
          isResolved = true
          try {
            const response = JSON.parse(buffer)
            ws.close(1000, 'Normal closure')
            resolve(response)
          } catch (e) {
            ws.close(4000, 'Parsing error')
            reject(e)
          }
        }
        
        // Обновление UI в реальном времени
        viewcontent(chunk, typeg)
      } catch (e) {
        ws.close(4000, 'Processing error')
        reject(e)
      }
    }

    ws.onerror = (error) => {
      if (!isResolved) {
        ws.close(4000, 'WebSocket error')
        reject(new Error(`WebSocket error: ${error.message}`))
      }
    }

    ws.onclose = (event) => {
      if (!isResolved) {
        try {
          const response = JSON.parse(buffer)
          resolve(response)
        } catch (e) {
          reject(new Error(`Connection closed: ${event.reason} | Buffer: ${buffer.substring(0, 100)}`))
        }
      }
    }
  })
}

/**
 * Проверка завершенности ответа
 * @param {string} buffer - Буфер данных
 * @returns {boolean} - Флаг завершения
 */
function isCompleteResponse(buffer) {
  try {
    const data = JSON.parse(buffer)
    return data.status === 'success' || data.status === 'error'
  } catch (e) {
    return false
  }
}

// Проверка аутентификации при монтировании
onMounted(() => {
  if (!localStorage.getItem('access_token')) {
    router.push('/noauth')
  }
})

/**
 * Инициирует процесс генерации контента
 * @param {string} type - Тип генерации (text/image/music/all)
 */
async function generate(type) {
  try {
    if (!text.value.trim()) {
      alert('Пожалуйста, введите текст для генерации')
      return
    }
    typeg = type
    await handleWebSocketRequest({
      action: type,
      text: text.value,
    })
  } catch (error) {
    console.error('Ошибка генерации:', error)
    alert(`Ошибка: ${error.message}`)
  }
}

/**
 * Обрабатывает и отображает полученный контент
 * @param {string} response - Ответ от сервера
 * @param {string} type - Тип контента
 */
async function viewcontent(response, type) {
  if (response.includes('Welcome')) return
  
  try {
    const data = JSON.parse(response)
    if (data.status === 'success') {
      // Формирование объекта контента
      const serverContent = {
        text: data.generated_text || "Текст не сгенерирован",
        image: `http://88.84.211.248:8000${data.image_urls}` || "",
        music: `http://88.84.211.248:8000${data.audio_url}` || ""
      }

      // Обновление состояния в зависимости от типа
      generatedContent.value = type === 'all' 
        ? serverContent
        : { [type]: serverContent[type] }

      resultType.value = type
      showModal.value = true
    }
  } catch (e) {
    console.error('Ошибка обработки ответа:', e)
  }
}

// Закрытие модального окна
function closeModal() {
  showModal.value = false
  generatedContent.value = null
}

// Навигация
function gotohistory() {
  router.push('/history')
}

function exit() {
  localStorage.clear()
  router.push('/login')
}
</script>

<style scoped>
/* Основные стили текстового поля */
textarea {
  width: 100%;
  height: 450px;
  padding: 0.85rem 1rem;
  font-size: 1rem;
  font-family: 'Georgia', serif;
  border: 2px solid var(--accent);
  border-radius: 8px;
  background-color: #fffef8;
  color: var(--text-main);
  transition: border-color 0.3s, box-shadow 0.3s;
  outline: none;
  resize: none;
}

/* Стили группы кнопок */
.button-group {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.button-group button {
  flex: 1 1 calc(33.333% - 0.5rem);
}

/* Стили модального окна */
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
  max-width: 80%;
  max-height: 80vh;
  overflow-y: auto;
  position: relative;
}

/* Стили аудио-плеера */
audio {
  width: 100%;
  margin: 15px 0;
  border-radius: 8px;
  overflow: hidden;
  background: #f5f1ea;
  box-shadow: 0 2px 4px rgba(60, 47, 30, 0.1);
}

/* Адаптация элементов управления аудио */
audio::-webkit-media-controls-panel {
  background-color: #f5f1ea;
  border-radius: 8px;
}

/* Дополнительные стили для кнопок и текста */
.main-button { background-color: #3c2f1e; margin-bottom: 1rem;}
.exit-button { background-color: #990000; }
.text-muted { color: #666; font-size: 0.8rem; }
.close-button { background-color: #990000; }
</style>