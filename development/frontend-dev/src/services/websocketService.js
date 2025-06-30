// 🔌 WebSocket Service for ChartGenius Frontend
// Версия: 1.1.0-dev
// Real-time уведомления и обновления

class WebSocketService {
  constructor() {
    this.ws = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectInterval = 1000; // 1 секунда
    this.listeners = new Map();
    this.isConnecting = false;
    this.userId = null;
    this.heartbeatInterval = null;
    
    console.log('WebSocket Service инициализирован');
  }

  /**
   * Подключение к WebSocket серверу
   * @param {string} userId - ID пользователя
   */
  connect(userId) {
    if (this.isConnecting || (this.ws && this.ws.readyState === WebSocket.OPEN)) {
      console.log('WebSocket уже подключен или подключается');
      return;
    }

    this.userId = userId;
    this.isConnecting = true;

    try {
      // Определяем URL WebSocket сервера
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const host = window.location.hostname;
      const port = process.env.NODE_ENV === 'development' ? ':8001' : '';
      const wsUrl = `${protocol}//${host}${port}/ws/${userId}`;

      console.log(`Подключение к WebSocket: ${wsUrl}`);
      
      this.ws = new WebSocket(wsUrl);
      
      this.ws.onopen = this.handleOpen.bind(this);
      this.ws.onmessage = this.handleMessage.bind(this);
      this.ws.onclose = this.handleClose.bind(this);
      this.ws.onerror = this.handleError.bind(this);

    } catch (error) {
      console.error('Ошибка создания WebSocket соединения:', error);
      this.isConnecting = false;
      this.scheduleReconnect();
    }
  }

  /**
   * Обработка открытия соединения
   */
  handleOpen(event) {
    console.log('WebSocket соединение установлено');
    this.isConnecting = false;
    this.reconnectAttempts = 0;
    
    // Запускаем heartbeat
    this.startHeartbeat();
    
    // Уведомляем слушателей о подключении
    this.notifyListeners('connection', {
      type: 'connected',
      timestamp: new Date().toISOString()
    });
  }

  /**
   * Обработка входящих сообщений
   */
  handleMessage(event) {
    try {
      const message = JSON.parse(event.data);
      console.log('WebSocket сообщение получено:', message);
      
      // Обрабатываем разные типы сообщений
      switch (message.type) {
        case 'connection_established':
          this.handleConnectionEstablished(message);
          break;
          
        case 'analysis_started':
          this.notifyListeners('analysis', message);
          break;
          
        case 'analysis_progress':
          this.notifyListeners('analysis', message);
          break;
          
        case 'analysis_completed':
          this.notifyListeners('analysis', message);
          this.showNotification('Анализ завершен', message.data?.message);
          break;
          
        case 'analysis_failed':
          this.notifyListeners('analysis', message);
          this.showNotification('Ошибка анализа', message.data?.message, 'error');
          break;
          
        case 'task_update':
          this.notifyListeners('task', message);
          break;
          
        case 'system_alert':
          this.notifyListeners('system', message);
          this.showNotification('Системное уведомление', message.data?.message, 'warning');
          break;
          
        case 'user_message':
          this.notifyListeners('user', message);
          break;
          
        case 'pong':
          // Ответ на ping - ничего не делаем
          break;
          
        default:
          console.log('Неизвестный тип сообщения:', message.type);
          this.notifyListeners('unknown', message);
      }
      
    } catch (error) {
      console.error('Ошибка обработки WebSocket сообщения:', error);
    }
  }

  /**
   * Обработка закрытия соединения
   */
  handleClose(event) {
    console.log('WebSocket соединение закрыто:', event.code, event.reason);
    this.isConnecting = false;
    this.stopHeartbeat();
    
    // Уведомляем слушателей о разрыве соединения
    this.notifyListeners('connection', {
      type: 'disconnected',
      code: event.code,
      reason: event.reason,
      timestamp: new Date().toISOString()
    });
    
    // Пытаемся переподключиться если соединение было закрыто не намеренно
    if (event.code !== 1000) { // 1000 = нормальное закрытие
      this.scheduleReconnect();
    }
  }

  /**
   * Обработка ошибок
   */
  handleError(event) {
    console.error('WebSocket ошибка:', event);
    this.notifyListeners('connection', {
      type: 'error',
      error: event,
      timestamp: new Date().toISOString()
    });
  }

