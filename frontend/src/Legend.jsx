import React from 'react';
import { Box } from '@mui/material';

export default function Legend({ items, onToggle }) {
  if (!items.length) return null;

  return (
    <Box
      sx={{
        position: 'absolute',
        bottom: 8,
        left: 8,
        backgroundColor: 'rgba(0,0,0,0.6)',
        color: '#fff',
        borderRadius: 1,
        p: 1,
        fontSize: '12px',
        zIndex: 30,
      }}
    >
      {items.map(({ name, color, dashed, icon, active }) => (
        <Box
          key={name}
          sx={{
            display: 'flex',
            alignItems: 'center',
            mb: 0.5,
            cursor: 'pointer',
            opacity: active ? 1 : 0.5,
          }}
          onClick={() => onToggle && onToggle(name)}
        >
          {icon ? (
            <Box component="span" sx={{ mr: 1, color }}>{icon}</Box>
          ) : (
            <Box
              sx={{
                width: 12,
                height: 12,
                mr: 1,
                border: dashed ? `2px dashed ${color}` : `2px solid ${color}`,
                backgroundColor: active && !dashed ? color : 'transparent',
              }}
            />
          )}
          {name}
        </Box>
      ))}
    </Box>
  );
}
