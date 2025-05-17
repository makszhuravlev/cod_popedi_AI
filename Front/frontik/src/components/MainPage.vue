<template>
  <div class="container">
    <h1>Искусство через призму военных лет</h1>

    <textarea
      id="description"
      rows="6"
      v-model="text"
      placeholder="Введите текст военного дневника..."
      :disabled="isLoading"
    ></textarea>

    <div class="button-group">
      <button @click="generate('text')" :disabled="isLoading">
        Создать текст
      </button>
      <button @click="generate('image')" :disabled="isLoading">
        Создать картинку
      </button>
      <button @click="generate('music')" :disabled="isLoading">
        Создать музыку
      </button>
    </div>
    
    <button class="main-button" @click="generate('all')" :disabled="isLoading">
      Сгенерировать
    </button>
    
    <button class="exit-button" @click="exit()" :disabled="isLoading">
      Выйти
    </button>

    <p class="text-muted">
      Сгенерированные произведения являются художественными и могут содержать неточные или вымышленные элементы
    </p>

    <!-- Модальное окно -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content">
        <h2>Результат генерации</h2>
        <div class="modal-body">
          <!-- Здесь будет отображаться контент -->
          <div v-if="generatedContent">
            <template v-if="resultType === 'text'">
              <p>{{ generatedContent }}</p>
            </template>
            <template v-else-if="resultType === 'image'">
              <img :src="generatedContent" alt="Сгенерированное изображение">
            </template>
            <template v-else-if="resultType === 'music'">
              <audio controls>
                <source :src="generatedContent" type="audio/mpeg">
              </audio>
            </template>
            <template v-else-if="resultType === 'all'">
              <!-- Комбинированный вывод -->
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
const resultType = ref('')
const generatedContent = ref(null)

// Check authentication
onMounted(() => {
  if (!localStorage.getItem('access_token')) {
    router.push('/noauth')
  }
})

async function generate(type) {
  if (!text.value.trim()) {
    alert('Пожалуйста, введите текст для генерации')
    return
  }

  // Замените эти ссылки на нужные вам
  const customContent = {
    text: "Деревня была где-то за лесом. Если идти в нее по большой дороге, нужно отмахать не один десяток километров; если пойти лесными тропинками, путь урежется вдвое. Толстые корни обхватили извилистую тропу. Лес шумит, успокаивает. В стылом воздухе кружатся жухлые листья. Тропинка, петляя среди деревьев, поднимается на пригорки, спускается в ложбинки, забираясь в чащобу осинника, выбегает на зарастающие ельником поляны, и кажется, что она так и не выведет тебя никуда.",
    image: "https://image.winudf.com/v2/image/bW9iaS5hbmRyb2FwcC5wcm9zcGVyaXR5YXBwcy5jNTExMV9zY3JlZW5fN18xNTI0MDQxMDUwXzAyMQ/screen-7.jpg?fakeurl=1&type=.jpg",
    music: "https://example.com/your-music.mp3"
  }

  generatedContent.value = type === 'all' 
    ? customContent
    : customContent[type]

  resultType.value = type
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  generatedContent.value = null
}

function exit() {
  localStorage.clear()
  router.push('/login')
}
</script>

<style scoped>
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

.button-group {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.button-group button {
  flex: 1 1 calc(33.333% - 0.5rem);
}

.main-button {
  margin-top: 0.5rem;
  background-color: #3c2f1e;
}

.exit-button {
  margin-top: 0.5rem;
  background-color: #990000;
}

button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

/* Стили для анимации загрузки */
.loader {
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 3px solid rgba(255,255,255,.3);
  border-radius: 50%;
  border-top-color: #fff;
  animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Стили для модального окна */
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

.modal-close {
  position: absolute;
  top: 10px;
  right: 10px;
  font-size: 1.5rem;
  background: none;
  border: none;
  cursor: pointer;
}

.modal-body {
  margin-top: 1rem;
}

.modal-body img {
  max-width: 100%;
  height: auto;
}

.text-muted {
  color: #666;
  font-size: 0.8rem;
  margin-top: 1rem;
}
/* Стили для кнопки закрытия */
.modal-close {
  position: absolute;
  top: 10px;
  right: 10px;
  font-size: 24px;
  background: none;
  border: none;
  cursor: pointer;
  color: #666;
  transition: color 0.3s;
}

.modal-close:hover {
  color: #000;
}

.modal-footer {
  text-align: right;
  margin-top: 20px;
  padding-top: 15px;
}

.close-button {
  padding: 8px 20px;
  background-color: #990000;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.close-button:hover {
  background-color: #770000;
}
audio {
  width: 100%;
  margin: 15px 0;
  border-radius: 8px;
  overflow: hidden;
  background: #f5f1ea;
  box-shadow: 0 2px 4px rgba(60, 47, 30, 0.1);
}

/* Базовые элементы управления */
audio::-webkit-media-controls-panel {
  background-color: #f5f1ea;
  border-radius: 8px;
}

/* Временная шкала */
audio::-webkit-media-controls-timeline {
  background-color: #d3c9b8;
  border-radius: 3px;
  margin: 0 10px;
}

/* Ползунок прогресса */
audio::-webkit-media-controls-current-time-display,
audio::-webkit-media-controls-time-remaining-display {
  font-family: 'Georgia', serif;
  color: #3c2f1e;
}

/* Кнопки управления */
audio::-webkit-media-controls-play-button,
audio::-webkit-media-controls-mute-button {
  background-color: #3c2f1e;
  border-radius: 50%;
  color: white;
}

audio::-webkit-media-controls-play-button:hover,
audio::-webkit-media-controls-mute-button:hover {
  background-color: #2d2417;
}

/* Полоса громкости */
audio::-webkit-media-controls-volume-slider {
  background-color: #d3c9b8;
  border-radius: 3px;
  height: 4px;
}

/* Иконка загрузки */
audio::-webkit-media-controls-loading-panel {
  background: #f5f1ea url('data:image/svg+xml;utf8,<svg...>') no-repeat center;
}

/* Для Firefox */
audio::-moz-range-track {
  background-color: #d3c9b8;
  height: 4px;
  border-radius: 3px;
}

audio::-moz-range-thumb {
  background: #3c2f1e;
  border: none;
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

/* Адаптация под тёмную тему */
@media (prefers-color-scheme: dark) {
  audio {
    background: #2d2417;
  }
  
  audio::-webkit-media-controls-panel {
    background-color: #2d2417;
  }
  
  audio::-webkit-media-controls-timeline {
    background-color: #3c2f1e;
  }
}

/* Общие состояния */
audio:focus {
  outline: 2px solid #990000;
  outline-offset: 2px;
}

audio::-webkit-media-controls {
  transition: all 0.3s ease;
}
</style>