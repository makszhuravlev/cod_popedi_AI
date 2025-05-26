import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import "./assets/style.css";
import IP_BACK from "../config.js";

createApp(App).use(router).mount("#app");
