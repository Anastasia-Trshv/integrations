import { useState, useEffect } from 'react';
import { authorsService } from '../services/authorsService';
import { tokenUtils } from '../services/authService';
import { useNavigate } from 'react-router-dom';
import AuthorForm from './AuthorForm';
import './Authors.css';

const Authors = () => {
  const navigate = useNavigate();
  const [authors, setAuthors] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [editingAuthor, setEditingAuthor] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [idempotencyKey, setIdempotencyKey] = useState(null);
  const [pagination, setPagination] = useState({
    page: 1,
    pageSize: 10,
    totalCount: 0,
    totalPages: 0,
  });

  useEffect(() => {
    loadAuthors(pagination.page, pagination.pageSize);
  }, [pagination.page, pagination.pageSize]);

  const loadAuthors = async (page = 1, pageSize = 10) => {
    setLoading(true);
    setError('');
    try {
      const data = await authorsService.getAllAuthors(page, pageSize);
      setAuthors(data.items || []);
      setPagination({
        page: data.page || page,
        pageSize: data.pageSize || pageSize,
        totalCount: data.totalCount || 0,
        totalPages: data.totalPages || 0,
      });
    } catch (err) {
      setError(err.message || 'Ошибка при загрузке авторов');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (authorData) => {
    try {
      setError('');
      await authorsService.createAuthor(authorData, idempotencyKey);
      setShowForm(false);
      setEditingAuthor(null);
      setIdempotencyKey(null);
      loadAuthors(pagination.page, pagination.pageSize);
    } catch (err) {
      setError(err.message || 'Ошибка при создании автора');
    }
  };

  const handleUpdate = async (id, authorData) => {
    try {
      setError('');
      await authorsService.updateAuthor(id, authorData);
      setShowForm(false);
      setEditingAuthor(null);
      loadAuthors(pagination.page, pagination.pageSize);
    } catch (err) {
      setError(err.message || 'Ошибка при обновлении автора');
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Вы уверены, что хотите удалить этого автора?')) {
      return;
    }
    try {
      setError('');
      await authorsService.deleteAuthor(id);
      // Если удалили последний элемент на странице и страница не первая, переходим на предыдущую
      if (authors.length === 1 && pagination.page > 1) {
        setPagination(prev => ({ ...prev, page: prev.page - 1 }));
      } else {
        loadAuthors(pagination.page, pagination.pageSize);
      }
    } catch (err) {
      setError(err.message || 'Ошибка при удалении автора');
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

  const handleEdit = (author) => {
    setEditingAuthor(author);
    setShowForm(true);
  };

  const handleNewAuthor = () => {
    setEditingAuthor(null);
    setIdempotencyKey(null);
    setShowForm(true);
  };

  return (
    <div className="authors-container">
      <header className="header">
        <h1>Авторы</h1>
        <div className="header-actions">
          <button onClick={() => navigate('/books')} className="nav-button">
            Книги
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
        <button onClick={handleNewAuthor} className="primary-button">
          + Добавить автора
        </button>
        <button onClick={() => loadAuthors(pagination.page, pagination.pageSize)} className="secondary-button" disabled={loading}>
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
        <AuthorForm
          author={editingAuthor}
          onSubmit={editingAuthor ? (data) => handleUpdate(editingAuthor.id, data) : handleCreate}
          onCancel={() => {
            setShowForm(false);
            setEditingAuthor(null);
            setIdempotencyKey(null);
          }}
        />
      )}

      {loading && !authors.length ? (
        <div className="loading">Загрузка авторов...</div>
      ) : (
        <div className="authors-grid">
          {authors.map((author) => (
            <div key={author.id} className="author-card">
              <h3>{[author.surname, author.name, author.patronymic].filter(Boolean).join(' ')}</h3>
              {author.bio && <p className="bio">{author.bio}</p>}
              <div className="card-actions">
                <button onClick={() => handleEdit(author)} className="edit-button">
                  Редактировать
                </button>
                <button onClick={() => handleDelete(author.id)} className="delete-button">
                  Удалить
                </button>
              </div>
            </div>
          ))}
          {authors.length === 0 && !loading && (
            <div className="empty-state">Авторы не найдены</div>
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

export default Authors;

