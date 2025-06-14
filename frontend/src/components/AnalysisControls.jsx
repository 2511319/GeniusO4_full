// src/components/AnalysisControls.jsx
import React, { useState } from 'react';
import PropTypes from 'prop-types';
import {
  Box,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import Spinner from './Spinner';

export default function AnalysisControls({
  symbol,
  setSymbol,
  interval,
  setInterval,
  limit,
  setLimit,
  onAnalyze,
  onLoadTest,
}) {
  const [loading, setLoading] = useState(false);

  const handleAnalyze = async () => {
    setLoading(true);
    try {
      await onAnalyze({ symbol, interval, limit });
    } finally {
      setLoading(false);
    }
  };
  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, p: 2, bgcolor: '#fafafa' }}>
      <FormControl size="small">
        <InputLabel>Symbol</InputLabel>
        <Select
          label="Symbol"
          value={symbol}
          onChange={e => setSymbol(e.target.value)}
        >
          <MenuItem value="BTCUSDT">BTCUSDT</MenuItem>
          <MenuItem value="ETHUSDT">ETHUSDT</MenuItem>
          <MenuItem value="BNBUSDT">BNBUSDT</MenuItem>
          {/* Добавьте свои символы */}
        </Select>
      </FormControl>

      <FormControl size="small">
        <InputLabel>Interval</InputLabel>
        <Select
          label="Interval"
          value={interval}
          onChange={e => setInterval(e.target.value)}
        >
          <MenuItem value="1m">1m</MenuItem>
          <MenuItem value="5m">5m</MenuItem>
          <MenuItem value="1h">1h</MenuItem>
          <MenuItem value="4h">4h</MenuItem>
          <MenuItem value="1d">1d</MenuItem>
        </Select>
      </FormControl>

      <TextField
        size="small"
        label="Limit"
        type="number"
        value={limit}
        onChange={e => setLimit(Number(e.target.value))}
        sx={{ width: 80 }}
      />

      <Button
        variant="contained"
        onClick={handleAnalyze}
        disabled={loading}
      >
        {loading ? (
          <Box
            sx={{
              width: 24,
              height: 24,
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <Spinner size={16} />
          </Box>
        ) : (
          'Analyze'
        )}
      </Button>

      {import.meta.env.DEV && (
        <Button
          variant="outlined"
          onClick={onLoadTest}
        >
          Load Test
        </Button>
      )}
    </Box>
  );
}

AnalysisControls.propTypes = {
  symbol:     PropTypes.string.isRequired,
  setSymbol:  PropTypes.func.isRequired,
  interval:   PropTypes.string.isRequired,
  setInterval:PropTypes.func.isRequired,
  limit:      PropTypes.number.isRequired,
  setLimit:   PropTypes.func.isRequired,
  onAnalyze:  PropTypes.func.isRequired,
  onLoadTest: PropTypes.func.isRequired,
};
