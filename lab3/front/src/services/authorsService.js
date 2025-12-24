import apiClient from './apiClient';
import { generateIdempotencyKey } from '../config/api';

/**
 * Сервис для работы с авторами (v2 API)
 */
export const authorsService = {
  /**
   * Получить всех авторов с пагинацией
   * @param {number} page - Номер страницы (по умолчанию 1)
   * @param {number} pageSize - Размер страницы (по умолчанию 10)
   * @param {string} include - Поля для включения через запятую (опционально)
   * @returns {Promise<Object>} Объект с полями: items, page, pageSize, totalCount, totalPages
   */
  async getAllAuthors(page = 1, pageSize = 10, include = null) {
    try {
      const params = { page, pageSize };
      if (include) {
        params.include = include;
      }
      const response = await apiClient.get('/api/v2/Authors', { params });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Получить автора по ID
   * @param {number} id - ID автора
   * @param {string} include - Поля для включения через запятую (опционально)
   * @returns {Promise<Object>}
   */
  async getAuthorById(id, include = null) {
    try {
      const params = include ? { include } : {};
      const response = await apiClient.get(`/api/v2/Authors/${id}`, { params });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Создать автора (идемпотентная операция)
   * @param {Object} authorData - Данные автора
   * @param {string} idempotencyKey - Ключ идемпотентности (опционально)
   * @returns {Promise<Object>}
   */
  async createAuthor(authorData, idempotencyKey = null) {
    try {
      const key = idempotencyKey || generateIdempotencyKey();
      const response = await apiClient.post(
        '/api/v2/Authors',
        authorData,
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

  /**
   * Обновить автора по ID
   * @param {number} id - ID автора
   * @param {Object} authorData - Новые данные автора
   * @returns {Promise<Object>}
   */
  async updateAuthor(id, authorData) {
    try {
      const response = await apiClient.put(
        `/api/v2/Authors/${id}`,
        authorData
      );
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Удалить автора по ID
   * @param {number} id - ID автора
   * @returns {Promise<void>}
   */
  async deleteAuthor(id) {
    try {
      await apiClient.delete(`/api/v2/Authors/${id}`);
    } catch (error) {
      throw error;
    }
  },
};

