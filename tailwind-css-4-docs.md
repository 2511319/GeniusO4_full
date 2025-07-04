# Tailwind CSS 4.0+ Документация

## Основные изменения в Tailwind CSS 4.0

### 1. Новая архитектура установки

#### Для Vite проектов:
```bash
npm install tailwindcss @tailwindcss/vite
```

**vite.config.js:**
```javascript
import { defineConfig } from 'vite'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [
    tailwindcss(),
  ],
})
```

**CSS файл:**
```css
@import "tailwindcss";
```

#### Для Next.js проектов:
```bash
npm install tailwindcss @tailwindcss/postcss postcss
```

**postcss.config.mjs:**
```javascript
const config = {
  plugins: {
    "@tailwindcss/postcss": {},
  },
};
export default config;
```

**globals.css:**
```css
@import "tailwindcss";
```

### 2. CSS-first конфигурация

Вместо `tailwind.config.js` используется CSS конфигурация:

```css
@import "tailwindcss";

@theme {
  --font-display: "Satoshi", "sans-serif";
  --breakpoint-3xl: 1920px;
  --color-avocado-100: oklch(0.99 0 0);
  --color-avocado-200: oklch(0.98 0.04 113.22);
  --color-avocado-300: oklch(0.94 0.11 115.03);
  --color-avocado-400: oklch(0.92 0.19 114.08);
  --color-avocado-500: oklch(0.84 0.18 117.33);
  --color-avocado-600: oklch(0.53 0.12 118.34);
  --ease-fluid: cubic-bezier(0.3, 0, 0, 1);
  --ease-snappy: cubic-bezier(0.2, 0, 0, 1);
}
```

### 3. Автоматическое обнаружение контента

- Не нужно настраивать `content` массив
- Автоматически игнорирует файлы из `.gitignore`
- Автоматически исключает бинарные файлы

Для добавления дополнительных источников:
```css
@import "tailwindcss";
@source "../node_modules/@my-company/ui-lib";
```

### 4. Встроенная поддержка импортов

Не нужен `postcss-import` - встроенная поддержка `@import`.

### 5. CSS переменные темы

Все токены дизайна доступны как CSS переменные:

```css
:root {
  --font-display: "Satoshi", "sans-serif";
  --breakpoint-3xl: 1920px;
  --color-avocado-100: oklch(0.99 0 0);
  /* ... */
}
```

### 6. Динамические утилиты

```html
<!-- Сетки любого размера -->
<div class="grid grid-cols-15">

<!-- Кастомные data атрибуты -->
<div data-current class="opacity-75 data-current:opacity-100">

<!-- Динамические значения spacing -->
<div class="mt-8 w-17 pr-29">
```

### 7. Модернизированная P3 цветовая палитра

Переход с `rgb` на `oklch` для более ярких цветов.

### 8. Container Queries (встроенные)

```html
<div class="@container">
  <div class="grid grid-cols-1 @sm:grid-cols-3 @lg:grid-cols-4">
    <!-- ... -->
  </div>
</div>

<!-- Max-width container queries -->
<div class="@container">
  <div class="grid grid-cols-3 @max-md:grid-cols-1">
    <!-- ... -->
  </div>
</div>

<!-- Диапазоны -->
<div class="@container">
  <div class="flex @min-md:@max-xl:hidden">
    <!-- ... -->
  </div>
</div>
```

### 9. 3D трансформации

```html
<div class="perspective-distant">
  <article class="rotate-x-51 rotate-z-43 transform-3d">
    <!-- ... -->
  </article>
</div>
```

### 10. Расширенные градиенты

```html
<!-- Углы для линейных градиентов -->
<div class="bg-linear-45 from-indigo-500 via-purple-500 to-pink-500"></div>

<!-- Интерполяция цветов -->
<div class="bg-linear-to-r/srgb from-indigo-500 to-teal-400"></div>
<div class="bg-linear-to-r/oklch from-indigo-500 to-teal-400"></div>

<!-- Конические и радиальные градиенты -->
<div class="bg-conic/[in_hsl_longer_hue] from-red-600 to-red-600"></div>
<div class="bg-radial-[at_25%_25%] from-white to-zinc-900 to-75%"></div>
```

### 11. @starting-style поддержка

```html
<div>
  <button popovertarget="my-popover">Check for updates</button>
  <div popover id="my-popover" class="transition-discrete starting:open:opacity-0">
    <!-- ... -->
  </div>
</div>
```

### 12. not-* вариант

```html
<!-- Отрицание псевдо-классов -->
<div class="not-hover:opacity-75">

<!-- Отрицание media queries -->
<div class="not-supports-hanging-punctuation:px-4">
```

### 13. Новые утилиты

- `inset-shadow-*` и `inset-ring-*` - многослойные тени
- `field-sizing` - авто-ресайз textarea
- `color-scheme` - схемы цветов для темного режима
- `font-stretch` - растяжение шрифтов
- `inert` вариант - для неинтерактивных элементов
- `nth-*` варианты - nth-child селекторы
- `in-*` вариант - как group-* но без класса group
- `:popover-open` поддержка
- descendant вариант - стилизация всех потомков

## Производительность

- Полные сборки: до 5x быстрее
- Инкрементальные сборки: до 100x быстрее (в микросекундах)
- Оптимизация для современного CSS

## Совместимость

- Требует современные браузеры с поддержкой CSS cascade layers
- Поддержка color-mix(), @property, логических свойств
- Автоматические vendor prefixes через Lightning CSS
