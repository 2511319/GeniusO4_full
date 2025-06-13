import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom/vitest';
import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import Legend from './Legend';

describe('Legend', () => {
  it('calls onToggle and reflects visibility', () => {
    const onToggle = vi.fn();
    const { rerender } = render(
      <Legend meta={[{ key: 'Volume', name: 'Volume', color: '#000', visible: true, onToggle }]} />
    );
    const item = screen.getByText('Volume');
    fireEvent.click(item);
    expect(onToggle).toHaveBeenCalled();

  rerender(
    <Legend meta={[{ key: 'Volume', name: 'Volume', color: '#000', visible: false, onToggle }]} />
  );
  screen.getByText('Volume');
  });
});
