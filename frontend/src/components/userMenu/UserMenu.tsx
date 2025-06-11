import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import styles from './UserMenu.module.css';

interface UserMenuProps {
  onMenuAction?: () => void;
}

const UserMenu: React.FC<UserMenuProps> = ({ onMenuAction }) => {
  const { user, logout } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  const handleLogout = () => {
    logout();
    setIsOpen(false);
    onMenuAction?.(); // Cerrar menú móvil si existe
  };

  const handleMenuItemClick = () => {
    setIsOpen(false);
    onMenuAction?.(); // Cerrar menú móvil si existe
  };

  // Función actualizada para usar email
  const getInitials = (email: string): string => {
    console.log('letra inicial del email:', email.charAt(0).toUpperCase());
    return email.charAt(0).toUpperCase();
  };

  const handleClickOutside = (event: MouseEvent) => {
    if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
      setIsOpen(false);
    }
  };

  useEffect(() => {
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);


  if (!user) return null;

  return (
    <div className={styles.userMenu} ref={menuRef}>
      <button
        className={styles.userButton}
        onClick={() => setIsOpen(!isOpen)}
        aria-label="User menu"
      >
        <div className={styles.avatar}>
          {getInitials(user.email)}
        </div>
      </button>

      {isOpen && (
        <div className={styles.dropdown}>
          <div className={styles.userInfo}>
            <div className={styles.userName}>{user.username}</div>
            <div className={styles.userEmail}>{user.email}</div>
          </div>
          
          <div className={styles.divider}></div>
          
          <button className={styles.menuItem} onClick={handleMenuItemClick}>
            <svg className={styles.icon} viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
              <circle cx="12" cy="7" r="4"></circle>
            </svg>
            Account Settings
          </button>
          
          <button className={styles.menuItem}>
            <svg className={styles.icon} viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
              <polyline points="16,17 21,12 16,7"></polyline>
              <line x1="21" y1="12" x2="9" y2="12"></line>
            </svg>
            My Predictions
          </button>
          
          <div className={styles.divider}></div>
          
          <button 
            className={`${styles.menuItem} ${styles.logoutItem}`}
            onClick={handleLogout}
          >
            <svg className={styles.icon} viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
              <polyline points="16,17 21,12 16,7"></polyline>
              <line x1="21" y1="12" x2="9" y2="12"></line>
            </svg>
            Sign Out
          </button>
        </div>
      )}
    </div>
  );
};

export default UserMenu;
