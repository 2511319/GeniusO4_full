import { useSelector } from "react-redux";
import { Navigate } from "react-router-dom";
import TelegramLoginButton from "../components/TelegramLoginButton";

export default function Login() {
  const token = useSelector((state) => state.auth.token);

  // Если пользователь уже авторизован, перенаправляем на главную
  if (token) {
    return <Navigate to="/" replace />;
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">GeniusO4</h1>
          <p className="text-gray-600">Профессиональный анализ криптовалют с ИИ</p>
        </div>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          <div className="space-y-6">
            <div className="text-center">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                Добро пожаловать!
              </h2>
              <p className="text-gray-600 text-sm mb-6">
                Войдите в систему, чтобы получить доступ к профессиональному анализу криптовалют
              </p>
            </div>

            <TelegramLoginButton />

            <div className="mt-6">
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-gray-300" />
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-2 bg-white text-gray-500">или</span>
                </div>
              </div>
            </div>

            <div className="text-center">
              <p className="text-sm text-gray-600">
                Используйте наш{" "}
                <a 
                  href="https://t.me/your_bot_username" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="font-medium text-blue-600 hover:text-blue-500"
                >
                  Telegram бот
                </a>{" "}
                для быстрого доступа к анализу
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-8 text-center">
        <p className="text-xs text-gray-500">
          Входя в систему, вы соглашаетесь с нашими условиями использования
        </p>
      </div>
    </div>
  );
}
