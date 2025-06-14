// src/components/HeadlessTransition.jsx
import React, { Fragment, useState } from 'react';
import { Transition } from '@headlessui/react';

export default function HeadlessTransition() {
  const [show, setShow] = useState(false);
  return (
    <div>
      <button
        className="px-3 py-2 bg-green-500 text-white rounded"
        onClick={() => setShow(!show)}
      >
        Переключить
      </button>
      <Transition
        as={Fragment}
        show={show}
        enter="transition-opacity duration-300"
        enterFrom="opacity-0"
        enterTo="opacity-100"
        leave="transition-opacity duration-200"
        leaveFrom="opacity-100"
        leaveTo="opacity-0"
      >
        <div className="mt-2 rounded bg-green-100 p-4">
          Анимированный контент
        </div>
      </Transition>
    </div>
  );
}
