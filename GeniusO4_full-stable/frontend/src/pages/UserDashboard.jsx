import React from 'react';

export default function UserDashboard() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Кабинет пользователя</h1>
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-gray-600">Добро пожаловать в кабинет пользователя!</p>
          <p className="text-sm text-gray-500 mt-2">Здесь будет отображаться информация о вашем аккаунте.</p>
        </div>
      </div>
    </div>
  );
}
