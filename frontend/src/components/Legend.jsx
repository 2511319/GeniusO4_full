// src/components/Legend.jsx

import React from 'react';
import PropTypes from 'prop-types';
import { Box, Typography, List, ListItem, ListItemIcon, ListItemText } from '@mui/material';

/**
 * Legend — простая легенда, в которую передаётся массив meta:
 * [{ key, name, color, dashed, icon, visible }, ...]
 */
export default function Legend({ meta = [], orientation = 'vertical' }) {  // meta по умолчанию = []
  return (
    <Box sx={(theme) => ({
      position: 'absolute',
      bottom: 0,
      left: 0,
      zIndex: 2,
      bgcolor: theme.palette.background.paper,
      maxHeight: 200,
      overflowY: 'auto',
      p: theme.spacing(1),
      borderRadius: theme.shape.borderRadius,
    })}>
      <Typography variant="subtitle2" gutterBottom>Legend</Typography>
      <List
        dense
        disablePadding
        sx={{
          display: 'flex',
          flexDirection: orientation === 'horizontal' ? 'row' : 'column',
          flexWrap: orientation === 'horizontal' ? 'wrap' : 'nowrap',
        }}
      >
        {meta.map(item => (
          <ListItem
            key={item.key}
            button
            onClick={item.onToggle}  // onToggle можно добавить в meta
          >
            <ListItemIcon>
              <Box
                sx={{
                  width: 12,
                  height: 12,
                  bgcolor: item.color,
                  border: item.dashed ? '1px dashed' : 'none',
                  display: 'inline-block',
                }}
              >
                {item.icon && <Typography component="span" sx={{ fontSize: 10 }}>{item.icon}</Typography>}
              </Box>
            </ListItemIcon>
            <ListItemText
              primary={item.name}
              sx={{ textDecoration: item.visible ? 'none' : 'line-through' }}
            />
          </ListItem>
        ))}
      </List>
    </Box>
  );
}

Legend.propTypes = {
  meta: PropTypes.arrayOf(PropTypes.shape({
    key:     PropTypes.string.isRequired,
    name:    PropTypes.string.isRequired,
    color:   PropTypes.string,
    dashed:  PropTypes.bool,
    icon:    PropTypes.string,
    visible: PropTypes.bool,
    onToggle:PropTypes.func,
  })),
  orientation: PropTypes.oneOf(['vertical', 'horizontal']),
};
