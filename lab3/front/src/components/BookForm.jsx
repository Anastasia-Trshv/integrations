import { useState, useEffect } from 'react';
import './BookForm.css';

const BookForm = ({ book, onSubmit, onCancel }) => {
  const [formData, setFormData] = useState({
    title: '',
    isbn: '',
    genre: '',
    description: '',
    publicationYear: '',
    publisher: '',
    authors: [],
  });
  const [authorInput, setAuthorInput] = useState('');

  useEffect(() => {
    if (book) {
      setFormData({
        title: book.title || '',
        isbn: book.isbn || '',
        genre: book.genre || '',
        description: book.description || '',
        publicationYear: book.publicationYear || '',
        publisher: book.publisher || '',
        authors: book.authors || [],
      });
    }
  }, [book]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const handleAddAuthor = () => {
    if (authorInput.trim()) {
      setFormData({
        ...formData,
        authors: [...formData.authors, authorInput.trim()],
      });
      setAuthorInput('');
    }
  };

  const handleRemoveAuthor = (index) => {
    setFormData({
      ...formData,
      authors: formData.authors.filter((_, i) => i !== index),
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const data = {
      ...formData,
      publicationYear: formData.publicationYear ? parseInt(formData.publicationYear) : 0,
    };
    onSubmit(data);
  };

  return (
    <div className="form-overlay">
      <div className="form-modal book-form-modal">
        <h2>{book ? 'Редактировать книгу' : 'Создать книгу'}</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="title">Название *</label>
            <input
              type="text"
              id="title"
              name="title"
              value={formData.title}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="isbn">ISBN</label>
            <input
              type="text"
              id="isbn"
              name="isbn"
              value={formData.isbn}
              onChange={handleChange}
            />
          </div>
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="genre">Жанр</label>
              <input
                type="text"
                id="genre"
                name="genre"
                value={formData.genre}
                onChange={handleChange}
              />
            </div>
            <div className="form-group">
              <label htmlFor="publicationYear">Год публикации</label>
              <input
                type="number"
                id="publicationYear"
                name="publicationYear"
                value={formData.publicationYear}
                onChange={handleChange}
                min="0"
              />
            </div>
          </div>
          <div className="form-group">
            <label htmlFor="publisher">Издательство</label>
            <input
              type="text"
              id="publisher"
              name="publisher"
              value={formData.publisher}
              onChange={handleChange}
            />
          </div>
          <div className="form-group">
            <label htmlFor="description">Описание</label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleChange}
              rows="4"
            />
          </div>
          <div className="form-group">
            <label htmlFor="authors">Авторы</label>
            <div className="authors-input-group">
              <input
                type="text"
                id="authorInput"
                value={authorInput}
                onChange={(e) => setAuthorInput(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    handleAddAuthor();
                  }
                }}
                placeholder="Введите имя автора и нажмите Enter"
              />
              <button type="button" onClick={handleAddAuthor} className="add-button">
                Добавить
              </button>
            </div>
            {formData.authors.length > 0 && (
              <div className="authors-list">
                {formData.authors.map((author, index) => (
                  <div key={index} className="author-tag">
                    {author}
                    <button
                      type="button"
                      onClick={() => handleRemoveAuthor(index)}
                      className="remove-author"
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
          <div className="form-actions">
            <button type="submit" className="primary-button">
              {book ? 'Сохранить' : 'Создать'}
            </button>
            <button type="button" onClick={onCancel} className="secondary-button">
              Отмена
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default BookForm;

