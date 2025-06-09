import React from 'react';
import { Box } from '@mui/material';

export default function Legend({ items }) {
  if (!items.length) return null;

  return (
    <Box
      sx={{
        position: 'absolute',
        top: 8,
        left: 8,
        backgroundColor: 'rgba(0,0,0,0.6)',
        color: '#fff',
        borderRadius: 1,
        p: 1,
        fontSize: '12px',
        zIndex: 30,
      }}
    >
      {items.map(({ name, color, dashed, icon }) => (
        <Box key={name} sx={{ display: 'flex', alignItems: 'center', mb: 0.5 }}>
          {icon ? (
            <Box component="span" sx={{ mr: 1, color }}>{icon}</Box>
          ) : (
            <Box
              sx={{
                width: 12,
                height: 12,
                mr: 1,
                border: dashed ? `2px dashed ${color}` : `2px solid ${color}`,
                backgroundColor: dashed ? 'transparent' : color,
              }}
            />
          )}
          {name}
        </Box>
      ))}
    </Box>
  );
}
