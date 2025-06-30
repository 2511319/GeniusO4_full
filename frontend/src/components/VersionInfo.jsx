import React, { useState } from 'react';
import { 
  Box, Typography, Chip, Dialog, DialogTitle, 
  DialogContent, List, ListItem, ListItemText,
  IconButton, Divider
} from '@mui/material';
import InfoIcon from '@mui/icons-material/Info';
import { APP_VERSION, DEBUG, BUILD_INFO } from '../config';

export default function VersionInfo() {
  const [open, setOpen] = useState(false);
  const [apiStatus, setApiStatus] = useState(null);

  const checkApiStatus = async () => {
    try {
      const response = await fetch('/api/health');
      if (response.ok) {
        const data = await response.json();
        setApiStatus(data);
      } else {
        setApiStatus({ error: 'API недоступен' });
      }
    } catch (error) {
      setApiStatus({ error: error.message });
    }
  };

  const handleOpen = () => {
    setOpen(true);
    checkApiStatus();
  };

  return (
    <>
      {/* Компактная версия в углу */}
      <Box sx={{ 
        position: 'fixed', 
        bottom: 8, 
        right: 8, 
        zIndex: 1000,
        display: 'flex',
        gap: 1,
        alignItems: 'center'
      }}>
        <IconButton 
          size="small" 
          onClick={handleOpen}
          sx={{ 
            bgcolor: 'background.paper',
            boxShadow: 1,
            '&:hover': { boxShadow: 2 }
          }}
        >
          <InfoIcon fontSize="small" />
        </IconButton>
        
        <Chip 
          label={`v${APP_VERSION}`} 
          size="small" 
          color="primary" 
          variant="outlined"
          sx={{ bgcolor: 'background.paper' }}
        />
        
        {DEBUG && (
          <Chip 
            label="DEV" 
            size="small" 
            color="warning" 
            variant="filled"
          />
        )}
      </Box>

      {/* Детальная информация в диалоге */}
      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          Информация о системе ChartGenius
        </DialogTitle>
        <DialogContent>
          <List dense>
            <ListItem>
              <ListItemText 
                primary="Версия Frontend" 
                secondary={APP_VERSION}
              />
              <Chip label="Активна" color="success" size="small" />
            </ListItem>
            
            <ListItem>
              <ListItemText 
                primary="Режим" 
                secondary={DEBUG ? 'Development' : 'Production'}
              />
              <Chip 
                label={DEBUG ? 'DEV' : 'PROD'} 
                color={DEBUG ? 'warning' : 'success'} 
                size="small" 
              />
            </ListItem>

            <Divider sx={{ my: 1 }} />

            <ListItem>
              <ListItemText 
                primary="API Статус" 
                secondary={
                  apiStatus === null ? 'Проверка...' :
                  apiStatus.error ? `Ошибка: ${apiStatus.error}` :
                  `${apiStatus.status} (v${apiStatus.version || 'неизвестно'})`
                }
              />
              <Chip 
                label={
                  apiStatus === null ? 'Проверка' :
                  apiStatus.error ? 'Ошибка' :
                  apiStatus.status === 'healthy' ? 'OK' : 'Проблема'
                }
                color={
                  apiStatus === null ? 'default' :
                  apiStatus.error ? 'error' :
                  apiStatus.status === 'healthy' ? 'success' : 'warning'
                }
                size="small" 
              />
            </ListItem>

            {apiStatus && apiStatus.environment && (
              <ListItem>
                <ListItemText 
                  primary="API Окружение" 
                  secondary={apiStatus.environment}
                />
              </ListItem>
            )}

            {apiStatus && apiStatus.region && (
              <ListItem>
                <ListItemText 
                  primary="Регион" 
                  secondary={apiStatus.region}
                />
              </ListItem>
            )}

            <Divider sx={{ my: 1 }} />

            <ListItem>
              <ListItemText 
                primary="Время сборки" 
                secondary={BUILD_INFO.buildTime}
              />
            </ListItem>

            <ListItem>
              <ListItemText 
                primary="API Режим" 
                secondary={BUILD_INFO.apiMode}
              />
            </ListItem>
          </List>

          <Typography variant="caption" color="text.secondary" sx={{ mt: 2, display: 'block' }}>
            Для отладки проблем с развертыванием используйте эту информацию
          </Typography>
        </DialogContent>
      </Dialog>
    </>
  );
}
