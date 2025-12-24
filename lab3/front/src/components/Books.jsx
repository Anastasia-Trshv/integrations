import { useState, useEffect } from 'react';
import { booksService } from '../services/booksService';
import { tokenUtils } from '../services/authService';
import { useNavigate } from 'react-router-dom';
import BookForm from './BookForm';
import './Books.css';

const Books = () => {
  const navigate = useNavigate();
  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [editingBook, setEditingBook] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [idempotencyKey, setIdempotencyKey] = useState(null);
  const [pagination, setPagination] = useState({
    page: 1,
    pageSize: 10,
    totalCount: 0,
    totalPages: 0,
  });

  useEffect(() => {
    loadBooks(pagination.page, pagination.pageSize);
  }, [pagination.page, pagination.pageSize]);

  const loadBooks = async (page = 1, pageSize = 10) => {
    setLoading(true);
    setError('');
    try {
      const data = await booksService.getAllBooks(page, pageSize);
      setBooks(data.items || []);
      setPagination({
        page: data.page || page,
        pageSize: data.pageSize || pageSize,
        totalCount: data.totalCount || 0,
        totalPages: data.totalPages || 0,
      });
    } catch (err) {
      setError(err.message || 'Ошибка при загрузке книг');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (bookData) => {
    try {
      setError('');
      await booksService.createBook(bookData, idempotencyKey);
      setShowForm(false);
      setEditingBook(null);
      setIdempotencyKey(null);
      loadBooks(pagination.page, pagination.pageSize);
    } catch (err) {
      setError(err.message || 'Ошибка при создании книги');
    }
  };

  const handleUpdate = async (id, bookData) => {
    try {
      setError('');
      await booksService.updateBook(id, bookData);
      setShowForm(false);
      setEditingBook(null);
      loadBooks(pagination.page, pagination.pageSize);
    } catch (err) {
      setError(err.message || 'Ошибка при обновлении книги');
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Вы уверены, что хотите удалить эту книгу?')) {
      return;
    }
    try {
      setError('');
      await booksService.deleteBook(id);
      // Если удалили последний элемент на странице и страница не первая, переходим на предыдущую
      if (books.length === 1 && pagination.page > 1) {
        setPagination(prev => ({ ...prev, page: prev.page - 1 }));
      } else {
        loadBooks(pagination.page, pagination.pageSize);
      }
    } catch (err) {
      setError(err.message || 'Ошибка при удалении книги');
    }
  };

  const handlePageChange = (newPage) => {
    if (newPage >= 1 && newPage <= pagination.totalPages) {
      setPagination(prev => ({ ...prev, page: newPage }));
    }
  };

  const handlePageSizeChange = (e) => {
    const newPageSize = parseInt(e.target.value);
    setPagination(prev => ({ ...prev, pageSize: newPageSize, page: 1 }));
  };

  const handleEdit = (book) => {
    setEditingBook(book);
    setShowForm(true);
  };

  const handleNewBook = () => {
    setEditingBook(null);
    setIdempotencyKey(null);
    setShowForm(true);
  };

  return (
    <div className="books-container">
      <header className="header">
        <h1>Книги</h1>
        <div className="header-actions">
          <button onClick={() => navigate('/authors')} className="nav-button">
            Авторы
          </button>
          <button
            onClick={() => {
              tokenUtils.removeToken();
              navigate('/login');
            }}
            className="logout-button"
          >
            Выйти
          </button>
        </div>
      </header>

      {error && <div className="error-message">{error}</div>}

      <div className="actions-bar">
        <button onClick={handleNewBook} className="primary-button">
          + Добавить книгу
        </button>
        <button onClick={() => loadBooks(pagination.page, pagination.pageSize)} className="secondary-button" disabled={loading}>
          {loading ? 'Загрузка...' : 'Обновить'}
        </button>
        <div className="pagination-controls">
          <label htmlFor="pageSize">Размер страницы:</label>
          <select
            id="pageSize"
            value={pagination.pageSize}
            onChange={handlePageSizeChange}
            className="page-size-select"
          >
            <option value="5">5</option>
            <option value="10">10</option>
            <option value="20">20</option>
            <option value="50">50</option>
          </select>
        </div>
        {!idempotencyKey && (
          <button
            onClick={() => {
              setIdempotencyKey('test-key-' + Date.now());
            }}
            className="info-button"
            title="Включить идемпотентность для следующего создания"
          >
            Включить идемпотентность
          </button>
        )}
        {idempotencyKey && (
          <div className="idempotency-info">
            Идемпотентность активна: {idempotencyKey.substring(0, 20)}...
          </div>
        )}
      </div>

      {showForm && (
        <BookForm
          book={editingBook}
          onSubmit={editingBook ? (data) => handleUpdate(editingBook.id, data) : handleCreate}
          onCancel={() => {
            setShowForm(false);
            setEditingBook(null);
            setIdempotencyKey(null);
          }}
        />
      )}

      {loading && !books.length ? (
        <div className="loading">Загрузка книг...</div>
      ) : (
        <div className="books-grid">
          {books.map((book) => (
            <div key={book.id} className="book-card">
              <h3>{book.title}</h3>
              <div className="book-info">
                {book.isbn && <p><strong>ISBN:</strong> {book.isbn}</p>}
                {book.genre && <p><strong>Жанр:</strong> {book.genre}</p>}
                {book.publicationYear && <p><strong>Год:</strong> {book.publicationYear}</p>}
                {book.publisher && <p><strong>Издательство:</strong> {book.publisher}</p>}
                {book.authors && book.authors.length > 0 && (
                  <p><strong>Авторы:</strong> {book.authors.join(', ')}</p>
                )}
                {book.description && (
                  <p className="description">{book.description}</p>
                )}
              </div>
              <div className="card-actions">
                <button onClick={() => handleEdit(book)} className="edit-button">
                  Редактировать
                </button>
                <button onClick={() => handleDelete(book.id)} className="delete-button">
                  Удалить
                </button>
              </div>
            </div>
          ))}
          {books.length === 0 && !loading && (
            <div className="empty-state">Книги не найдены</div>
          )}
        </div>
      )}

      {pagination.totalPages > 1 && (
        <div className="pagination">
          <button
            onClick={() => handlePageChange(pagination.page - 1)}
            disabled={pagination.page === 1 || loading}
            className="pagination-button"
          >
            Назад
          </button>
          <span className="pagination-info">
            Страница {pagination.page} из {pagination.totalPages} 
            {pagination.totalCount > 0 && (
              <span className="total-count"> (Всего: {pagination.totalCount})</span>
            )}
          </span>
          <button
            onClick={() => handlePageChange(pagination.page + 1)}
            disabled={pagination.page === pagination.totalPages || loading}
            className="pagination-button"
          >
            Вперед
          </button>
        </div>
      )}
    </div>
  );
};

export default Books;

