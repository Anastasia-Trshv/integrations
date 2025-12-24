// API базовый URL - можно вынести в переменные окружения
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5042';

// Генерация Idempotency-Key для идемпотентных операций
export const generateIdempotencyKey = () => {
  return `${Date.now()}-${Math.random().toString(36).substring(2, 15)}`;
};

