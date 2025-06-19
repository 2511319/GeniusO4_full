import { useEffect } from "react";
import { useDispatch } from "react-redux";
import { setToken } from "../store";

export default function TelegramLoginButton() {
  const dispatch = useDispatch();

  useEffect(() => {
    // Создаем скрипт для Telegram Login Widget
    const script = document.createElement("script");
    script.src = "https://telegram.org/js/telegram-widget.js?22";
    script.dataset.telegramLogin = import.meta.env.VITE_TELEGRAM_BOT_USERNAME || "your_bot_username";
    script.dataset.size = "large";
    script.dataset.userpic = "false";
    script.dataset.requestAccess = "write";
    script.dataset.onauth = "handleTelegramAuth";
    
    // Добавляем скрипт в DOM
    const container = document.getElementById("tg-login-root");
    if (container) {
      container.appendChild(script);
    }

    // Глобальная функция для обработки аутентификации
    window.handleTelegramAuth = async (user) => {
      try {
        const response = await fetch("/auth/telegram", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(user),
        });

        if (response.ok) {
          const data = await response.json();
          const { access_token } = data;
          
          // Сохраняем токен в Redux store и localStorage
          dispatch(setToken(access_token));
          
          // Перезагружаем страницу для применения аутентификации
          window.location.reload();
        } else {
          console.error("Authentication failed:", response.statusText);
          alert("Ошибка аутентификации. Попробуйте еще раз.");
        }
      } catch (error) {
        console.error("Authentication error:", error);
        alert("Произошла ошибка при аутентификации.");
      }
    };

    // Cleanup function
    return () => {
      const container = document.getElementById("tg-login-root");
      if (container) {
        container.innerHTML = "";
      }
      delete window.handleTelegramAuth;
    };
  }, [dispatch]);

  return (
    <div className="telegram-login-container">
      <div className="mb-4 text-center">
        <h3 className="text-lg font-semibold mb-2">Войти через Telegram</h3>
        <p className="text-gray-600 text-sm mb-4">
          Быстрый и безопасный вход с помощью вашего Telegram аккаунта
        </p>
      </div>
      <div id="tg-login-root" className="flex justify-center py-4" />
    </div>
  );
}
