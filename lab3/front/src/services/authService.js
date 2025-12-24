import apiClient from './apiClient';
import { generateIdempotencyKey } from '../config/api';

/**
 * Сервис для работы с авторизацией
 */
export const authService = {
  /**
   * Войти в систему
   * @param {string} login - Логин пользователя
   * @param {string} password - Пароль пользователя
   * @returns {Promise<string>} JWT токен
   */
  async login(login, password) {
    try {
      const response = await apiClient.post('/api/v2/Auth/login', {
        login,
        password,
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Зарегистрировать нового пользователя
   * @param {Object} userData - Данные пользователя
   * @param {string} userData.username - Имя пользователя
   * @param {string} userData.login - Логин
   * @param {string} userData.passwordHash - Пароль (будет использован как hash)
   * @param {string} idempotencyKey - Ключ идемпотентности (опционально)
   * @returns {Promise<Object>}
   */
  async register(userData, idempotencyKey = null) {
    try {
      const key = idempotencyKey || generateIdempotencyKey();
      const response = await apiClient.post(
        '/api/v2/Users/CreateUser',
        {
          username: userData.username,
          login: userData.login,
          passwordHash: userData.passwordHash, // В v2 используется passwordHash напрямую
        },
        {
          headers: {
            'Idempotency-Key': key,
          },
        }
      );
      return response.data;
    } catch (error) {
      throw error;
    }
  },
};

/**
 * Утилиты для работы с токеном
 */
export const tokenUtils = {
  /**
   * Сохранить токен в localStorage
   * @param {string} token - JWT токен
   */
  saveToken(token) {
    localStorage.setItem('jwt_token', token);
  },

  /**
   * Получить токен из localStorage
   * @returns {string|null}
   */
  getToken() {
    return localStorage.getItem('jwt_token');
  },

  /**
   * Удалить токен из localStorage
   */
  removeToken() {
    localStorage.removeItem('jwt_token');
  },

  /**
   * Проверить, есть ли токен
   * @returns {boolean}
   */
  hasToken() {
    return !!this.getToken();
  },
};

