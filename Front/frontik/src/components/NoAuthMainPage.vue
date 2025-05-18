<template>
  <!-- Основной контейнер для сообщения о неавторизованном доступе -->
  <div class="container">
    <h1>Вы попытались зайти без авторизации</h1>

    <!-- Кнопка выхода с обработчиком события -->
    <button class="exit-button" @click="exit()">Уйти отсюда</button>

    <!-- Информационное сообщение -->
    <p class="text-muted">
      Пожалуйста пройдите авторизацию
    </p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

/**
 * Функция для выхода из системы
 * Очищает локальное хранилище и перенаправляет на страницу входа
 */
function exit() {
  localStorage.clear();
  router.push('/login')
}
</script>

<style scoped>
/* Стилизация элементов (некоторые стили могут быть избыточны для этого компонента) */

/* Стили для текстового поля (в текущем компоненте не используется) */
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

/* Стили для группы кнопок (в текущем компоненте не используется) */
.button-group {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.button-group button {
  flex: 1 1 calc(33.333% - 0.5rem);
}

/* Стиль основной кнопки (в текущем компоненте не используется) */
.main-button {
  margin-top: 0.5rem;
  background-color: #3c2f1e;
}

/* Стиль кнопки выхода */
.exit-button {
  margin-top: 0.5rem;
  background-color: #990000;
}
</style>