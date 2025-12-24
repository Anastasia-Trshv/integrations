import { useState, useEffect } from 'react';
import { authService, tokenUtils } from '../services/authService';
import { useNavigate } from 'react-router-dom';
import './Login.css';

const Login = () => {
  const navigate = useNavigate();
  
  useEffect(() => {
    // Если пользователь уже залогинен, перенаправляем на главную
    if (tokenUtils.hasToken()) {
      navigate('/books');
    }
  }, [navigate]);
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    username: '',
    login: '',
    password: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
    setError('');
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const token = await authService.login(formData.login, formData.password);
      tokenUtils.saveToken(token);
      navigate('/books');
    } catch (err) {
      setError(err.message || 'Ошибка при входе. Проверьте логин и пароль.');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    if (!formData.username || !formData.login || !formData.password) {
      setError('Все поля обязательны для заполнения');
      setLoading(false);
      return;
    }

    try {
      await authService.register({
        username: formData.username,
        login: formData.login,
        passwordHash: formData.password, // В v2 используется passwordHash напрямую
      });
      
      // После регистрации автоматически логинимся
      const token = await authService.login(formData.login, formData.password);
      tokenUtils.saveToken(token);
      navigate('/books');
    } catch (err) {
      setError(err.message || 'Ошибка при регистрации. Возможно, такой логин уже существует.');
    } finally {
      setLoading(false);
    }
  };

  const switchMode = () => {
    setIsLogin(!isLogin);
    setError('');
    setFormData({
      username: '',
      login: '',
      password: '',
    });
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <h1>{isLogin ? 'Вход' : 'Регистрация'}</h1>
        
        {error && <div className="error-message">{error}</div>}

        <form onSubmit={isLogin ? handleLogin : handleRegister}>
          {!isLogin && (
            <div className="form-group">
              <label htmlFor="username">Имя пользователя *</label>
              <input
                type="text"
                id="username"
                name="username"
                value={formData.username}
                onChange={handleChange}
                required={!isLogin}
                placeholder="Введите ваше имя"
              />
            </div>
          )}

          <div className="form-group">
            <label htmlFor="login">Логин *</label>
            <input
              type="text"
              id="login"
              name="login"
              value={formData.login}
              onChange={handleChange}
              required
              placeholder="Введите логин"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Пароль *</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
              placeholder="Введите пароль"
            />
          </div>

          <button
            type="submit"
            className="primary-button login-button"
            disabled={loading}
          >
            {loading ? 'Загрузка...' : isLogin ? 'Войти' : 'Зарегистрироваться'}
          </button>
        </form>

        <div className="switch-mode">
          <span>
            {isLogin ? 'Нет аккаунта? ' : 'Уже есть аккаунт? '}
          </span>
          <button
            type="button"
            onClick={switchMode}
            className="link-button"
          >
            {isLogin ? 'Зарегистрироваться' : 'Войти'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Login;

