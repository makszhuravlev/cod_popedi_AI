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

const text = ref(`Прошедший день был трудный. Но всё-таки нашим взводам удалось в очередной раз отбить атаку противника и удержать позиции.`)

function generate(type) {
  alert(`Генерация типа: ${type}`)
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
