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
import { compile, ref } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({ isLogin: Boolean })
const email = ref('')
const password = ref('')
const password1 = ref('')
const login  = ref('')
const router = useRouter()

const title = props.isLogin ? 'ВОЙТИ' : 'РЕГИСТРАЦИЯ'
const buttonText = props.isLogin ? 'ВОЙТИ' : 'ЗАРЕГИСТРИРОВАТЬСЯ'

function submit() {
if (props.isLogin){
  if(login.value && password.value){
    if (1){
      router.push('/home')
    }else{
      alert('Нету такого пользователя')
    }
  }else{
    alert('Заполнены не все поля')
  }
}else{
  if(login.value && password.value && password1.value && email.value){
    if(password.value === password1.value){
      if(1){
        router.push('/home')
      }else{
        alert('Пользователь с такими данными уже есть')
      }
   }else{
    alert('Пароли не совпадают')
   }
   }else{
    alert('Не все поля заполнены')
   }
}
}
</script>
