import React from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { Check, ClipboardList, ShoppingBag } from 'lucide-react';

const OrderSuccess = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const orderId = location.state?.orderId;

  return (
    <div style={{ maxWidth: '550px', margin: '4rem auto', textAlign: 'center' }}>
      <div className="glass-card" style={{ padding: '3.5rem 2rem' }}>
        <div style={{ 
          width: '72px', 
          height: '72px', 
          backgroundColor: 'rgba(16, 185, 129, 0.1)', 
          border: '2px solid var(--accent-primary)', 
          borderRadius: '50%', 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center', 
          margin: '0 auto 2rem',
          boxShadow: '0 0 20px rgba(16,185,129,0.3)',
          animation: 'pulseGlow 2s infinite'
        }}>
          <Check size={36} className="accent-primary" />
        </div>

        <h1 style={{ fontSize: '2rem', fontFamily: 'var(--font-display)', fontWeight: 800, marginBottom: '0.75rem' }}>
          Order Confirmed!
        </h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '1.05rem', marginBottom: '1.5rem' }}>
          Your prescription and medicines are registered. The store is assembling your order.
        </p>

        {orderId && (
          <div style={{ 
            backgroundColor: 'rgba(255,255,255,0.03)', 
            border: '1px solid var(--border-glass)', 
            borderRadius: 'var(--radius-md)', 
            padding: '0.75rem 1.5rem', 
            fontSize: '1rem', 
            fontFamily: 'monospace', 
            color: '#ffffff', 
            display: 'inline-block',
            marginBottom: '2.5rem'
          }}>
            Order Reference: #{orderId}
          </div>
        )}

        <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
          <Link to="/orders" className="btn btn-secondary">
            <ClipboardList size={16} />
            <span>Order History</span>
          </Link>
          <Link to="/" className="btn btn-primary">
            <ShoppingBag size={16} />
            <span>Shop More</span>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default OrderSuccess;