  /**
   * Планирование переподключения
   */
  scheduleReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Превышено максимальное количество попыток переподключения');
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectInterval * Math.pow(2, this.reconnectAttempts - 1); // Exponential backoff
    
    console.log(`Переподключение через ${delay}ms (попытка ${this.reconnectAttempts})`);
    
    setTimeout(() => {
      if (this.userId) {
        this.connect(this.userId);
      }
    }, delay);
  }

  /**
   * Отправка сообщения
   */
  send(message) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      try {
        const messageStr = typeof message === 'string' ? message : JSON.stringify(message);
        this.ws.send(messageStr);
        console.log('WebSocket сообщение отправлено:', message);
      } catch (error) {
        console.error('Ошибка отправки WebSocket сообщения:', error);
      }
    } else {
      console.warn('WebSocket не подключен, сообщение не отправлено:', message);
    }
  }

  /**
   * Подписка на задачу
   */
  subscribeToTask(taskId) {
    this.send({
      type: 'subscribe_task',
      data: { task_id: taskId }
    });
  }

  /**
   * Отписка от задачи
   */
  unsubscribeFromTask(taskId) {
    this.send({
      type: 'unsubscribe_task',
      data: { task_id: taskId }
    });
  }

  /**
   * Запуск heartbeat
   */
  startHeartbeat() {
    this.heartbeatInterval = setInterval(() => {
      this.send({
        type: 'ping',
        data: { timestamp: new Date().toISOString() }
      });
    }, 30000); // Каждые 30 секунд
  }

  /**
   * Остановка heartbeat
   */
  stopHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  /**
   * Добавление слушателя событий
   */
  addEventListener(eventType, callback) {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, new Set());
    }
    this.listeners.get(eventType).add(callback);
    
    console.log(`Добавлен слушатель для события: ${eventType}`);
  }

  /**
   * Удаление слушателя событий
   */
  removeEventListener(eventType, callback) {
    if (this.listeners.has(eventType)) {
      this.listeners.get(eventType).delete(callback);
    }
  }

  /**
   * Уведомление слушателей
   */
  notifyListeners(eventType, data) {
    if (this.listeners.has(eventType)) {
      this.listeners.get(eventType).forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error(`Ошибка в слушателе события ${eventType}:`, error);
        }
      });
    }
  }

  /**
   * Обработка установления соединения
   */
  handleConnectionEstablished(message) {
    console.log('Соединение установлено:', message.data);
  }

  /**
   * Показ уведомления пользователю
   */
  showNotification(title, message, type = 'info') {
    // Проверяем поддержку браузером уведомлений
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification(title, {
        body: message,
        icon: '/favicon.ico',
        tag: 'chartgenius-notification'
      });
    }
    
    // Также можно отправить событие для показа уведомления в UI
    this.notifyListeners('notification', {
      title,
      message,
      type,
      timestamp: new Date().toISOString()
    });
  }

  /**
   * Запрос разрешения на уведомления
   */
  requestNotificationPermission() {
    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission().then(permission => {
        console.log('Разрешение на уведомления:', permission);
      });
    }
  }

  /**
   * Отключение от WebSocket
   */
  disconnect() {
    this.stopHeartbeat();
    
    if (this.ws) {
      this.ws.close(1000, 'Отключение по запросу пользователя');
      this.ws = null;
    }
    
    this.userId = null;
    this.reconnectAttempts = 0;
    this.isConnecting = false;
    
    console.log('WebSocket отключен');
  }

  /**
   * Получение статуса соединения
   */
  getConnectionStatus() {
    if (!this.ws) return 'disconnected';
    
    switch (this.ws.readyState) {
      case WebSocket.CONNECTING:
        return 'connecting';
      case WebSocket.OPEN:
        return 'connected';
      case WebSocket.CLOSING:
        return 'closing';
      case WebSocket.CLOSED:
        return 'disconnected';
      default:
        return 'unknown';
    }
  }

  /**
   * Проверка подключения
   */
  isConnected() {
    return this.ws && this.ws.readyState === WebSocket.OPEN;
  }
}

// Создаем глобальный экземпляр сервиса
const websocketService = new WebSocketService();

export default websocketService;
