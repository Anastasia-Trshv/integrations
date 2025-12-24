import { useState, useEffect } from 'react';
import './AuthorForm.css';

const AuthorForm = ({ author, onSubmit, onCancel }) => {
  const [formData, setFormData] = useState({
    name: '',
    surname: '',
    patronymic: '',
    bio: '',
  });

  useEffect(() => {
    if (author) {
      setFormData({
        name: author.name || '',
        surname: author.surname || '',
        patronymic: author.patronymic || '',
        bio: author.bio || '',
      });
    }
  }, [author]);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <div className="form-overlay">
      <div className="form-modal">
        <h2>{author ? 'Редактировать автора' : 'Создать автора'}</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="surname">Фамилия *</label>
            <input
              type="text"
              id="surname"
              name="surname"
              value={formData.surname}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="name">Имя *</label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="patronymic">Отчество</label>
            <input
              type="text"
              id="patronymic"
              name="patronymic"
              value={formData.patronymic}
              onChange={handleChange}
            />
          </div>
          <div className="form-group">
            <label htmlFor="bio">Биография</label>
            <textarea
              id="bio"
              name="bio"
              value={formData.bio}
              onChange={handleChange}
              rows="4"
            />
          </div>
          <div className="form-actions">
            <button type="submit" className="primary-button">
              {author ? 'Сохранить' : 'Создать'}
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

export default AuthorForm;

