<template>
  <div class="container1">
    <h1>{{ title }}</h1>
    <input type="text" placeholder="Логин" v-if="!isLogin" v-e v-model="login" />
    <input type="email" placeholder="Электронная почта" v-model="email" />
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

// WebSocket
const WS_URL = 'ws://localhost:8000/ws'

// Helpers
const title = props.isLogin ? 'ВОЙТИ' : 'РЕГИСТРАЦИЯ'
const buttonText = props.isLogin ? 'ВОЙТИ' : 'ЗАРЕГИСТРИРОВАТЬСЯ'

// WebSocket handler
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

// Submit handler
async function submit() {
  try {
    if (props.isLogin) {
      // Login logic
      if (!email.value || !password.value) {
        throw new Error('Заполните все поля')
      }

      const response = await handleWebSocketRequest({
        action: 'login',
        email: email.value,
        password: password.value
      })

      if (response.status === 'success') {
        router.push('/home')
      } else {
        alert(response.message || 'Ошибка авторизации')
      }
    } else {
      // Registration logic
      if (!login.value || !email.value || !password.value || !password1.value) {
        throw new Error('Заполните все поля')
      }

      if (password.value !== password1.value) {
        throw new Error('Пароли не совпадают')
      }

      const hashedPassword = await hashPassword(password.value)

      const response = await handleWebSocketRequest({
        action: 'register',
        login: login.value,
        email: email.value,
        password: hashedPassword
      })

      if (response.status === 'success') {
        router.push('/home')
      } else {
        alert(response.message || 'Ошибка регистрации')
      }
    }
  } catch (error) {
    alert(error.message)
  }
}

// Hash function
async function hashPassword(password) {
  if (!window.crypto?.subtle) {
    throw new Error('Требуется безопасное соединение (HTTPS)')
  }

  const salt = crypto.getRandomValues(new Uint8Array(16))
  const encoder = new TextEncoder()
  const passwordBuffer = encoder.encode(password)

  const importedKey = await crypto.subtle.importKey(
    'raw',
    passwordBuffer,
    { name: 'PBKDF2' },
    false,
    ['deriveBits']
  )

  const derivedBits = await crypto.subtle.deriveBits(
    {
      name: 'PBKDF2',
      salt,
      iterations: 600000,
      hash: 'SHA-256'
    },
    importedKey,
    256
  )

  const hashArray = new Uint8Array(derivedBits)
  const saltHex = Array.from(salt)
    .map(b => b.toString(16).padStart(2, '0')).join('')
  const hashHex = Array.from(hashArray)
    .map(b => b.toString(16).padStart(2, '0')).join('')
  
  return `${saltHex}:${hashHex}`
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