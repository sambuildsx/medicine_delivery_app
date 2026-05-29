import React, { useEffect, useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ShoppingCart, LogOut, ClipboardList, Pill, User } from 'lucide-react';

const Navbar = () => {
  const { user, logout, authFetch } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [cartCount, setCartCount] = useState(0);

  // Re-fetch cart count on location changes or whenever user logs in
  useEffect(() => {
    if (!user) return;
    
    const fetchCartCount = async () => {
      try {
        const res = await authFetch('/cart');
        if (res.ok) {
          const data = await res.json();
          // Count total quantity of items
          const count = data.items.reduce((acc, item) => acc + item.quantity, 0);
          setCartCount(count);
        }
      } catch (err) {
        console.error('Failed to fetch cart count in navbar:', err);
      }
    };

    fetchCartCount();
    
    // Listen for custom 'cartUpdated' event to instantly sync counts
    const handleCartUpdate = () => fetchCartCount();
    window.addEventListener('cartUpdated', handleCartUpdate);
    return () => window.removeEventListener('cartUpdated', handleCartUpdate);
  }, [user, location.pathname]);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <div className="navbar-inner">
        <Link to="/" className="brand">
          <Pill size={24} className="accent-primary" style={{ stroke: 'url(#brand-grad)' }} />
          <span>MedVibe</span>
        </Link>
        
        {user ? (
          <div className="nav-links">
            <Link to="/" className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}>
              <Pill size={18} />
              <span>Medicines</span>
            </Link>
            
            <Link to="/cart" className={`nav-link cart-indicator ${location.pathname === '/cart' ? 'active' : ''}`}>
              <ShoppingCart size={18} />
              <span>Cart</span>
              {cartCount > 0 && <span className="badge">{cartCount}</span>}
            </Link>
            
            <Link to="/orders" className={`nav-link ${location.pathname === '/orders' ? 'active' : ''}`}>
              <ClipboardList size={18} />
              <span>Orders</span>
            </Link>
            
            <div className="nav-link" style={{ cursor: 'default', color: '#ffffff', fontWeight: 600, borderLeft: '1px solid rgba(255,255,255,0.1)', paddingLeft: '1rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <User size={16} className="accent-primary" />
              <span>{user.full_name}</span>
            </div>
            
            <button onClick={handleLogout} className="logout-btn">
              <LogOut size={16} />
              <span>Logout</span>
            </button>
          </div>
        ) : (
          <div className="nav-links">
            <Link to="/login" className="btn btn-primary" style={{ padding: '0.5rem 1.25rem', fontSize: '0.9rem' }}>
              Sign In
            </Link>
          </div>
        )}
      </div>
      
      {/* SVG Gradient definition for brand icon */}
      <svg width="0" height="0" style={{ position: 'absolute' }}>
        <defs>
          <linearGradient id="brand-grad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#10b981" />
            <stop offset="100%" stopColor="#06b6d4" />
          </linearGradient>
        </defs>
      </svg>
    </nav>
  );
};

export default Navbar;
