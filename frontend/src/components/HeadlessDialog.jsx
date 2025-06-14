// src/components/HeadlessDialog.jsx
import React, { Fragment, useState } from 'react';
import { Dialog, Transition } from '@headlessui/react';

export default function HeadlessDialog() {
  const [isOpen, setIsOpen] = useState(false);
  return (
    <>
      <button
        className="px-3 py-2 bg-blue-500 text-white rounded"
        onClick={() => setIsOpen(true)}
      >
        Открыть диалог
      </button>

      <Transition appear show={isOpen} as={Fragment}>
        <Dialog as="div" className="relative z-10" onClose={() => setIsOpen(false)}>
          <Transition.Child
            as={Fragment}
            enter="ease-out duration-300"
            enterFrom="opacity-0"
            enterTo="opacity-100"
            leave="ease-in duration-200"
            leaveFrom="opacity-100"
            leaveTo="opacity-0"
          >
            <div className="fixed inset-0 bg-black/25" />
          </Transition.Child>

          <div className="fixed inset-0 overflow-y-auto">
            <div className="flex min-h-full items-center justify-center p-4">
              <Transition.Child
                as={Fragment}
                enter="ease-out duration-300"
                enterFrom="opacity-0 scale-95"
                enterTo="opacity-100 scale-100"
                leave="ease-in duration-200"
                leaveFrom="opacity-100 scale-100"
                leaveTo="opacity-0 scale-95"
              >
                <Dialog.Panel className="w-full max-w-md transform overflow-hidden rounded-2xl bg-white p-6 text-left align-middle shadow-xl transition-all">
                  <Dialog.Title as="h3" className="text-lg font-medium leading-6 text-gray-900">
                    Простое диалоговое окно
                  </Dialog.Title>
                  <p className="mt-2 text-sm text-gray-500">Пример компонента Dialog.</p>
                  <div className="mt-4">
                    <button
                      className="inline-flex justify-center rounded-md bg-blue-100 px-4 py-2 text-sm font-medium text-blue-900 hover:bg-blue-200"
                      onClick={() => setIsOpen(false)}
                    >
                      Закрыть
                    </button>
                  </div>
                </Dialog.Panel>
              </Transition.Child>
            </div>
          </div>
        </Dialog>
      </Transition>
    </>
  );
}
