<template>
  <div class="container">
    <h1>{{ title }}</h1>
    <input type="email" placeholder="Логин" v-if="!isLogin" v-e v-model="email" />
    <input type="email" placeholder="Электронная почта" v-model="email" />
    <input type="password" placeholder="Пароль" v-model="password" />
    <input type="password" placeholder="Подтвердите пароль" v-if="!isLogin" v-model="password" />

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

const router = useRouter()

const title = props.isLogin ? 'ВОЙТИ' : 'РЕГИСТРАЦИЯ'
const buttonText = props.isLogin ? 'ВОЙТИ' : 'ЗАРЕГИСТРИРОВАТЬСЯ'

function submit() {
  if (email.value && password.value) {
    router.push('/home')
  } else {
    alert('Пожалуйста, заполните все поля.')
  }
}
</script>
