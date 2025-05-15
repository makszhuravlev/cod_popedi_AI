<template>
  <div class="container">
    <h1>Искусство через призму военных лет</h1>

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

    <p class="text-muted">
      Сгенерированные произведения являются художественными и могут содержать неточные или вымышленные элементы
    </p>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const WS_URL = `ws:/88.84.211.248:8000/ws?token=${localStorage.getItem('access_token')}`
const text = ref('')
async function handleWebSocketRequest(data) {
  return new Promise((resolve, reject) => {
    const ws = new WebSocket(WS_URL)

    ws.onopen = () => ws.send(JSON.stringify(data))
    
    ws.onmessage = (event) => {
      try {
        const response = JSON.parse(event.data)
        ws.close()
        resolve(response)
      } catch (e) {
        reject(e)
      }
    }

    ws.onerror = (error) => {
      ws.close()
     
      reject(new Error('Ошибка соединения'))
    }

    setTimeout(() => {
      ws.close()
      reject(new Error('Таймаут соединения'))
    }, 5000)
  })
}
async function generate(type) {
  try {
      const response = await handleWebSocketRequest({
        action: type,
        text: text.value,
      })
      console.log(1)
      if (response.status == 'success') {
        alert('Начало генирации')
      } else {
        alert('Ошибка генирации')
      }
    }
    catch (error) {
      console.error('Ошибка:', error)
    }
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
</style>
