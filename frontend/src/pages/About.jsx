import React from 'react';
import { Box, Typography } from '@mui/material';

export default function About() {
  return (
    <Box p={2}>
      <Typography variant="h5" gutterBottom>About</Typography>
      <Typography>ChartGenius helps analyze cryptocurrency markets using technical indicators and GPT-based insights.</Typography>
    </Box>
  );
}
