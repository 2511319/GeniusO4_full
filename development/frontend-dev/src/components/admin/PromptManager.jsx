// 📝 Prompt Manager Component for ChartGenius Admin
// Версия: 1.1.0-dev
// Управление промптами для LLM

import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  CardHeader,
  Typography,
  Button,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
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
  Alert,
  Snackbar,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as VisibilityIcon,
  CloudUpload as CloudUploadIcon,
  CheckCircle as CheckCircleIcon,
  RadioButtonUnchecked as RadioButtonUncheckedIcon,
  ExpandMore as ExpandMoreIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';

const PROMPT_TYPES = [
  { value: 'technical_analysis', label: 'Технический анализ' },
  { value: 'fundamental_analysis', label: 'Фундаментальный анализ' },
  { value: 'sentiment_analysis', label: 'Анализ настроений' },
  { value: 'risk_assessment', label: 'Оценка рисков' }
];

const PromptManager = () => {
  const [prompts, setPrompts] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  
  // Диалоги
  const [uploadDialog, setUploadDialog] = useState(false);
  const [viewDialog, setViewDialog] = useState(false);
  const [selectedPrompt, setSelectedPrompt] = useState(null);
  
  // Форма загрузки
  const [uploadForm, setUploadForm] = useState({
    prompt_type: '',
    version: '',
    prompt_text: '',
    description: '',
    parameters: {
      temperature: 0.7,
      max_tokens: 4000
    }
  });

  const fetchPrompts = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch('/api/llm/prompts');
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      if (data.success) {
        setPrompts(data.prompts);
      } else {
        throw new Error('Failed to fetch prompts');
      }

    } catch (err) {
      console.error('Error fetching prompts:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPrompts();
  }, []);

  const handleUploadPrompt = async () => {
    try {
      setError(null);

      const response = await fetch('/api/llm/prompt/upload', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(uploadForm),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      if (data.success) {
        setSuccess('Промпт успешно загружен');
        setUploadDialog(false);
        setUploadForm({
          prompt_type: '',
          version: '',
          prompt_text: '',
          description: '',
          parameters: {
            temperature: 0.7,
            max_tokens: 4000
          }
        });
        await fetchPrompts();
      } else {
        throw new Error(data.message || 'Failed to upload prompt');
      }

    } catch (err) {
      console.error('Error uploading prompt:', err);
      setError(err.message);
    }
  };

  const handleActivateVersion = async (promptType, version) => {
    try {
      setError(null);

      const response = await fetch(`/api/llm/prompts/${promptType}/activate/${version}`, {
        method: 'PUT',
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      if (data.success) {
        setSuccess(`Версия ${version} активирована для ${promptType}`);
        await fetchPrompts();
      } else {
        throw new Error(data.message || 'Failed to activate version');
      }

    } catch (err) {
      console.error('Error activating version:', err);
      setError(err.message);
    }
  };

  const handleDeleteVersion = async (promptType, version) => {
    if (!window.confirm(`Удалить версию ${version} промпта ${promptType}?`)) {
      return;
    }

    try {
      setError(null);

      const response = await fetch(`/api/llm/prompts/${promptType}/versions/${version}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      if (data.success) {
        setSuccess(`Версия ${version} удалена`);
        await fetchPrompts();
      } else {
        throw new Error(data.message || 'Failed to delete version');
      }

    } catch (err) {
      console.error('Error deleting version:', err);
      setError(err.message);
    }
  };

  const handleViewPrompt = async (promptType, version) => {
    try {
      const response = await fetch(`/api/llm/prompts/${promptType}/versions/${version}`);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      if (data.success) {
        setSelectedPrompt({
          type: promptType,
          version: version,
          content: data.content
        });
        setViewDialog(true);
      }

    } catch (err) {
      console.error('Error viewing prompt:', err);
      setError(err.message);
    }
  };

  const renderPromptCard = (promptType, promptData) => {
    const typeLabel = PROMPT_TYPES.find(t => t.value === promptType)?.label || promptType;
    const versions = promptData.versions || {};
    const activeVersion = promptData.active_version;

    return (
      <Card key={promptType}>
        <CardHeader
          title={typeLabel}
          subheader={`Активная версия: ${activeVersion || 'Не установлена'}`}
          action={
            <Chip
              label={Object.keys(versions).length + ' версий'}
              color="primary"
              variant="outlined"
            />
          }
        />
        <CardContent>
          {Object.keys(versions).length === 0 ? (
            <Typography color="textSecondary">
              Нет загруженных версий
            </Typography>
          ) : (
            <TableContainer component={Paper} variant="outlined">
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Версия</TableCell>
                    <TableCell>Описание</TableCell>
                    <TableCell>Создано</TableCell>
                    <TableCell>Автор</TableCell>
                    <TableCell>Действия</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {Object.entries(versions).map(([version, versionData]) => (
                    <TableRow key={version}>
                      <TableCell>
                        <Box display="flex" alignItems="center" gap={1}>
                          {activeVersion === version ? (
                            <CheckCircleIcon color="success" fontSize="small" />
                          ) : (
                            <RadioButtonUncheckedIcon color="disabled" fontSize="small" />
                          )}
                          <Typography variant="body2" fontWeight="medium">
                            {version}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {versionData.description || 'Без описания'}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" color="textSecondary">
                          {new Date(versionData.created_at).toLocaleDateString()}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {versionData.created_by}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Box display="flex" gap={1}>
                          <Tooltip title="Просмотреть">
                            <IconButton
                              size="small"
                              onClick={() => handleViewPrompt(promptType, version)}
                            >
                              <VisibilityIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          
                          {activeVersion !== version && (
                            <Tooltip title="Активировать">
                              <IconButton
                                size="small"
                                onClick={() => handleActivateVersion(promptType, version)}
                              >
                                <CheckCircleIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
                          )}
                          
                          {activeVersion !== version && (
                            <Tooltip title="Удалить">
                              <IconButton
                                size="small"
                                color="error"
                                onClick={() => handleDeleteVersion(promptType, version)}
                              >
                                <DeleteIcon fontSize="small" />
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
          )}
        </CardContent>
      </Card>
    );
  };

  return (
    <Box>
      {/* Заголовок */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5" component="h2">
          Управление промптами
        </Typography>
        <Box display="flex" gap={2}>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={fetchPrompts}
            disabled={loading}
          >
            Обновить
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setUploadDialog(true)}
          >
            Загрузить промпт
          </Button>
        </Box>
      </Box>

      {/* Список промптов */}
      <Grid container spacing={3}>
        {PROMPT_TYPES.map(({ value, label }) => (
          <Grid item xs={12} key={value}>
            {renderPromptCard(value, prompts[value] || {})}
          </Grid>
        ))}
      </Grid>

      {/* Диалог загрузки промпта */}
      <Dialog
        open={uploadDialog}
        onClose={() => setUploadDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Загрузить новый промпт</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Тип промпта</InputLabel>
                <Select
                  value={uploadForm.prompt_type}
                  onChange={(e) => setUploadForm(prev => ({ ...prev, prompt_type: e.target.value }))}
                >
                  {PROMPT_TYPES.map(type => (
                    <MenuItem key={type.value} value={type.value}>
                      {type.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Версия"
                value={uploadForm.version}
                onChange={(e) => setUploadForm(prev => ({ ...prev, version: e.target.value }))}
                placeholder="1.0"
              />
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Описание"
                value={uploadForm.description}
                onChange={(e) => setUploadForm(prev => ({ ...prev, description: e.target.value }))}
                placeholder="Краткое описание промпта"
              />
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={10}
                label="Текст промпта"
                value={uploadForm.prompt_text}
                onChange={(e) => setUploadForm(prev => ({ ...prev, prompt_text: e.target.value }))}
                placeholder="Введите текст промпта..."
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setUploadDialog(false)}>
            Отмена
          </Button>
          <Button
            onClick={handleUploadPrompt}
            variant="contained"
            startIcon={<CloudUploadIcon />}
            disabled={!uploadForm.prompt_type || !uploadForm.version || !uploadForm.prompt_text}
          >
            Загрузить
          </Button>
        </DialogActions>
      </Dialog>

      {/* Диалог просмотра промпта */}
      <Dialog
        open={viewDialog}
        onClose={() => setViewDialog(false)}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>
          Просмотр промпта: {selectedPrompt?.type} v{selectedPrompt?.version}
        </DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            multiline
            rows={15}
            value={selectedPrompt?.content || ''}
            InputProps={{
              readOnly: true,
            }}
            sx={{ mt: 1 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setViewDialog(false)}>
            Закрыть
          </Button>
        </DialogActions>
      </Dialog>

      {/* Уведомления */}
      <Snackbar
        open={!!error}
        autoHideDuration={6000}
        onClose={() => setError(null)}
      >
        <Alert severity="error" onClose={() => setError(null)}>
          {error}
        </Alert>
      </Snackbar>

      <Snackbar
        open={!!success}
        autoHideDuration={4000}
        onClose={() => setSuccess(null)}
      >
        <Alert severity="success" onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default PromptManager;
