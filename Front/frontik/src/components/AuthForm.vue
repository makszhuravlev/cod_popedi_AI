<template>
  <!-- Основной контейнер формы -->
  <div class="container1">
    
    <img class='mainlogo' height=180rem src="../../public/logo1.png">
    <h1>{{ title }}</h1>
    <!-- Поле ввода логина -->
    <input type="text" placeholder="Логин" v-model="login" />

    <!-- Условное отображение поля email только для регистрации -->
    <input 
      type="email"
      pattern="/^[a-zA-Z0-9.!#$%&’*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$/"
      placeholder="Электронная почта"
      v-if="!isLogin"
      v-model="email"
    />

    <!-- Пароль и подтверждение пароля -->
    <input type="password" placeholder="Пароль" v-model="password" />
    <input 
      type="password" 
      placeholder="Подтвердите пароль" 
      v-if="!isLogin" 
      v-model="password1" 
    />

    <!-- Кнопка отправки формы -->
    <button @click="submit">{{ buttonText }}</button>

    <!-- Ссылки для перехода между формами -->
    <div class="link-row">
      <!-- Ссылка на вход для зарегистрированных пользователей -->
      <router-link v-if="!isLogin" to="/login"><br>Есть аккаунт?</router-link>
    </div>
    
    <div class="link-row1">
      <!-- Ссылка на регистрацию для новых пользователей -->
      <br><router-link class="reg" v-if="isLogin" to="/register">Зарегистрироваться</router-link>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

// Получение пропса для определения типа формы
const props = defineProps({ isLogin: Boolean })
const router = useRouter()

// Реактивные переменные для полей формы
const email = ref('')
const password = ref('')
const password1 = ref('')
const login = ref('')

// Очистка локального хранилища при монтировании компонента
onMounted(() => {
  localStorage.clear()
})

// Динамические заголовок и текст кнопки в зависимости от типа формы
const title = props.isLogin ? 'ВХОД' : 'РЕГИСТРАЦИЯ'
const buttonText = props.isLogin ? 'ВОЙТИ' : 'ЗАРЕГИСТРИРОВАТЬСЯ'

// Обработчик отправки формы
async function submit() {
  try {
    if (props.isLogin) {
      // === Логика авторизации ===
      
      // Валидация обязательных полей
      if (!login.value || !password.value) {
        throw new Error('Заполните все поля')
      }

      // Формирование данных для запроса
      const formData = new FormData()
      formData.append('username', login.value) // Соответствует OAuth2PasswordRequestForm
      formData.append('password', password.value)

      // Отправка запроса на сервер
      const response = await fetch('http://10.22.244.39:8000/token', {
        method: 'POST',
        body: formData
      })

      // Обработка ответа сервера
      const result = await response.json()

      if (!response.ok) {
        throw new Error(result.detail || 'Ошибка авторизации')
      }

      // Сохранение токена и перенаправление
      localStorage.setItem('access_token', result.access_token)
      router.push('/home')

    } else {
      // === Логика регистрации ===
      
      // Валидация полей формы
      if (!login.value || !email.value || !password.value || !password1.value) {
        throw new Error('Заполните все поля')
      }

      // Проверка совпадения паролей
      if (password.value !== password1.value) {
        throw new Error('Пароли не совпадают')
      }

      // Формирование данных для регистрации
      const data = JSON.stringify({
        email: email.value,
        login: login.value,
        password: password.value
      })

      // Отправка запроса на регистрацию
      const response = await fetch('http://10.22.244.39:8000/register', {
        method: 'POST',
        headers: {
          "Content-Type": 'application/json;charset=utf-8',
          "Content-Length": data.length,
        },
        body: data
      })

      // Обработка ответа сервера
      const result = await response.json()
      
      if (!response.ok) {
        throw new Error(result.detail || 'Ошибка регистрации')
      }

      // Уведомление и перенаправление
      alert('Успешная регистрация')
      router.push('/login')
    }
  } catch (error) {
    // Обработка ошибок
    alert(error.message)
  }
}
</script>

<style>
/* Стили основного контейнера формы */
.container1 {
  background-color: var(--bg-light);
  padding: 2rem;
  margin: 0rem auto;
  border-radius: 12px;
  max-width: 500px;
  width: 100%;
  text-align: center;
  box-shadow: 0 0 12px rgba(0, 0, 0, 0.2); /* Эффект тени */
}
</style>