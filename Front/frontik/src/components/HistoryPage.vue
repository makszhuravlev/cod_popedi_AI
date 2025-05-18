<template>
  <button class="back-button" @click="goBack">
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M15 18L9 12L15 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
    Назад
  </button>
  
  <div class="history-container">
    <div v-if="historyEntries.length === 0" class="empty-history">
      <p>Ваша история запросов пока пуста</p>
    </div>

    <div v-else class="history-scroll">
      <div 
        v-for="entry in historyEntries"
        :key="entry.id"
        class="history-card"
        @click="showEntry(entry)"
      >
        <div class="card-header">
          <span class="type-badge" :class="entry.type">{{ getTypeLabel(entry.type) }}</span>
          <span class="date">{{ formatDate(entry.date) }}</span>
        </div>
        <div class="preview-text">{{ truncateText(entry.text) }}</div>
      </div>
    </div>

    <div v-if="selectedEntry" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content large-modal">
        <h2>Детали запроса от {{ formatDateTime(selectedEntry.date) }}</h2>
        <div class="modal-body">
          <div class="section">
            <h3>Исходный текст:</h3>
            <div class="original-text">{{ selectedEntry.text }}</div>
          </div>

          <div class="generated-content">
            <template v-if="selectedEntry.type === 'text'">
              <h3>Сгенерированный текст:</h3>
              <div class="text-content">{{ selectedEntry.content }}</div>
            </template>

            <template v-else-if="selectedEntry.type === 'image'">
              <h3>Изображение:</h3>
              <img :src="selectedEntry.content" alt="Сгенерированное изображение" class="generated-image">
            </template>

            <template v-else-if="selectedEntry.type === 'music'">
              <h3>Аудиозапись:</h3>
              <audio controls class="audio-player">
                <source :src="selectedEntry.content" type="audio/mpeg">
              </audio>
            </template>

            <template v-else-if="selectedEntry.type === 'all'">
              <div v-if="selectedEntry.content.text" class="content-section">
                <h3>Текстовая часть:</h3>
                <div class="text-content">{{ selectedEntry.content.text }}</div>
              </div>
              
              <div v-if="selectedEntry.content.image" class="content-section">
                <h3>Изображение:</h3>
                <img :src="selectedEntry.content.image" alt="Изображение" class="generated-image">
              </div>
              
              <div v-if="selectedEntry.content.music" class="content-section">
                <h3>Музыкальная композиция:</h3>
                <audio controls class="audio-player">
                  <source :src="selectedEntry.content.music" type="audio/mpeg">
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
const selectedEntry = ref(null)

const historyEntries = ref([
  {
    id: 1,
    type: 'text',
    text: 'Запрос пользователя',
    content: 'Весенний ветер шелестит, Цветы распускаются, мир манит...',
    date: new Date('2024-03-05T09:15:00')
  },
  {
    id: 1,
    type: 'text',
    text: 'Запрос пользователя',
    content: 'Весенний ветер шелестит, Цветы распускаются, мир манит...',
    date: new Date('2024-03-05T09:15:00')
  },
 
  

])

const typeLabels = {
  text: 'Текст',
  image: 'Изображение',
  music: 'Музыка',
  all: 'Комплексный'
}

onMounted(() => {
  if (!localStorage.getItem('access_token')) router.push('/noauth')
})

function getTypeLabel(type) {
  return typeLabels[type] || 'Неизвестный тип'
}

function formatDate(date) {
  return date.toLocaleDateString('ru-RU')
}

function formatDateTime(date) {
  return date.toLocaleString('ru-RU')
}

function truncateText(text, length = 100) {
  return text.length > length ? text.substring(0, length) + '...' : text
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
</script>

<style scoped>
.history-container {
  padding: 2rem;
  position: relative;
  min-height: 100vh;
}

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

.history-scroll {
  display: grid;
  gap: 1.5rem;
  padding: 2rem 0;
  grid-template-columns: repeat(1, 1fr);
}

@media (min-width: 768px) {
  .history-scroll {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .history-scroll {
    grid-template-columns: repeat(3, 1fr);
  }
}

.history-container {
  padding: 2rem;
  position: relative;
  min-height: 100vh;
  box-sizing: border-box;
}

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

.history-card {
  background: #fff;
  border-radius: 8px;
  padding: 1.5rem;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  border: 1px solid #e0e0e0;
  min-height: 150px;
  margin: 0 10px; /* Добавим небольшие отступы между карточками */
}

.type-badge.text { background: #e3f2fd; color: #1976d2; border-radius: 5px;}
.type-badge.image { background: #f0f4c3; color: #827717;border-radius: 5px; }
.type-badge.music { background: #f8bbd0; color: #c2185b; border-radius: 5px;}
.type-badge.all { background: #dcedc8; color: #689f38; border-radius: 5px;}

.date {
  font-weight: bold;
  color: #666;
  font-size: 0.9rem;
  padding-left: 10%;
}

.preview-text {
  color: #444;
  line-height: 1.5;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
}

.empty-history {
  text-align: center;
  padding: 4rem;
  color: #666;
  font-size: 1.2rem;
}

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
}

.large-modal {
  width: 90%;
  max-width: 1000px;
}

.generated-image {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  margin: 1rem 0;
}

.audio-player {
  width: 100%;
  margin: 1rem 0;
}

.section {
  margin-bottom: 2rem;
}

.original-text {
  white-space: pre-wrap;
  background: #f5f5f5;
  padding: 1rem;
  border-radius: 8px;
  margin: 1rem 0;
}

.text-content {
  line-height: 1.6;
  white-space: pre-wrap;
}

.content-section {
  margin: 2rem 0;
  padding: 1rem;
  background: #f8f8f8;
  border-radius: 8px;
}

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
    padding: 1rem 0;
  }
  
  .back-button {
    top: 0.5rem;
    left: 0.5rem;
    padding: 0.5rem 1rem;
  }
}
</style>