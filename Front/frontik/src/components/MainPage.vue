<template>
  <div class="container">
    <h1>Искусство через призму военных лет</h1>
    
    <button class="main-button" @click="gotohistory()">
      История запросов
    </button>
    
    <textarea
      id="description"
      rows="6"
      v-model="text"
      placeholder="Введите текст военного дневника..."
    ></textarea>

    <div class="button-group">
      <button @click="generate('text')">Создать текст</button>
      <button @click="generate('image')">Создать картинку</button>
      <button @click="generate('music')">Создать музыку</button>
      
    </div>
    
    <button class="main-button" @click="generate('all')">Сгенерировать</button>
    <button class="exit-button" @click="exit()">Выйти</button>

    <p class="text-muted">
      Сгенерированные произведения являются художественными и могут содержать неточные или вымышленные элементы
    </p>

    <!-- Окно загрузки -->
    <div v-if="isLoading" class="modal-overlay">
      <div class="modal-content loading-modal">
        <h2>Обработка запроса</h2>
        <p>Ваш запрос обрабатывается...</p>
        <div class="loader"></div>
      </div>
    </div>

    <!-- Окно результатов -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content">
        <h2>Результат генерации</h2>
        <div class="modal-body">
          <div v-if="generatedContent">
            <template v-if="resultType === 'text'">
              <p>{{ generatedContent.text }}</p>
            </template>

            <template v-else-if="resultType === 'image'">
              <img :src="generatedContent.image" alt="Сгенерированное изображение">
            </template>

            <template v-else-if="resultType === 'music'">
              <audio controls>
                <source :src="generatedContent.music" type="audio/mpeg">
              </audio>
            </template>

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

const text = ref('')
const showModal = ref(false)
const isLoading = ref(false)
const resultType = ref('')
const generatedContent = ref(null)
const WS_URL = `ws://88.84.211.248:8000/ws?token=${localStorage.getItem('access_token')}`
let typeg = ''

async function handleWebSocketRequest(data) {
  return new Promise((resolve, reject) => {
    const ws = new WebSocket(WS_URL)
    let buffer = ''
    let isResolved = false

    ws.onopen = () => ws.send(JSON.stringify(data))
    
    ws.onmessage = async (event) => {
      try {
        const chunk = event.data instanceof Blob 
          ? await event.data.text()
          : event.data
        
        buffer += chunk

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

function isCompleteResponse(buffer) {
  try {
    const data = JSON.parse(buffer)
    return data.status === 'success' || data.status === 'error'
  } catch (e) {
    return false
  }
}

onMounted(() => {
  if (!localStorage.getItem('access_token')) {
    router.push('/noauth')
  }
})

async function generate(type) {
  try {
    if (!text.value.trim()) {
      alert('Пожалуйста, введите текст для генерации')
      return
    }
    isLoading.value = true
    typeg = type
    await handleWebSocketRequest({
      action: type,
      text: text.value,
    })
  } catch (error) {
    console.error('Ошибка генерации:', error)
    alert(`Ошибка: ${error.message}`)
    isLoading.value = false
  }
}

async function viewcontent(response, type) {
  if (response.includes('Welcome')) return
  
  try {
    const data = JSON.parse(response)
    if (data.status === 'success') {
      const serverContent = {
        text: data.generated_text || "Текст не сгенерирован",
        image: `http://88.84.211.248:8000${data.image_urls}` || "",
        music: `http://88.84.211.248:8000${data.audio_url}` || ""
      }

      generatedContent.value = type === 'all' 
        ? serverContent
        : { [type]: serverContent[type] }

      resultType.value = type
      showModal.value = true
      isLoading.value = false
    }
  } catch (e) {
    isLoading.value = false
    console.error('Ошибка обработки ответа:', e)
  }
}

function closeModal() {
  showModal.value = false
  generatedContent.value = null
}

function gotohistory() {
  router.push('/history')
}

function exit() {
  localStorage.clear()
  router.push('/login')
}
</script>

<style scoped>
.container {
  align-items: center;
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
}

h1 {
  color: #3c2f1e;
  text-align: center;
  margin-bottom: 2rem;
}

textarea {
  width: 100%;
  height: 450px;
  font-size: 1rem;
  font-family: 'Georgia', serif;
  border: 2px solid #3c2f1e;
  border-radius: 8px;
  background-color: #fffef8;
  color: #3c2f1e;
  transition: border-color 0.3s, box-shadow 0.3s;
  outline: none;
  resize: none;
}

.button-group {
  display: flex;
  margin: -1rem 0;
  width: 100%;
  gap: 0.5rem;

}

.button-group button {
  flex: 2 1 calc(30% - 0.5rem);
  margin: 1rem 0;
  padding: 0.5rem;
  background-color: #5d4a36;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s;
}

button {

  border: none;
  border-radius: 5px;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
}

.main-button {
  margin: 0.5rem 0;
  background-color: #3c2f1e;
  width: 100%;
}

.exit-button {
  background-color: #990000;
  width: 100%;
}

.text-muted {
  color: #666;
  font-size: 0.8rem;
  margin-top: 1rem;
  text-align: center;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.7);
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

.loading-modal {
  text-align: center;
  padding: 2rem 3rem;
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

.modal-body img {
  max-width: 100%;
  height: auto;
  margin: 1rem 0;
  border-radius: 5px;
}

audio {
  width: 100%;
  margin: 15px 0;
  border-radius: 8px;
  overflow: hidden;
  background: #f5f1ea;
  box-shadow: 0 2px 4px rgba(60, 47, 30, 0.1);
}

audio::-webkit-media-controls-panel {
  background-color: #f5f1ea;
  border-radius: 8px;
}

.close-button {
  background-color: #990000;
  margin-top: 1rem;
}
</style>