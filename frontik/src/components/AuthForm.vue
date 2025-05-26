<template>
    <!-- Основной контейнер формы -->
    <img
        src="../assets/40коп.webp"
        alt="Описательный текст"
        style="position: absolute; top: 0; right: 0"
    />
    <div class="container1">
        <img class="mainlogo" height="180rem" src="../../public/logo3.webp" />
        <h1 class="tittle">{{ title }}</h1>
        <!-- Поле ввода логина -->
        <input
            type="text"
            class="placeholder"
            placeholder="Логин"
            v-model="login"
        />
        <!-- Условное отображение поля email только для регистрации -->
        <input
            class="placeholder"
            type="email"
            pattern="/^[a-zA-Z0-9.!#$%&’*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$/"
            placeholder="Электронная почта"
            v-if="!isLogin"
            v-model="email"
        />

        <!-- Пароль и подтверждение пароля -->
        <input
            type="password"
            class="placeholder"
            placeholder="Пароль"
            v-model="password"
        />
        <input
            class="placeholder"
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
            <router-link style="color: #ce191d" v-if="!isLogin" to="/login"
                ><br />Есть аккаунт?</router-link
            >
        </div>

        <div class="link-row1">
            <!-- Ссылка на регистрацию для новых пользователей -->
            <br /><router-link
                class="reg"
                style="color: #ce191d"
                v-if="isLogin"
                to="/register"
                >Зарегистрироваться</router-link
            >
        </div>
    </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { IP_BACK } from "@/config.js";

// Получение пропса для определения типа формы
const props = defineProps({ isLogin: Boolean });
const router = useRouter();

// Реактивные переменные для полей формы
const email = ref("");
const password = ref("");
const password1 = ref("");
const login = ref("");

// Очистка локального хранилища при монтировании компонента
onMounted(() => {
    localStorage.clear();
});

// Динамические заголовок и текст кнопки в зависимости от типа формы
const title = props.isLogin ? "ВХОД" : "РЕГИСТРАЦИЯ";
const buttonText = props.isLogin ? "ВОЙТИ" : "ЗАРЕГИСТРИРОВАТЬСЯ";

// Обработчик отправки формы
async function submit() {
    try {
        if (props.isLogin) {
            // === Логика авторизации ===

            // Валидация обязательных полей
            if (!login.value || !password.value) {
                throw new Error("Заполните все поля");
            }

            // Формирование данных для запроса
            const formData = new FormData();
            formData.append("username", login.value); // Соответствует OAuth2PasswordRequestForm
            formData.append("password", password.value);

            // Отправка запроса на сервер
            const response = await fetch("http://" + IP_BACK + ":8000/token", {
                method: "POST",
                body: formData,
            });

            // Обработка ответа сервера
            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.detail || "Ошибка авторизации");
            }

            // Сохранение токена и перенаправление
            localStorage.setItem("access_token", result.access_token);
            router.push("/home");
        } else {
            // === Логика регистрации ===

            // Валидация полей формы
            if (
                !login.value ||
                !email.value ||
                !password.value ||
                !password1.value
            ) {
                throw new Error("Заполните все поля");
            }

            // Проверка совпадения паролей
            if (password.value !== password1.value) {
                throw new Error("Пароли не совпадают");
            }

            // Формирование данных для регистрации
            const data = JSON.stringify({
                email: email.value,
                login: login.value,
                password: password.value,
            });

            // Отправка запроса на регистрацию
            const response = await fetch(
                "http://" + IP_BACK + ":8000/register",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json;charset=utf-8",
                        "Content-Length": data.length,
                    },
                    body: data,
                },
            );

            // Обработка ответа сервера
            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.detail || "Ошибка регистрации");
            }

            // Уведомление и перенаправление
            alert("Успешная регистрация");
            router.push("/login");
        }
    } catch (error) {
        // Обработка ошибок
        alert(error.message);
    }
}
</script>

<style>
/* Стили основного контейнера формы */
.container1 {
    font-family: "MetaDat";
    font-variant: normal;
    font-size: 1.3rem;
    background-color: #ebdfc2;
    padding: 1.2rem;
    margin: 2rem auto;
    border-radius: 12px;
    max-width: 500px;
    width: 100%;
    text-align: center;
}

.tittle {
    font-weight: 100;
    color: #ce191d;
}
.page-footer {
    background-color: #0a0a15;
    color: #ce191d;
    text-align: center;
    padding: 1rem 0;
    font-family: "MetaDat", sans-serif;
    font-size: 1rem;
    flex-shrink: 0;
}
.placeholder {
    background-color: #f6e5b0;
    border-color: #ce191d;
    font-size: 1.2rem;
    font-family: "TT";
}
</style>
