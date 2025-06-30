// 📋 Task Monitor Component for ChartGenius Admin
// Версия: 1.1.0-dev
// Мониторинг фоновых задач

import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  CardHeader,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Button,
  IconButton,
  Tooltip,
  LinearProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Grid
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  PlayArrow as PlayArrowIcon,
  Stop as StopIcon,
  Visibility as VisibilityIcon,
  Delete as DeleteIcon,
  Schedule as ScheduleIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Pause as PauseIcon
} from '@mui/icons-material';

const TaskMonitor = () => {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedTask, setSelectedTask] = useState(null);
  const [taskDialog, setTaskDialog] = useState(false);

  // Заглушка данных задач
  const mockTasks = [
    {
      id: 'task_001',
      type: 'analysis',
      status: 'PROCESSING',
      progress: 65,
      symbol: 'BTCUSDT',
      user_id: '123456789',
      created_at: new Date(Date.now() - 300000).toISOString(),
      updated_at: new Date(Date.now() - 60000).toISOString(),
      current_step: 'llm_analysis',
      message: 'Генерация AI анализа...'
    },
    {
      id: 'task_002',
      type: 'analysis',
      status: 'SUCCESS',
      progress: 100,
      symbol: 'ETHUSDT',
      user_id: '987654321',
      created_at: new Date(Date.now() - 600000).toISOString(),
      updated_at: new Date(Date.now() - 120000).toISOString(),
      current_step: 'completed',
      message: 'Анализ завершен успешно'
    },
    {
      id: 'task_003',
      type: 'analysis',
      status: 'FAILURE',
      progress: 40,
      symbol: 'ADAUSDT',
      user_id: '456789123',
      created_at: new Date(Date.now() - 900000).toISOString(),
      updated_at: new Date(Date.now() - 300000).toISOString(),
      current_step: 'indicators',
      message: 'Ошибка получения рыночных данных',
      error: 'Network timeout'
    },
    {
      id: 'task_004',
      type: 'analysis',
      status: 'PENDING',
      progress: 0,
      symbol: 'DOTUSDT',
      user_id: '789123456',
      created_at: new Date(Date.now() - 30000).toISOString(),
      updated_at: new Date(Date.now() - 30000).toISOString(),
      current_step: 'queued',
      message: 'Ожидание в очереди'
    }
  ];

  useEffect(() => {
    // Имитация загрузки данных
    setTasks(mockTasks);
    
    // Автообновление каждые 5 секунд
    const interval = setInterval(() => {
      // Имитация обновления прогресса
      setTasks(prevTasks => 
        prevTasks.map(task => {
          if (task.status === 'PROCESSING' && task.progress < 100) {
            return {
              ...task,
              progress: Math.min(task.progress + Math.random() * 10, 100),
              updated_at: new Date().toISOString()
            };
          }
          return task;
        })
      );
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const getStatusIcon = (status) => {
    switch (status) {
      case 'SUCCESS':
        return <CheckCircleIcon color="success" />;
      case 'FAILURE':
        return <ErrorIcon color="error" />;
      case 'PROCESSING':
        return <PlayArrowIcon color="primary" />;
      case 'PENDING':
        return <ScheduleIcon color="warning" />;
      case 'REVOKED':
        return <StopIcon color="disabled" />;
      default:
        return <PauseIcon color="disabled" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'SUCCESS':
        return 'success';
      case 'FAILURE':
        return 'error';
      case 'PROCESSING':
        return 'primary';
      case 'PENDING':
        return 'warning';
      case 'REVOKED':
        return 'default';
      default:
        return 'default';
    }
  };

  const getStatusLabel = (status) => {
    switch (status) {
      case 'SUCCESS':
        return 'Завершено';
      case 'FAILURE':
        return 'Ошибка';
      case 'PROCESSING':
        return 'Выполняется';
      case 'PENDING':
        return 'Ожидание';
      case 'REVOKED':
        return 'Отменено';
      default:
        return status;
    }
  };

  const formatDuration = (startTime, endTime) => {
    const start = new Date(startTime);
    const end = endTime ? new Date(endTime) : new Date();
    const diffMs = end - start;
    const diffSecs = Math.floor(diffMs / 1000);
    const diffMins = Math.floor(diffSecs / 60);
    
    if (diffMins > 0) {
      return `${diffMins}м ${diffSecs % 60}с`;
    }
    return `${diffSecs}с`;
  };

  const handleViewTask = (task) => {
    setSelectedTask(task);
    setTaskDialog(true);
  };

  const handleCancelTask = async (taskId) => {
    if (!window.confirm('Отменить задачу?')) {
      return;
    }

    try {
      // Имитация отмены задачи
      setTasks(prevTasks =>
        prevTasks.map(task =>
          task.id === taskId
            ? { ...task, status: 'REVOKED', message: 'Задача отменена' }
            : task
        )
      );
    } catch (err) {
      setError(err.message);
    }
  };

  const getTaskStats = () => {
    const total = tasks.length;
    const processing = tasks.filter(t => t.status === 'PROCESSING').length;
    const pending = tasks.filter(t => t.status === 'PENDING').length;
    const completed = tasks.filter(t => t.status === 'SUCCESS').length;
    const failed = tasks.filter(t => t.status === 'FAILURE').length;

    return { total, processing, pending, completed, failed };
  };

  const stats = getTaskStats();

  return (
    <Box>
      {/* Заголовок */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5" component="h2">
          Мониторинг задач
        </Typography>
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={() => window.location.reload()}
        >
          Обновить
        </Button>
      </Box>

      {/* Статистика */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Всего задач
              </Typography>
              <Typography variant="h4">
                {stats.total}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Выполняется
              </Typography>
              <Typography variant="h4" color="primary">
                {stats.processing}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                В очереди
              </Typography>
              <Typography variant="h4" color="warning.main">
                {stats.pending}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Завершено
              </Typography>
              <Typography variant="h4" color="success.main">
                {stats.completed}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Ошибки
              </Typography>
              <Typography variant="h4" color="error.main">
                {stats.failed}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Информационное сообщение */}
      <Alert severity="info" sx={{ mb: 3 }}>
        <Typography variant="body2">
          Показаны тестовые данные задач. Автообновление каждые 5 секунд.
        </Typography>
      </Alert>

      {/* Таблица задач */}
      <Card>
        <CardHeader title="Активные задачи" />
        <CardContent>
          <TableContainer component={Paper} variant="outlined">
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>ID задачи</TableCell>
                  <TableCell>Тип</TableCell>
                  <TableCell>Статус</TableCell>
                  <TableCell>Прогресс</TableCell>
                  <TableCell>Символ</TableCell>
                  <TableCell>Пользователь</TableCell>
                  <TableCell>Длительность</TableCell>
                  <TableCell>Действия</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {tasks.map((task) => (
                  <TableRow key={task.id}>
                    <TableCell>
                      <Typography variant="body2" fontFamily="monospace">
                        {task.id}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={task.type}
                        size="small"
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>
                      <Box display="flex" alignItems="center" gap={1}>
                        {getStatusIcon(task.status)}
                        <Chip
                          label={getStatusLabel(task.status)}
                          color={getStatusColor(task.status)}
                          size="small"
                          variant="outlined"
                        />
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Box sx={{ minWidth: 100 }}>
                        <LinearProgress
                          variant="determinate"
                          value={task.progress}
                          sx={{ mb: 1 }}
                        />
                        <Typography variant="body2" color="textSecondary">
                          {task.progress}%
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" fontWeight="medium">
                        {task.symbol}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" fontFamily="monospace">
                        {task.user_id}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {formatDuration(task.created_at, task.updated_at)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Box display="flex" gap={1}>
                        <Tooltip title="Просмотреть детали">
                          <IconButton
                            size="small"
                            onClick={() => handleViewTask(task)}
                          >
                            <VisibilityIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                        
                        {(task.status === 'PROCESSING' || task.status === 'PENDING') && (
                          <Tooltip title="Отменить задачу">
                            <IconButton
                              size="small"
                              color="error"
                              onClick={() => handleCancelTask(task.id)}
                            >
                              <StopIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        )}
                      </Box>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>

          {tasks.length === 0 && (
            <Box textAlign="center" py={4}>
              <Typography variant="body1" color="textSecondary">
                Нет активных задач
              </Typography>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Диалог деталей задачи */}
      <Dialog
        open={taskDialog}
        onClose={() => setTaskDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Детали задачи: {selectedTask?.id}
        </DialogTitle>
        <DialogContent>
          {selectedTask && (
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" gutterBottom>
                  Статус
                </Typography>
                <Box display="flex" alignItems="center" gap={1} mb={2}>
                  {getStatusIcon(selectedTask.status)}
                  <Chip
                    label={getStatusLabel(selectedTask.status)}
                    color={getStatusColor(selectedTask.status)}
                    variant="outlined"
                  />
                </Box>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" gutterBottom>
                  Прогресс
                </Typography>
                <LinearProgress
                  variant="determinate"
                  value={selectedTask.progress}
                  sx={{ mb: 1 }}
                />
                <Typography variant="body2">
                  {selectedTask.progress}%
                </Typography>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" gutterBottom>
                  Символ
                </Typography>
                <Typography variant="body1">
                  {selectedTask.symbol}
                </Typography>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" gutterBottom>
                  Текущий шаг
                </Typography>
                <Typography variant="body1">
                  {selectedTask.current_step}
                </Typography>
              </Grid>
              
              <Grid item xs={12}>
                <Typography variant="subtitle2" gutterBottom>
                  Сообщение
                </Typography>
                <Typography variant="body1">
                  {selectedTask.message}
                </Typography>
              </Grid>
              
              {selectedTask.error && (
                <Grid item xs={12}>
                  <Typography variant="subtitle2" gutterBottom>
                    Ошибка
                  </Typography>
                  <Alert severity="error">
                    {selectedTask.error}
                  </Alert>
                </Grid>
              )}
              
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" gutterBottom>
                  Создано
                </Typography>
                <Typography variant="body2">
                  {new Date(selectedTask.created_at).toLocaleString()}
                </Typography>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" gutterBottom>
                  Обновлено
                </Typography>
                <Typography variant="body2">
                  {new Date(selectedTask.updated_at).toLocaleString()}
                </Typography>
              </Grid>
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setTaskDialog(false)}>
            Закрыть
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default TaskMonitor;
