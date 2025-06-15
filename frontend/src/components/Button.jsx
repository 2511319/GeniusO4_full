// src/components/Button.jsx
import React from 'react';
import PropTypes from 'prop-types';

function classNames(...classes) {
  return classes.filter(Boolean).join(' ');
}

export default function Button({ variant = 'primary', onClick, disabled = false, children }) {
  const base = 'rounded focus:outline-none';
  const variants = {
    primary: 'px-4 py-2 text-sm font-medium bg-blue-500 text-white hover:bg-blue-600',
    secondary: 'px-4 py-2 text-sm font-medium bg-gray-200 text-gray-700 hover:bg-gray-300',
    loading: 'px-4 py-2 text-sm font-medium bg-gray-400 text-gray-600 cursor-wait',
    icon: 'p-1 text-gray-600 hover:bg-gray-200',
  };
  const isLoading = variant === 'loading';

  return (
    <button
      type="button"
      className={classNames(base, variants[variant], disabled ? 'opacity-50 cursor-not-allowed' : '')}
      onClick={onClick}
      disabled={isLoading || disabled}
    >
      {isLoading ? 'Loading...' : children}
    </button>
  );
}

Button.propTypes = {
  variant: PropTypes.oneOf(['primary', 'secondary', 'loading', 'icon']),
  onClick: PropTypes.func,
  disabled: PropTypes.bool,
  children: PropTypes.node,
};
