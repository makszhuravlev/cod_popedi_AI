<template>
  <div class="container1">
    <h1>{{ title }}</h1>
    <input type="text" placeholder="Логин" v-e v-model="login" />
    <input type="email" placeholder="Электронная почта" v-if="!isLogin" v-model="email" />
    <input type="password" placeholder="Пароль" v-model="password" />
    <input type="password" placeholder="Подтвердите пароль" v-if="!isLogin" v-model="password1" />

    <button @click="submit">{{ buttonText }}</button>

    <div class="link-row">
      <router-link v-if="!isLogin" to="/login"><br>Есть аккаунт?</router-link>
      
    </div>
    <div class="link-row1">
        <br><router-link class="reg" v-if="isLogin" to="/register">Зарегистрироваться</router-link>
        <router-link class="reg" v-if="isLogin" to="/register">Забыли пароль?</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({ isLogin: Boolean })
const router = useRouter()

// Refs
const email = ref('')
const password = ref('')
const password1 = ref('')
const login = ref('')

// Helpers
const title = props.isLogin ? 'ВОЙТИ' : 'РЕГИСТРАЦИЯ'
const buttonText = props.isLogin ? 'ВОЙТИ' : 'ЗАРЕГИСТРИРОВАТЬСЯ'

// Submit handler
async function submit() {
  try {
    if (props.isLogin) {
      // === Авторизация ===
      if (!login.value || !password.value) {
        throw new Error('Заполните все поля')
      }

      const formData = new FormData()
      formData.append('username', login.value)  // FastAPI OAuth2PasswordRequestForm
      formData.append('password', password.value)

      const response = await fetch('http://88.84.211.248:8000/token', {
        method: 'POST',
        body: formData
      })

      const result = await response.json()

      if (!response.ok) {
        throw new Error(result.detail || 'Ошибка авторизации')
      }

      localStorage.setItem('access_token', result.access_token)
      router.push('/home')

    } else {
      // === Регистрация ===
      if (!login.value || !email.value || !password.value || !password1.value) {
        throw new Error('Заполните все поля')
      }

      if (password.value !== password1.value) {
        throw new Error('Пароли не совпадают')
      }
      const data = JSON.stringify({
          email: email.value,
          login: login.value,
          password: password.value
        })
      const response = await fetch('http://88.84.211.248:8000/register', {
        method: 'POST',
        headers : {
            "Content-Type" : 'application/json;charset=utf-8',
            "Content-Length": data.length,
          },
          body: data
      })
      console.log(JSON.stringify({
          email: email.value,
          login: login.value,
          password: password.value
        }))
      const result = await response.json()
      
      if (!response.ok) {
        throw new Error(result.detail || 'Ошибка регистрации')
      }

      alert('Успешная регистрация')
      router.push('/login')
    }
  } catch (error) {
    alert(error.message)
  }
}


</script>
<style>
.container1 {
  background-color: var(--bg-light);
  padding: 2rem;
  margin: 2rem auto;
  border-radius: 12px;
  max-width: 500px;
  width: 100%;
  box-shadow: 0 0 12px rgba(0, 0, 0, 0.2);
}

</style>