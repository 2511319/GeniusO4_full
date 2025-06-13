import React from 'react';
import PropTypes from 'prop-types';
import { ToggleButtonGroup, ToggleButton, Box, IconButton } from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import CommentIcon from '@mui/icons-material/Comment';

export default function ChartControls({ type, onChange, setSidebarOpen, setCommentsOpen }) {
  return (
    <Box sx={{ px: 1, py: 0.5, display: 'flex', alignItems: 'center', gap: 1 }}>
      <IconButton onClick={() => setSidebarOpen(o => !o)} size="small">
        <MenuIcon />
      </IconButton>
      <IconButton onClick={() => setCommentsOpen(o => !o)} size="small">
        <CommentIcon />
      </IconButton>
      <ToggleButtonGroup
        exclusive size="small" color="primary"
        value={type} onChange={(_, val) => val && onChange(val)}
      >
        <ToggleButton value="candles">Candle</ToggleButton>
        <ToggleButton value="heikin">Heikin-Ashi</ToggleButton>
        <ToggleButton value="renko">Renko</ToggleButton>
      </ToggleButtonGroup>
    </Box>
  );
}

ChartControls.propTypes = {
  type: PropTypes.oneOf(['candles', 'heikin', 'renko']).isRequired,
  onChange: PropTypes.func.isRequired,
  setSidebarOpen: PropTypes.func,
  setCommentsOpen: PropTypes.func,
};
