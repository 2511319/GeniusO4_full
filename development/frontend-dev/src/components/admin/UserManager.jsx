// 👥 User Manager Component for ChartGenius Admin
// Версия: 1.1.0-dev
// Управление пользователями

import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Alert,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  Tooltip,
  TextField,
  InputAdornment
} from '@mui/material';
import {
  Search as SearchIcon,
  Refresh as RefreshIcon,
  Person as PersonIcon,
  AdminPanelSettings as AdminIcon,
  Star as StarIcon,
  Diamond as DiamondIcon
} from '@mui/icons-material';

const UserManager = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');

  // Заглушка данных пользователей
  const mockUsers = [
    {
      id: '299820674',
      username: 'admin',
      role: 'admin',
      subscription: 'admin',
      lastActive: new Date().toISOString(),
      totalAnalyses: 150,
      joinDate: '2024-01-01'
    },
    {
      id: '123456789',
      username: 'test_user',
      role: 'premiumuser',
      subscription: 'premium',
      lastActive: new Date(Date.now() - 3600000).toISOString(),
      totalAnalyses: 45,
      joinDate: '2024-06-01'
    },
    {
      id: '987654321',
      username: 'vip_trader',
      role: 'vipuser',
      subscription: 'vip',
      lastActive: new Date(Date.now() - 7200000).toISOString(),
      totalAnalyses: 89,
      joinDate: '2024-03-15'
    }
  ];

  useEffect(() => {
    // Имитация загрузки данных
    setTimeout(() => {
      setUsers(mockUsers);
      setLoading(false);
    }, 1000);
  }, []);

  const getRoleIcon = (role) => {
    switch (role) {
      case 'admin':
        return <AdminIcon color="error" />;
      case 'vipuser':
        return <DiamondIcon color="primary" />;
      case 'premiumuser':
        return <StarIcon color="warning" />;
      default:
        return <PersonIcon color="disabled" />;
    }
  };

  const getRoleColor = (role) => {
    switch (role) {
      case 'admin':
        return 'error';
      case 'vipuser':
        return 'primary';
      case 'premiumuser':
        return 'warning';
      default:
        return 'default';
    }
  };

  const getRoleLabel = (role) => {
    switch (role) {
      case 'admin':
        return 'Администратор';
      case 'vipuser':
        return 'VIP пользователь';
      case 'premiumuser':
        return 'Премиум пользователь';
      default:
        return 'Пользователь';
    }
  };

  const filteredUsers = users.filter(user =>
    user.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.id.includes(searchTerm)
  );

  const formatLastActive = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 60) {
      return `${diffMins} мин назад`;
    } else if (diffHours < 24) {
      return `${diffHours} ч назад`;
    } else {
      return `${diffDays} дн назад`;
    }
  };

  return (
    <Box>
      {/* Заголовок */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5" component="h2">
          Управление пользователями
        </Typography>
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={() => window.location.reload()}
        >
          Обновить
        </Button>
      </Box>

      {/* Информационное сообщение */}
      <Alert severity="info" sx={{ mb: 3 }}>
        <Typography variant="body2">
          Управление пользователями находится в разработке. 
          Показаны тестовые данные для демонстрации интерфейса.
        </Typography>
      </Alert>

      {/* Поиск */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <TextField
            fullWidth
            placeholder="Поиск по имени пользователя или ID..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
          />
        </CardContent>
      </Card>

      {/* Статистика */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Статистика пользователей
          </Typography>
          <Box display="flex" gap={4} flexWrap="wrap">
            <Box>
              <Typography variant="h4" color="primary">
                {users.length}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Всего пользователей
              </Typography>
            </Box>
            <Box>
              <Typography variant="h4" color="success.main">
                {users.filter(u => u.role === 'admin').length}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Администраторов
              </Typography>
            </Box>
            <Box>
              <Typography variant="h4" color="warning.main">
                {users.filter(u => u.role === 'premiumuser').length}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Премиум пользователей
              </Typography>
            </Box>
            <Box>
              <Typography variant="h4" color="primary.main">
                {users.filter(u => u.role === 'vipuser').length}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                VIP пользователей
              </Typography>
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* Таблица пользователей */}
      <Card>
        <CardContent>
          <TableContainer component={Paper} variant="outlined">
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Пользователь</TableCell>
                  <TableCell>Роль</TableCell>
                  <TableCell>Подписка</TableCell>
                  <TableCell>Последняя активность</TableCell>
                  <TableCell>Анализов</TableCell>
                  <TableCell>Дата регистрации</TableCell>
                  <TableCell>Действия</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredUsers.map((user) => (
                  <TableRow key={user.id}>
                    <TableCell>
                      <Box display="flex" alignItems="center" gap={1}>
                        {getRoleIcon(user.role)}
                        <Box>
                          <Typography variant="body2" fontWeight="medium">
                            {user.username}
                          </Typography>
                          <Typography variant="caption" color="textSecondary">
                            ID: {user.id}
                          </Typography>
                        </Box>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={getRoleLabel(user.role)}
                        color={getRoleColor(user.role)}
                        size="small"
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={user.subscription}
                        color={user.subscription === 'admin' ? 'error' : 'primary'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {formatLastActive(user.lastActive)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {user.totalAnalyses}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" color="textSecondary">
                        {new Date(user.joinDate).toLocaleDateString()}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Tooltip title="Функции управления в разработке">
                        <span>
                          <IconButton size="small" disabled>
                            <AdminIcon fontSize="small" />
                          </IconButton>
                        </span>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>

          {filteredUsers.length === 0 && (
            <Box textAlign="center" py={4}>
              <Typography variant="body1" color="textSecondary">
                Пользователи не найдены
              </Typography>
            </Box>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export default UserManager;
