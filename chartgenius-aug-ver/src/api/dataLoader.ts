// D:/project/chartgenius-aug-ver/src/api/dataLoader.ts

// Используем специальный импорт Vite для загрузки файлов как есть (raw)
import promptDataRaw from '../../sample_data/prompt_1749228821.txt?raw';
import responseDataRaw from '../../sample_data/chatgpt_response_1749229059.json?raw';

// Определяем базовые типы для большей предсказуемости
// В будущем их можно детализировать для полной типобезопасности
type CandleData = any;
type AiResponseData = any;

// Функция для безопасного парсинга JSON с обработкой ошибок
function safeJsonParse(jsonString: string, fileName: string): any {
  try {
    // Удаляем возможные BOM и лишние пробелы
    let cleanedString = jsonString.replace(/^\uFEFF/, '').trim();

    // Для файла prompt_1749228821.txt - извлекаем только JSON массив
    if (fileName.includes('prompt_1749228821.txt')) {
      // Находим начало JSON массива
      const jsonStart = cleanedString.indexOf('[');
      if (jsonStart !== -1) {
        // Находим конец JSON массива, ищем последнюю закрывающую скобку перед текстом
        let bracketCount = 0;
        let jsonEnd = -1;

        for (let i = jsonStart; i < cleanedString.length; i++) {
          if (cleanedString[i] === '[') bracketCount++;
          if (cleanedString[i] === ']') {
            bracketCount--;
            if (bracketCount === 0) {
              jsonEnd = i + 1;
              break;
            }
          }
        }

        if (jsonEnd !== -1) {
          cleanedString = cleanedString.substring(jsonStart, jsonEnd);
        }
      }
    }

    return JSON.parse(cleanedString);
  } catch (error) {
    console.error(`Ошибка парсинга JSON в файле ${fileName}:`, error);
    console.error(`Проблемная строка (первые 200 символов):`, jsonString.substring(0, 200));
    throw new Error(`Не удалось загрузить данные из ${fileName}: ${error}`);
  }
}

// Парсим текстовые данные в объекты JavaScript с обработкой ошибок
const candleData: CandleData = safeJsonParse(promptDataRaw, 'prompt_1749228821.txt');
const aiResponseData: AiResponseData = safeJsonParse(responseDataRaw, 'chatgpt_response_1749229059.json');

// Экспортируем готовые данные для использования в приложении
export { candleData, aiResponseData };
