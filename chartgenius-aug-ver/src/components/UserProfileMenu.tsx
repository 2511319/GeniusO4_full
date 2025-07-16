import { useEffect, useRef } from 'react';

interface UserProfileMenuProps {
  isOpen: boolean;
  onClose: () => void;
}

const UserProfileMenu: React.FC<UserProfileMenuProps> = ({ isOpen, onClose }) => {
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen, onClose]);

  const handlePersonalCabinet = () => {
    console.log('Переход в личный кабинет');
    onClose();
  };

  const handleLogout = () => {
    console.log('Выход из системы');
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div
      ref={menuRef}
      className="absolute right-0 top-full mt-2 w-48 bg-[#1e1e1e] border border-gray-700 rounded-lg shadow-lg z-50"
    >
      <div className="py-2">
        <button
          onClick={handlePersonalCabinet}
          className="w-full text-left px-4 py-2 text-gray-300 hover:bg-gray-700 hover:text-white transition-colors flex items-center gap-2"
        >
          <span className="text-sm">👤</span>
          Личный кабинет / Подписка
        </button>
        <hr className="border-gray-700 my-1" />
        <button
          onClick={handleLogout}
          className="w-full text-left px-4 py-2 text-gray-300 hover:bg-gray-700 hover:text-white transition-colors flex items-center gap-2"
        >
          <span className="text-sm">🚪</span>
          Выход
        </button>
      </div>
    </div>
  );
};

export default UserProfileMenu;
