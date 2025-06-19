import React, { useState } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Button,
  Box,
  Grid,
  Chip,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider
} from '@mui/material';
import {
  Speed as SpeedIcon,
  Analytics as AnalyticsIcon,
  TrendingUp as TrendingUpIcon,
  ShowChart as ShowChartIcon,
  Assessment as AssessmentIcon,
  Timeline as TimelineIcon
} from '@mui/icons-material';

export default function AnalysisSelector({ onAnalysisSelect, subscription }) {
  const [selectedType, setSelectedType] = useState(null);

  const analysisTypes = [
    {
      id: 'simple',
      title: 'Краткий анализ',
      subtitle: 'Быстрый обзор рынка',
      icon: <SpeedIcon />,
      color: 'primary',
      features: [
        'Основные технические индикаторы',
        'Текущий тренд',
        'Базовые рекомендации',
        'Время выполнения: ~30 сек'
      ],
      requiredSubscription: 'basic'
    },
    {
      id: 'full',
      title: 'Полный анализ',
      subtitle: 'Детальное исследование',
      icon: <AnalyticsIcon />,
      color: 'success',
      features: [
        'Все технические индикаторы',
        'Паттерны и формации',
        'Уровни поддержки/сопротивления',
        'Прогнозирование цен',
        'Детальные торговые рекомендации',
        'Интерактивные графики',
        'Время выполнения: ~2-3 мин'
      ],
      requiredSubscription: 'premium'
    }
  ];

  const handleSelect = (type) => {
    setSelectedType(type.id);
    onAnalysisSelect(type);
  };

  const canUseAnalysis = (requiredSub) => {
    if (!subscription) return false;
    
    const levels = { 'basic': 1, 'premium': 2 };
    const userLevel = levels[subscription.level] || 0;
    const requiredLevel = levels[requiredSub] || 0;
    
    return userLevel >= requiredLevel && subscription.is_active;
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h5" gutterBottom>
          📊 Выберите тип анализа
        </Typography>
        
        <Typography variant="body2" color="text.secondary" paragraph>
          Выберите подходящий тип анализа в зависимости от ваших потребностей
        </Typography>

        <Grid container spacing={3}>
          {analysisTypes.map((type) => {
            const canUse = canUseAnalysis(type.requiredSubscription);
            const isSelected = selectedType === type.id;
            
            return (
              <Grid item xs={12} md={6} key={type.id}>
                <Card 
                  variant={isSelected ? "elevation" : "outlined"}
                  sx={{ 
                    height: '100%',
                    cursor: canUse ? 'pointer' : 'not-allowed',
                    opacity: canUse ? 1 : 0.6,
                    border: isSelected ? 2 : 1,
                    borderColor: isSelected ? `${type.color}.main` : 'divider'
                  }}
                  onClick={() => canUse && handleSelect(type)}
                >
                  <CardContent>
                    <Box display="flex" alignItems="center" gap={1} mb={2}>
                      {type.icon}
                      <Typography variant="h6">
                        {type.title}
                      </Typography>
                      <Chip 
                        label={type.requiredSubscription === 'basic' ? 'Базовая' : 'Премиум'}
                        size="small"
                        color={type.color}
                        variant="outlined"
                      />
                    </Box>
                    
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      {type.subtitle}
                    </Typography>

                    <Divider sx={{ my: 2 }} />

                    <List dense>
                      {type.features.map((feature, index) => (
                        <ListItem key={index} sx={{ px: 0 }}>
                          <ListItemIcon sx={{ minWidth: 32 }}>
                            {index < 3 ? (
                              <TrendingUpIcon fontSize="small" color={type.color} />
                            ) : index < 5 ? (
                              <ShowChartIcon fontSize="small" color={type.color} />
                            ) : (
                              <TimelineIcon fontSize="small" color={type.color} />
                            )}
                          </ListItemIcon>
                          <ListItemText 
                            primary={feature}
                            primaryTypographyProps={{ variant: 'body2' }}
                          />
                        </ListItem>
                      ))}
                    </List>

                    {!canUse && (
                      <Box mt={2}>
                        <Chip 
                          label={`Требуется ${type.requiredSubscription === 'basic' ? 'базовая' : 'премиум'} подписка`}
                          color="warning"
                          size="small"
                          variant="outlined"
                        />
                      </Box>
                    )}

                    {canUse && (
                      <Box mt={2}>
                        <Button
                          variant={isSelected ? "contained" : "outlined"}
                          color={type.color}
                          fullWidth
                          startIcon={<AssessmentIcon />}
                          onClick={() => handleSelect(type)}
                        >
                          {isSelected ? 'Выбрано' : 'Выбрать'}
                        </Button>
                      </Box>
                    )}
                  </CardContent>
                </Card>
              </Grid>
            );
          })}
        </Grid>

        {!subscription?.is_active && (
          <Box mt={3}>
            <Card variant="outlined" sx={{ bgcolor: 'warning.light', color: 'warning.contrastText' }}>
              <CardContent>
                <Typography variant="body2" align="center">
                  ⚠️ Для использования анализа необходима активная подписка
                </Typography>
              </CardContent>
            </Card>
          </Box>
        )}
      </CardContent>
    </Card>
  );
}
