import axios from 'axios';
import { API_BASE_URL } from '../config/api';
import { tokenUtils } from './authService';

// Создаем axios instance с базовой конфигурацией
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Интерцептор запросов - добавляем JWT токен в заголовки
apiClient.interceptors.request.use(
  (config) => {
    const token = tokenUtils.getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Интерцептор ответов - обрабатываем ошибки
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response) {
      // Обработка различных статусов ошибок
      const { status, data } = error.response;
      
      // Если 401 (Unauthorized), удаляем токен
      if (status === 401) {
        tokenUtils.removeToken();
      }
      
      // Возвращаем структурированную ошибку
      return Promise.reject({
        status,
        message: data?.message || error.message || 'Произошла ошибка',
        data,
      });
    } else if (error.request) {
      // Запрос был отправлен, но ответ не получен
      return Promise.reject({
        status: 0,
        message: 'Сервер недоступен. Проверьте подключение к интернету.',
      });
    } else {
      // Ошибка при настройке запроса
      return Promise.reject({
        status: 0,
        message: error.message || 'Произошла ошибка',
      });
    }
  }
);

export default apiClient;

