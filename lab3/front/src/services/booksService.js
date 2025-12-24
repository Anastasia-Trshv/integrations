import apiClient from './apiClient';
import { generateIdempotencyKey } from '../config/api';

/**
 * Сервис для работы с книгами (v2 API)
 */
export const booksService = {
  /**
   * Получить все книги с пагинацией
   * @param {number} page - Номер страницы (по умолчанию 1)
   * @param {number} pageSize - Размер страницы (по умолчанию 10)
   * @param {string} include - Поля для включения через запятую (опционально)
   * @returns {Promise<Object>} Объект с полями: items, page, pageSize, totalCount, totalPages
   */
  async getAllBooks(page = 1, pageSize = 10, include = null) {
    try {
      const params = { page, pageSize };
      if (include) {
        params.include = include;
      }
      const response = await apiClient.get('/api/v2/Books', { params });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Получить книгу по ID
   * @param {number} id - ID книги
   * @param {string} include - Поля для включения через запятую (опционально)
   * @returns {Promise<Object>}
   */
  async getBookById(id, include = null) {
    try {
      const params = include ? { include } : {};
      const response = await apiClient.get(`/api/v2/Books/${id}`, { params });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Создать книгу (идемпотентная операция)
   * @param {Object} bookData - Данные книги
   * @param {string} idempotencyKey - Ключ идемпотентности (опционально)
   * @returns {Promise<Object>}
   */
  async createBook(bookData, idempotencyKey = null) {
    try {
      const key = idempotencyKey || generateIdempotencyKey();
      const response = await apiClient.post(
        '/api/v2/Books',
        bookData,
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
   * Обновить книгу по ID
   * @param {number} id - ID книги
   * @param {Object} bookData - Новые данные книги
   * @returns {Promise<Object>}
   */
  async updateBook(id, bookData) {
    try {
      const response = await apiClient.put(
        `/api/v2/Books/${id}`,
        bookData
      );
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Удалить книгу по ID
   * @param {number} id - ID книги
   * @returns {Promise<void>}
   */
  async deleteBook(id) {
    try {
      await apiClient.delete(`/api/v2/Books/${id}`);
    } catch (error) {
      throw error;
    }
  },
};

