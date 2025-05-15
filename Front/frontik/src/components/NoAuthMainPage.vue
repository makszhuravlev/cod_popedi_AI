<template>
  <div class="container">
    <h1>Вы попытались зайти без авторизации</h1>

    <button class="exit-button" @click="exit()">Уйти отсюда</button>

    <p class="text-muted">
      Пожалуйста пройдите авторизацию
    </p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'


const router = useRouter()
const WS_URL = `ws:/88.84.211.248:8000/ws?token=${localStorage.getItem('access_token')}`
const text = ref('')

function exit() {
  localStorage.clear();
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
</style>
