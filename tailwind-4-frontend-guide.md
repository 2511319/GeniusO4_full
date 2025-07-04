# Руководство по работе с Frontend элементами в Tailwind CSS 4.0+

## 🎯 Основные принципы работы

### 1. CSS-first подход
В Tailwind CSS 4.0+ конфигурация происходит через CSS, а не через JavaScript файлы:

```css
@theme {
  --color-primary: #2563eb;
  --color-secondary: #fb923c;
  --radius: 0.75rem;
}
```

### 2. Современная архитектура
- **@tailwindcss/vite** плагин для оптимальной производительности
- **Автоматическое обнаружение контента** - не нужно настраивать content
- **Встроенные container queries** без дополнительных плагинов
- **3D трансформации** и современные CSS функции

## 🏗️ Структура компонентов

### Базовые компоненты (уже реализованы)

#### Кнопки:
```jsx
// Основная кнопка
<button className="btn btn-primary">Запустить анализ</button>

// Вторичная кнопка
<button className="btn btn-secondary">Сохранить</button>

// Контурная кнопка
<button className="btn btn-outline">Отмена</button>

// Размеры
<button className="btn btn-primary btn-sm">Маленькая</button>
<button className="btn btn-primary btn-md">Средняя</button>
<button className="btn btn-primary btn-lg">Большая</button>
```

#### Карточки:
```jsx
<div className="card">
  <div className="card-header">
    <h3 className="card-title">Заголовок</h3>
    <p className="card-description">Описание</p>
  </div>
  <div className="card-content">
    Содержимое карточки
  </div>
  <div className="card-footer">
    <button className="btn btn-primary">Действие</button>
  </div>
</div>
```

#### Поля ввода:
```jsx
<input 
  type="text" 
  className="input" 
  placeholder="Введите значение"
/>
```

### Layout компоненты

#### Grid система:
```jsx
// Основной layout (как в Home.jsx)
<div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
  <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
    {/* Левая панель */}
    <div className="lg:col-span-3">
      <div className="bg-white rounded-lg shadow p-4">
        Боковая панель
      </div>
    </div>
    
    {/* Центральная область */}
    <div className="lg:col-span-6">
      <div className="bg-white rounded-lg shadow p-4">
        Основной контент
      </div>
    </div>
    
    {/* Правая панель */}
    <div className="lg:col-span-3">
      <div className="bg-white rounded-lg shadow p-4">
        Результаты
      </div>
    </div>
  </div>
</div>
```

## 🎨 Работа с цветами

### Семантические цвета:
```jsx
// Фон и текст
<div className="bg-background text-foreground">
  Основной контент
</div>

// Приглушенные элементы
<div className="bg-muted text-muted-foreground">
  Вторичная информация
</div>

// Карточки
<div className="bg-card text-card-foreground border border-border">
  Карточка
</div>

// Акценты
<div className="bg-accent text-accent-foreground">
  Выделенный элемент
</div>
```

### Цветовая палитра:
```jsx
// Основные цвета
<div className="bg-primary text-white">Основной</div>
<div className="bg-secondary text-white">Вторичный</div>

// Состояния
<div className="bg-green-500 text-white">Успех</div>
<div className="bg-red-500 text-white">Ошибка</div>
<div className="bg-destructive text-destructive-foreground">Опасно</div>
```

## 📱 Responsive дизайн

### Breakpoints:
```jsx
<div className="
  grid 
  grid-cols-1 
  sm:grid-cols-2 
  md:grid-cols-3 
  lg:grid-cols-4 
  xl:grid-cols-6
">
  Адаптивная сетка
</div>
```

### Container queries (новое в 4.0+):
```jsx
<div className="@container">
  <div className="@sm:grid-cols-2 @md:grid-cols-3">
    Контейнерные запросы
  </div>
</div>
```

## 🎭 Анимации и переходы

