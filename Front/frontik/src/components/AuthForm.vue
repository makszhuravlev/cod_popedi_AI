<template>
  <div class="container">
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
const email = ref('')
const password = ref('')
const password1 = ref('')
const login = ref('')
const router = useRouter()

const WS_URL = ''
const title = props.isLogin ? 'ВОЙТИ' : 'РЕГИСТРАЦИЯ'
const buttonText = props.isLogin ? 'ВОЙТИ' : 'ЗАРЕГИСТРИРОВАТЬСЯ'

async function handleWebSocketRequest(data) {
  return new Promise((resolve, reject) => {
    const ws = new WebSocket(WS_URL)

    ws.onopen = () => {
      ws.send(JSON.stringify(data))
    }

    ws.onmessage = (event) => {
      const response = JSON.parse(event.data)
      ws.close()
      resolve(response)
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

async function submit() {
  try {
    if (props.isLogin) {
      console.log(WS_URL)
      // Логин: отправляем email и чистый пароль
      if (!email.value || !password.value) {
        throw new Error('Заполнены не все поля')
      }

      const response = await handleWebSocketRequest({
        action: 'login',
        email: email.value,
        password: password.value // Отправляем исходный пароль
      })

      if (response.success) {
        router.push('/home')
      } else {
        alert(response.message || 'Ошибка аутентификации')
      }
    } else {
      // Регистрация: хешируем пароль перед отправкой
      if (!login.value || !email.value || !password.value || !password1.value) {
        throw new Error('Не все поля заполнены')
      }

      if (password.value !== password1.value) {
        throw new Error('Пароли не совпадают')
      }

      const hashedPassword = await hashPassword(password.value)

      const response = await handleWebSocketRequest({
        action: 'register',
        login: login.value,
        email: email.value,
        password: hashedPassword // Отправляем соль:хеш
      })

      if (response.success) {
        router.push('/home')
      } else {
        alert(response.message || 'Ошибка регистрации')
      }
    }
  } catch (error) {
    alert(error.message)
  }
}

// Функция хеширования для регистрации
async function hashPassword(password) {
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
  const saltHex = Array.from(salt).map(b => b.toString(16).padStart(2, '0')).join('')
  const hashHex = Array.from(hashArray).map(b => b.toString(16).padStart(2, '0')).join('')
  return `${saltHex}:${hashHex}`
}


</script>
