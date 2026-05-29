import React, { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Trash2, AlertTriangle, ArrowRight, Pill, Ticket, Percent } from 'lucide-react';

const Cart = () => {
  const { authFetch } = useAuth();
  const navigate = useNavigate();
  const [cartData, setCartData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Coupon input states
  const [couponInput, setCouponInput] = useState('');
  const [couponMessage, setCouponMessage] = useState(null);
  const [couponStatus, setCouponStatus] = useState(null); // 'valid' or 'invalid'

  const fetchCart = async (couponCode = '') => {
    try {
      const url = couponCode ? `/cart?coupon_code=${encodeURIComponent(couponCode)}` : '/cart';
      const res = await authFetch(url);
      if (res.ok) {
        const data = await res.json();
        setCartData(data);
        if (data.coupon_applied) {
          setCouponInput(data.coupon_applied);
        }
      } else {
        throw new Error('Failed to retrieve cart details.');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCart();
  }, []);

  const handleUpdateQty = async (itemId, currentQty, amount, maxStock) => {
    const newQty = currentQty + amount;
    
    // Prevent lowering below 1 (user must use remove/delete instead)
    if (newQty < 1) return;
    
    if (newQty > maxStock) {
      alert(`Cannot increase quantity. Maximum available stock is ${maxStock}.`);
      return;
    }

    try {
      const res = await authFetch(`/cart/items/${itemId}`, {
        method: 'PATCH',
        body: JSON.stringify({ quantity: newQty })
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Could not update quantity.');
      }
      
      // Dispatch custom cart event to notify navbar count
      window.dispatchEvent(new Event('cartUpdated'));
      
      // Refresh cart with current applied coupon if any
      fetchCart(cartData.coupon_applied || '');
    } catch (err) {
      alert(err.message);
    }
  };

  const handleRemoveItem = async (itemId) => {
    if (!confirm('Are you sure you want to remove this medicine from your cart?')) return;
    
    try {
      const res = await authFetch(`/cart/items/${itemId}`, {
        method: 'DELETE'
      });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || 'Could not remove item.');
      }
      
      // Dispatch custom cart event to notify navbar count
      window.dispatchEvent(new Event('cartUpdated'));
      
      // Refresh cart
      fetchCart(cartData.coupon_applied || '');
    } catch (err) {
      alert(err.message);
    }
  };

  const handleApplyCoupon = async (e) => {
    e.preventDefault();
    setCouponMessage(null);
    setCouponStatus(null);
    
    if (!couponInput.trim()) {
      setCouponMessage('Please enter a coupon code.');
      setCouponStatus('invalid');
      return;
    }

    try {
      const res = await authFetch('/coupons/apply', {
        method: 'POST',
        body: JSON.stringify({ code: couponInput.trim() })
      });
      const data = await res.json();
      
      if (data.valid) {
        setCouponMessage(data.message);
        setCouponStatus('valid');
        // Refresh cart calculations with applied coupon
        fetchCart(couponInput.trim().toUpperCase());
      } else {
        setCouponMessage(data.message);
        setCouponStatus('invalid');
        // Re-fetch cart with no coupon to clear any invalid discounts
        fetchCart('');
      }
    } catch (err) {
      setCouponMessage(err.message);
      setCouponStatus('invalid');
    }
  };

  const handleRemoveCoupon = () => {
    setCouponInput('');
    setCouponMessage(null);
    setCouponStatus(null);
    fetchCart('');
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', padding: '6rem' }}>
        <div style={{ width: '40px', height: '40px', border: '3px solid rgba(255,255,255,0.1)', borderTopColor: 'var(--accent-primary)', borderRadius: '50%', animation: 'pulseGlow 1s infinite linear' }}></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-banner" style={{ maxWidth: '600px', margin: '4rem auto' }}>
        <AlertTriangle size={18} />
        <span>{error}</span>
      </div>
    );
  }

  const hasItems = cartData && cartData.items.length > 0;

  return (
    <div>
      <div style={{ marginBottom: '2.5rem' }}>
        <h1 style={{ fontSize: '2.25rem', fontFamily: 'var(--font-display)', fontWeight: 800, marginBottom: '0.5rem' }}>
          Your Shopping Cart
        </h1>
        <p style={{ color: 'var(--text-secondary)' }}>
          Review selected medicines, adjust quantities, and apply discount vouchers.
        </p>
      </div>

      {!hasItems ? (
        <div className="glass-card" style={{ textAlign: 'center', padding: '5rem 2rem', borderStyle: 'dashed' }}>
          <Pill size={48} className="accent-primary" style={{ marginBottom: '1.5rem', opacity: 0.4 }} />
          <h2 style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>Your Cart is Empty</h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>
            Browse our medicine catalog and add items to your cart.
          </p>
          <Link to="/" className="btn btn-primary">
            Browse Catalogue
          </Link>
        </div>
      ) : (
        <div className="cart-layout">
          {/* Cart items list */}
          <div className="cart-items-list">
            {cartData.items.map((item) => {
              const itemTotal = (item.medicine.selling_price * item.quantity).toFixed(2);
              return (
                <div key={item.id} className="cart-item-card">
                  <div className="cart-item-info">
                    <h4 style={{ color: '#ffffff' }}>{item.medicine.name}</h4>
                    <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontStyle: 'italic', marginBottom: '0.25rem' }}>
                      {item.medicine.salt_composition}
                    </p>
                    <span className={item.medicine.prescription_required ? "badge-prescription" : "badge-otc"}>
                      {item.medicine.prescription_required ? "Rx Required" : "OTC"}
                    </span>
                  </div>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem', alignItems: 'center' }}>
                    <div className="qty-counter">
                      <button 
                        onClick={() => handleUpdateQty(item.id, item.quantity, -1, item.medicine.stock)}
                        className="qty-btn"
                        disabled={item.quantity <= 1}
                      >
                        -
                      </button>
                      <span className="qty-number">{item.quantity}</span>
                      <button 
                        onClick={() => handleUpdateQty(item.id, item.quantity, 1, item.medicine.stock)}
                        className="qty-btn"
                        disabled={item.quantity >= item.medicine.stock}
                      >
                        +
                      </button>
                    </div>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      Stock: {item.medicine.stock}
                    </span>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                    <div style={{ textAlign: 'right' }}>
                      <div style={{ fontWeight: 700, fontSize: '1.1rem', fontFamily: 'var(--font-display)' }}>
                        ₹{itemTotal}
                      </div>
                      <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                        ₹{item.medicine.selling_price} each
                      </div>
                    </div>

                    <button 
                      onClick={() => handleRemoveItem(item.id)}
                      className="remove-item-btn"
                      title="Remove medicine"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Pricing & Voucher Summary */}
          <div className="glass-card">
            <h3 style={{ fontSize: '1.25rem', marginBottom: '1.5rem', borderBottom: '1px solid var(--border-glass)', paddingBottom: '0.5rem' }}>
              Order Breakdown
            </h3>

            {/* Coupon Apply Form */}
            <form onSubmit={handleApplyCoupon} style={{ marginBottom: '1.5rem' }}>
              <label className="form-label">Promotional Voucher</label>
              <div className="coupon-box">
                <div style={{ position: 'relative', flex: 1 }}>
                  <Ticket size={18} style={{ position: 'absolute', left: '0.75rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                  <input 
                    type="text" 
                    className="form-control" 
                    style={{ paddingLeft: '2.5rem', textTransform: 'uppercase' }}
                    placeholder="VOUCHER CODE (e.g. FLAT50)"
                    value={couponInput}
                    onChange={(e) => setCouponInput(e.target.value)}
                    disabled={!!cartData.coupon_applied}
                  />
                </div>
                {cartData.coupon_applied ? (
                  <button 
                    type="button" 
                    className="btn btn-secondary" 
                    onClick={handleRemoveCoupon}
                    style={{ padding: '0 1rem' }}
                  >
                    Clear
                  </button>
                ) : (
                  <button 
                    type="submit" 
                    className="btn btn-primary"
                    style={{ padding: '0 1.25rem' }}
                  >
                    Apply
                  </button>
                )}
              </div>
              {couponMessage && (
                <div className={`coupon-status ${couponStatus}`}>
                  {couponStatus === 'valid' ? (
                    <span>{couponMessage}</span>
                  ) : (
                    <span>{couponMessage}</span>
                  )}
                </div>
              )}
            </form>

            {/* Calculations Breakdown */}
            <div className="checkout-summary">
              <div className="summary-row">
                <span>Items Subtotal</span>
                <span>₹{Number(cartData.item_total).toFixed(2)}</span>
              </div>
              
              {cartData.discount_amount > 0 && (
                <div className="summary-row discount">
                  <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                    <Percent size={14} />
                    Coupon Discount ({cartData.coupon_applied})
                  </span>
                  <span>-₹{Number(cartData.discount_amount).toFixed(2)}</span>
                </div>
              )}

              <div className="summary-row">
                <span style={{ display: 'flex', flexDirection: 'column' }}>
                  <span>Small Cart Fee</span>
                  {Number(cartData.small_cart_fee) > 0 && (
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      Applied since subtotal &lt; ₹199
                    </span>
                  )}
                </span>
                <span>₹{Number(cartData.small_cart_fee).toFixed(2)}</span>
              </div>

              <div className="summary-row">
                <span style={{ display: 'flex', flexDirection: 'column' }}>
                  <span>Late Night Surcharge</span>
                  {Number(cartData.late_night_fee) > 0 && (
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      Applied (Placed 10 PM - 6 AM IST)
                    </span>
                  )}
                </span>
                <span>₹{Number(cartData.late_night_fee).toFixed(2)}</span>
              </div>

              <div className="summary-row" style={{ fontStyle: 'italic', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                <span>Delivery Charge</span>
                <span>Calculated at checkout</span>
              </div>

              <div className="summary-row total">
                <span>Payable Subtotal</span>
                <span>₹{Number(cartData.total_payable).toFixed(2)}</span>
              </div>
            </div>

            <button 
              onClick={() => navigate('/checkout', { state: { couponCode: cartData.coupon_applied } })}
              className="btn btn-primary"
              style={{ width: '100%', padding: '0.9rem' }}
            >
              <span>Proceed to Checkout</span>
              <ArrowRight size={16} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Cart;