### Встроенные анимации:
```jsx
// Появление
<div className="animate-in fade-in slide-in-from-bottom-4">
  Плавное появление
</div>

// Исчезновение
<div className="animate-out fade-out slide-out-to-top-4">
  Плавное исчезновение
</div>

// Пульсация
<div className="animate-pulse">
  Загрузка...
</div>

// Вращение
<div className="animate-spin">
  ⟳
</div>
```

### Переходы:
```jsx
<button className="
  transition-all 
  duration-200 
  hover:scale-105 
  hover:shadow-lg
">
  Интерактивная кнопка
</button>
```

## 🔧 Утилиты и хелперы

### Скрытие скроллбара:
```jsx
<div className="scrollbar-hide overflow-auto">
  Контент без видимого скроллбара
</div>
```

### Баланс текста:
```jsx
<h1 className="text-balance">
  Заголовок с балансированным переносом
</h1>
```

### Водяные знаки:
```jsx
<div className="watermark">Основной водяной знак</div>
<div className="watermark-chart">Для графиков</div>
<div className="watermark-summary">Для сводок</div>
<div className="watermark-explanations">Для объяснений</div>
<div className="watermark-export">Для экспорта</div>
```

## 🌙 Темная тема

Автоматическая поддержка темной темы через CSS:

```css
@media (prefers-color-scheme: dark) {
  @theme {
    --color-background: #0f172a;
    --color-foreground: #f8fafc;
    /* ... другие цвета */
  }
}
```

Использование в компонентах:
```jsx
<div className="bg-background text-foreground">
  Автоматически адаптируется к теме
</div>
```

## 📦 Работа с Radix UI

### Аккордеон:
```jsx
import * as Accordion from '@radix-ui/react-accordion';

<Accordion.Root type="single" collapsible>
  <Accordion.Item value="item-1">
    <Accordion.Trigger className="btn btn-outline w-full">
      Заголовок
    </Accordion.Trigger>
    <Accordion.Content className="p-4">
      Содержимое
    </Accordion.Content>
  </Accordion.Item>
</Accordion.Root>
```

### Диалог:
```jsx
import * as Dialog from '@radix-ui/react-dialog';

<Dialog.Root>
  <Dialog.Trigger className="btn btn-primary">
    Открыть диалог
  </Dialog.Trigger>
  <Dialog.Portal>
    <Dialog.Overlay className="fixed inset-0 bg-black/50" />
    <Dialog.Content className="card fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
      <Dialog.Title className="card-title">Заголовок</Dialog.Title>
      <div className="card-content">
        Содержимое диалога
      </div>
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>
```

## 🚀 Лучшие практики

### 1. Используйте семантические классы:
```jsx
// ✅ Хорошо
<div className="bg-card text-card-foreground">

// ❌ Плохо
<div className="bg-white text-black">
```

### 2. Группируйте связанные стили:
```jsx
// ✅ Хорошо
<button className="
  btn btn-primary
  hover:scale-105 
  focus:ring-2 focus:ring-primary
  disabled:opacity-50
">

// ❌ Плохо
<button className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
```

### 3. Используйте компонентные классы для повторяющихся паттернов:
```css
.analysis-card {
  @apply bg-white rounded-lg shadow p-4 mb-4;
}
```

### 4. Применяйте container queries для адаптивности:
```jsx
<div className="@container">
  <div className="@lg:grid-cols-2">
    Адаптивный контент
  </div>
</div>
```

## 📊 Специфичные компоненты проекта

### График TradingView:
```jsx
<div className="bg-white rounded-lg shadow p-4">
  <TradingViewChart 
    data={data} 
    layers={layers} 
    analysis={analysis} 
  />
</div>
```

### Панель индикаторов:
```jsx
<div className="bg-white rounded-lg shadow p-4 mb-4">
  <h3 className="text-lg font-semibold mb-4">Индикаторы</h3>
  <div className="space-y-2">
    {indicators.map(indicator => (
      <label key={indicator} className="flex items-center">
        <input type="checkbox" className="mr-2" />
        <span className="text-sm">{indicator}</span>
      </label>
    ))}
  </div>
</div>
```

Проект уже полностью настроен и готов к работе с современными Frontend элементами!
