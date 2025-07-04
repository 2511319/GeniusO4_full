import React, { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Badge } from '../components/ui/badge';
import { Alert, AlertDescription } from '../components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { 
  Users, 
  Settings, 
  MessageSquare, 
  Database, 
  Activity,
  Shield,
  Edit,
  Trash2,
  Plus,
  Send,
  RefreshCw
} from 'lucide-react';
import { clearAuth } from '../store';

export default function AdminPanel() {
  const { token } = useSelector((state) => state.auth);
  const dispatch = useDispatch();
  const navigate = useNavigate();
  
  // States
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // Stats
  const [stats, setStats] = useState({
    total_users: 0,
    roles: { admin: 0, moderator: 0, vip: 0, premium: 0, user: 0 },
    active_subscriptions: { premium: 0, vip: 0 }
  });
  
  // Users management
  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [newRole, setNewRole] = useState('');
  const [subscriptionDays, setSubscriptionDays] = useState(0);
  
  // Broadcast
  const [broadcastMessage, setBroadcastMessage] = useState('');
  
  // Prompts management
  const [prompts, setPrompts] = useState([]);
  const [selectedPrompt, setSelectedPrompt] = useState(null);
  const [promptText, setPromptText] = useState('');
  const [promptVariant, setPromptVariant] = useState('');
  
  // LLM Config
  const [llmConfig, setLlmConfig] = useState({
    openai_model: 'gpt-4',
    gemini_model: 'gemini-2.5-pro',
    default_provider: 'openai'
  });

  useEffect(() => {
    // Check admin access - TEMPORARILY DISABLED FOR TESTING
    // if (!token) {
    //   navigate('/');
    //   return;
    // }

    // try {
    //   const payload = JSON.parse(atob(token.split('.')[1]));
    //   if (payload.role !== 'admin') {
    //     navigate('/');
    //     return;
    //   }
    // } catch (err) {
    //   navigate('/');
    //   return;
    // }

    loadInitialData();
  }, [token, navigate]);

  const loadInitialData = async () => {
    await Promise.all([
      loadStats(),
      loadUsers(),
      loadPrompts(),
      loadLlmConfig()
    ]);
  };

  const loadStats = async () => {
    try {
      const response = await fetch('/api/admin/stats', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (err) {
      console.error('Error loading stats:', err);
    }
  };

  const loadUsers = async () => {
    try {
      const response = await fetch('/api/admin/users', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setUsers(data.users || []);
      }
    } catch (err) {
      console.error('Error loading users:', err);
    }
  };

  const loadPrompts = async () => {
    try {
      const response = await fetch('/api/admin/prompts', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setPrompts(data.prompts || []);
      }
    } catch (err) {
      console.error('Error loading prompts:', err);
    }
  };

  const loadLlmConfig = async () => {
    try {
      const response = await fetch('/api/admin/llm-config', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setLlmConfig(data);
      }
    } catch (err) {
      console.error('Error loading LLM config:', err);
    }
  };

  const handleSetRole = async () => {
    if (!selectedUser || !newRole) return;
    
    setLoading(true);
    try {
      const response = await fetch('/api/admin/set_role', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          telegram_id: selectedUser.telegram_id,
          role: newRole,
          subscription_days: subscriptionDays
        })
      });
      
      if (response.ok) {
        setSuccess('Роль успешно обновлена');
        await loadUsers();
        await loadStats();
        setSelectedUser(null);
        setNewRole('');
        setSubscriptionDays(0);
      } else {
        const error = await response.json();
        setError(error.detail || 'Ошибка обновления роли');
      }
    } catch (err) {
      setError('Ошибка сети');
    } finally {
      setLoading(false);
    }
  };

  const handleBroadcast = async () => {
    if (!broadcastMessage.trim()) return;
    
    setLoading(true);
    try {
      const response = await fetch('/api/admin/broadcast', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ text: broadcastMessage })
      });
      
      if (response.ok) {
        setSuccess('Рассылка запланирована');
        setBroadcastMessage('');
      } else {
        const error = await response.json();
        setError(error.detail || 'Ошибка создания рассылки');
      }
    } catch (err) {
      setError('Ошибка сети');
    } finally {
      setLoading(false);
    }
  };

  const handleGarbageCollect = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/admin/gc', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setSuccess(`Очистка завершена: анализы=${data.deleted.analyses}, флаги=${data.deleted.flags}, баны=${data.deleted.bans}`);
      } else {
        const error = await response.json();
        setError(error.detail || 'Ошибка очистки');
      }
    } catch (err) {
      setError('Ошибка сети');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    dispatch(clearAuth());
    navigate('/');
  };

  const getRoleColor = (role) => {
    const colors = {
      'admin': 'destructive',
      'moderator': 'secondary', 
      'vip': 'outline',
      'premium': 'default',
      'user': 'secondary'
    };
    return colors[role] || 'secondary';
  };

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
            <Shield className="h-8 w-8 text-red-600" />
            Admin Panel
          </h1>
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => navigate('/')}>
              К анализу
            </Button>
            <Button variant="outline" onClick={handleLogout}>
              Выйти
            </Button>
          </div>
        </div>

        {/* Alerts */}
        {error && (
          <Alert className="mb-4 border-red-200 bg-red-50">
            <AlertDescription className="text-red-800">{error}</AlertDescription>
          </Alert>
        )}
        
        {success && (
          <Alert className="mb-4 border-green-200 bg-green-50">
            <AlertDescription className="text-green-800">{success}</AlertDescription>
          </Alert>
        )}

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Всего пользователей</p>
                  <p className="text-2xl font-bold">{stats.total_users}</p>
                </div>
                <Users className="h-8 w-8 text-blue-600" />
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Premium подписки</p>
                  <p className="text-2xl font-bold">{stats.active_subscriptions.premium}</p>
                </div>
                <Activity className="h-8 w-8 text-green-600" />
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">VIP подписки</p>
                  <p className="text-2xl font-bold">{stats.active_subscriptions.vip}</p>
                </div>
                <Activity className="h-8 w-8 text-purple-600" />
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Администраторы</p>
                  <p className="text-2xl font-bold">{stats.roles.admin}</p>
                </div>
                <Shield className="h-8 w-8 text-red-600" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Main Tabs */}
        <Tabs defaultValue="users" className="space-y-4">
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="users">Пользователи</TabsTrigger>
            <TabsTrigger value="prompts">Промпты</TabsTrigger>
            <TabsTrigger value="llm">LLM настройки</TabsTrigger>
            <TabsTrigger value="broadcast">Рассылка</TabsTrigger>
            <TabsTrigger value="system">Система</TabsTrigger>
          </TabsList>

          {/* Prompts Tab */}
          <TabsContent value="prompts" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Edit className="h-5 w-5" />
                  Управление промптами
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label>Тип промпта</Label>
                      <Select value={promptVariant} onValueChange={setPromptVariant}>
                        <SelectTrigger>
                          <SelectValue placeholder="Выберите тип" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="technical_analysis">Технический анализ</SelectItem>
                          <SelectItem value="price_prediction">Прогноз цены</SelectItem>
                          <SelectItem value="volume_analysis">Анализ объемов</SelectItem>
                          <SelectItem value="indicators">Индикаторы</SelectItem>
                          <SelectItem value="recommendations">Рекомендации</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  <div>
                    <Label>Текст промпта</Label>
                    <Textarea
                      placeholder="Введите текст промпта..."
                      value={promptText}
                      onChange={(e) => setPromptText(e.target.value)}
                      rows={6}
                    />
                  </div>

                  <div className="flex gap-2">
                    <Button
                      onClick={() => {/* handleSavePrompt */}}
                      disabled={loading || !promptVariant || !promptText.trim()}
                    >
                      <Plus className="h-4 w-4 mr-2" />
                      Сохранить промпт
                    </Button>
                    <Button
                      variant="outline"
                      onClick={() => {setPromptText(''); setPromptVariant('');}}
                    >
                      Очистить
                    </Button>
                  </div>

                  {/* Existing prompts list */}
                  <div className="border-t pt-4">
                    <h3 className="font-semibold mb-2">Существующие промпты</h3>
                    <div className="space-y-2">
                      {prompts.map((prompt, index) => (
                        <div key={index} className="flex items-center justify-between p-2 border rounded">
                          <div>
                            <Badge variant="outline">{prompt.variant}</Badge>
                            <span className="ml-2 text-sm">{prompt.text.substring(0, 100)}...</span>
                          </div>
                          <Button size="sm" variant="outline">
                            <Edit className="h-4 w-4" />
                          </Button>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* LLM Config Tab */}
          <TabsContent value="llm" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Settings className="h-5 w-5" />
                  Настройки LLM провайдеров
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label>OpenAI модель</Label>
                      <Select value={llmConfig.openai_model} onValueChange={(value) =>
                        setLlmConfig(prev => ({...prev, openai_model: value}))
                      }>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="gpt-4">GPT-4</SelectItem>
                          <SelectItem value="gpt-4-turbo">GPT-4 Turbo</SelectItem>
                          <SelectItem value="gpt-3.5-turbo">GPT-3.5 Turbo</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div>
                      <Label>Gemini модель</Label>
                      <Select value={llmConfig.gemini_model} onValueChange={(value) =>
                        setLlmConfig(prev => ({...prev, gemini_model: value}))
                      }>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="gemini-2.5-pro">Gemini 2.5 Pro</SelectItem>
                          <SelectItem value="gemini-1.5-pro">Gemini 1.5 Pro</SelectItem>
                          <SelectItem value="gemini-1.0-pro">Gemini 1.0 Pro</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  <div>
                    <Label>Провайдер по умолчанию</Label>
                    <Select value={llmConfig.default_provider} onValueChange={(value) =>
                      setLlmConfig(prev => ({...prev, default_provider: value}))
                    }>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="openai">OpenAI</SelectItem>
                        <SelectItem value="gemini">Google Gemini</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <Button
                    onClick={() => {/* handleSaveLlmConfig */}}
                    disabled={loading}
                  >
                    {loading ? <RefreshCw className="h-4 w-4 animate-spin mr-2" /> : null}
                    Сохранить настройки
                  </Button>

                  <div className="border-t pt-4">
                    <h3 className="font-semibold mb-2">Тест провайдеров</h3>
                    <div className="flex gap-2">
                      <Button variant="outline" size="sm">
                        Тест OpenAI
                      </Button>
                      <Button variant="outline" size="sm">
                        Тест Gemini
                      </Button>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Users Tab */}
          <TabsContent value="users" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Users className="h-5 w-5" />
                  Управление пользователями
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {/* User Role Management */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <Label>Telegram ID пользователя</Label>
                      <Input 
                        placeholder="299820674"
                        value={selectedUser?.telegram_id || ''}
                        onChange={(e) => setSelectedUser({telegram_id: e.target.value})}
                      />
                    </div>
                    <div>
                      <Label>Новая роль</Label>
                      <Select value={newRole} onValueChange={setNewRole}>
                        <SelectTrigger>
                          <SelectValue placeholder="Выберите роль" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="user">Пользователь</SelectItem>
                          <SelectItem value="premium">Premium</SelectItem>
                          <SelectItem value="vip">VIP</SelectItem>
                          <SelectItem value="moderator">Модератор</SelectItem>
                          <SelectItem value="admin">Администратор</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label>Дни подписки (опционально)</Label>
                      <Input 
                        type="number"
                        placeholder="30"
                        value={subscriptionDays}
                        onChange={(e) => setSubscriptionDays(parseInt(e.target.value) || 0)}
                      />
                    </div>
                  </div>
                  
                  <Button 
                    onClick={handleSetRole}
                    disabled={loading || !selectedUser?.telegram_id || !newRole}
                    className="w-full md:w-auto"
                  >
                    {loading ? <RefreshCw className="h-4 w-4 animate-spin mr-2" /> : null}
                    Установить роль
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Broadcast Tab */}
          <TabsContent value="broadcast" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <MessageSquare className="h-5 w-5" />
                  Рассылка сообщений
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <Label>Текст сообщения</Label>
                    <Textarea 
                      placeholder="Введите текст для рассылки всем пользователям..."
                      value={broadcastMessage}
                      onChange={(e) => setBroadcastMessage(e.target.value)}
                      rows={4}
                    />
                  </div>
                  
                  <Button 
                    onClick={handleBroadcast}
                    disabled={loading || !broadcastMessage.trim()}
                    className="w-full md:w-auto"
                  >
                    {loading ? <RefreshCw className="h-4 w-4 animate-spin mr-2" /> : <Send className="h-4 w-4 mr-2" />}
                    Отправить рассылку
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* System Tab */}
          <TabsContent value="system" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Database className="h-5 w-5" />
                  Системные операции
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="p-4 border rounded-lg">
                    <h3 className="font-semibold mb-2">Очистка базы данных</h3>
                    <p className="text-sm text-gray-600 mb-4">
                      Удаляет старые анализы (&gt;30 дней), флаги (&gt;14 дней) и истекшие баны
                    </p>
                    <Button 
                      onClick={handleGarbageCollect}
                      disabled={loading}
                      variant="outline"
                    >
                      {loading ? <RefreshCw className="h-4 w-4 animate-spin mr-2" /> : <Trash2 className="h-4 w-4 mr-2" />}
                      Запустить очистку
                    </Button>
                  </div>
                  
                  <div className="p-4 border rounded-lg">
                    <h3 className="font-semibold mb-2">Обновить статистику</h3>
                    <p className="text-sm text-gray-600 mb-4">
                      Перезагружает статистику пользователей и подписок
                    </p>
                    <Button 
                      onClick={loadStats}
                      disabled={loading}
                      variant="outline"
                    >
                      {loading ? <RefreshCw className="h-4 w-4 animate-spin mr-2" /> : <RefreshCw className="h-4 w-4 mr-2" />}
                      Обновить
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
