import React from 'react';
import PropTypes from 'prop-types';

export default function Spinner({ size = 20 }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 44 44"
      xmlns="http://www.w3.org/2000/svg"
      stroke="currentColor"
    >
      <g fill="none" fillRule="evenodd" strokeWidth="4">
        <circle cx="22" cy="22" r="18" strokeOpacity="0.5" />
        <path d="M40 22c0-9.94-8.06-18-18-18">
          <animateTransform
            attributeName="transform"
            type="rotate"
            from="0 22 22"
            to="360 22 22"
            dur="1s"
            repeatCount="indefinite"
          />
        </path>
      </g>
    </svg>
  );
}

Spinner.propTypes = {
  size: PropTypes.number,
};
