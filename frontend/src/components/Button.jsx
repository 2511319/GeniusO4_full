// src/components/Button.jsx
import React from 'react';
import PropTypes from 'prop-types';

function classNames(...classes) {
  return classes.filter(Boolean).join(' ');
}

export default function Button({ variant = 'primary', onClick, children }) {
  const base = 'px-4 py-2 rounded text-sm font-medium focus:outline-none';
  const variants = {
    primary: 'bg-blue-500 text-white hover:bg-blue-600',
    secondary: 'bg-gray-200 text-gray-700 hover:bg-gray-300',
    loading: 'bg-gray-400 text-gray-600 cursor-wait',
  };
  const isLoading = variant === 'loading';

  return (
    <button
      type="button"
      className={classNames(base, variants[variant])}
      onClick={onClick}
      disabled={isLoading}
    >
      {isLoading ? 'Loading...' : children}
    </button>
  );
}

Button.propTypes = {
  variant: PropTypes.oneOf(['primary', 'secondary', 'loading']),
  onClick: PropTypes.func,
  children: PropTypes.node,
};
