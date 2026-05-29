import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { MapPin, Truck, Clock, ShieldCheck, AlertCircle, ArrowLeft, CheckCircle } from 'lucide-react';

const Checkout = () => {
  const { authFetch } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  
  // Passed coupon state from Cart.jsx
  const couponCode = location.state?.couponCode || '';

  // Form inputs
  const [pincode, setPincode] = useState('');
  const [distance, setDistance] = useState('');
  
  // State variables for checkout
  const [checkingService, setCheckingService] = useState(false);
  const [serviceStatus, setServiceStatus] = useState(null); // 'serviceable' or 'unserviceable'
  const [serviceMessage, setServiceMessage] = useState('');
  const [deliveryMinutes, setDeliveryMinutes] = useState(null);
  
  // Calculations returned from backend
  const [checkoutCart, setCheckoutCart] = useState(null);
  const [submittingOrder, setSubmittingOrder] = useState(false);
  const [submitError, setSubmitError] = useState(null);

  // Fetch standard cart (to verify items exist before starting)
  useEffect(() => {
    const checkEmptyCart = async () => {
      try {
        const res = await authFetch('/cart');
        if (res.ok) {
          const data = await res.json();
          if (data.items.length === 0) {
            navigate('/cart');
          }
        }
      } catch (err) {
        console.error('Error verifying cart state:', err);
      }
    };
    checkEmptyCart();
  }, []);

  const handleCheckServiceability = async (e) => {
    e.preventDefault();
    if (!pincode.trim() || !distance.trim()) {
      alert('Please fill out both Pincode and Distance.');
      return;
    }
    
    const distVal = parseInt(distance, 10);
    if (isNaN(distVal) || distVal < 0) {
      alert('Please enter a valid non-negative distance.');
      return;
    }

    setCheckingService(true);
    setServiceStatus(null);
    setServiceMessage('');
    setDeliveryMinutes(null);
    setCheckoutCart(null);
    
    try {
      const res = await authFetch('/serviceability/check', {
        method: 'POST',
        body: JSON.stringify({
          pincode: pincode.trim(),
          distance: distVal
        })
      });
      
      const data = await res.json();
      
      if (data.serviceable) {
        setServiceStatus('serviceable');
        setServiceMessage(data.message);
        setDeliveryMinutes(data.estimated_delivery_minutes);
        
        // Fetch cart again WITH distance parameter to compute delivery fee
        const cartRes = await authFetch(`/cart?distance=${distVal}&coupon_code=${encodeURIComponent(couponCode)}`);
        if (cartRes.ok) {
          const cartData = await cartRes.json();
          setCheckoutCart(cartData);
        }
      } else {
        setServiceStatus('unserviceable');
        setServiceMessage(data.message);
      }
    } catch (err) {
      alert('Serviceability query failed: ' + err.message);
    } finally {
      setCheckingService(false);
    }
  };

  const handlePlaceOrder = async () => {
    if (serviceStatus !== 'serviceable' || submittingOrder) return;
    
    setSubmittingOrder(true);
    setSubmitError(null);
    
    try {
      const res = await authFetch('/orders', {
        method: 'POST',
        body: JSON.stringify({
          pincode: pincode.trim(),
          distance: parseInt(distance, 10),
          coupon_code: couponCode || null
        })
      });
      
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Failed to place the order.');
      }
      
      // Dispatch custom cart event to notify navbar count is zero
      window.dispatchEvent(new Event('cartUpdated'));
      
      // Redirect to success page
      navigate('/order-success', { state: { orderId: data.id } });
    } catch (err) {
      setSubmitError(err.message);
      setSubmittingOrder(false);
    }
  };

  return (
    <div>
      <div style={{ marginBottom: '2.5rem', display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <button onClick={() => navigate('/cart')} className="btn btn-secondary" style={{ padding: '0.5rem 0.75rem' }}>
          <ArrowLeft size={16} />
        </button>
        <div>
          <h1 style={{ fontSize: '2.25rem', fontFamily: 'var(--font-display)', fontWeight: 800 }}>
            Delivery Checkout
          </h1>
          <p style={{ color: 'var(--text-secondary)' }}>
            Confirm delivery address serviceability and place your order.
          </p>
        </div>
      </div>

      <div className="cart-layout">
        {/* Pincode & Distance serviceability check panel */}
        <div>
          <div className="glass-card" style={{ marginBottom: '2rem' }}>
            <h3 style={{ fontSize: '1.25rem', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <MapPin className="accent-primary" size={20} />
              <span>Verify Delivery Address</span>
            </h3>

            <form onSubmit={handleCheckServiceability}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1.5rem' }}>
                <div className="form-group" style={{ marginBottom: 0 }}>
                  <label className="form-label">Delivery Pincode</label>
                  <input 
                    type="text" 
                    className="form-control" 
                    placeholder="e.g. 560001"
                    value={pincode}
                    onChange={(e) => setPincode(e.target.value)}
                    required
                  />
                </div>
                <div className="form-group" style={{ marginBottom: 0 }}>
                  <label className="form-label">Distance from Store (meters)</label>
                  <input 
                    type="number" 
                    className="form-control" 
                    placeholder="e.g. 1500"
                    value={distance}
                    onChange={(e) => setDistance(e.target.value)}
                    required
                  />
                </div>
              </div>

              <button 
                type="submit" 
                className="btn btn-secondary" 
                style={{ width: '100%' }}
                disabled={checkingService}
              >
                {checkingService ? 'Verifying Serviceability...' : 'Check Serviceability'}
              </button>
            </form>

            {/* Serviceability Result message */}
            {serviceStatus && (
              <div className={`serviceability-status-box ${serviceStatus}`}>
                {serviceStatus === 'serviceable' ? (
                  <>
                    <CheckCircle size={20} style={{ flexShrink: 0 }} />
                    <div style={{ fontSize: '0.95rem' }}>
                      <strong>Serviceable!</strong> {serviceMessage}
                    </div>
                  </>
                ) : (
                  <>
                    <AlertCircle size={20} style={{ flexShrink: 0 }} />
                    <div style={{ fontSize: '0.95rem' }}>
                      <strong>Unserviceable.</strong> {serviceMessage}
                    </div>
                  </>
                )}
              </div>
            )}
          </div>
          
          {serviceStatus === 'serviceable' && (
            <div className="glass-card">
              <h3 style={{ fontSize: '1.15rem', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Truck className="accent-secondary" size={18} />
                <span>Delivery Estimation</span>
              </h3>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div style={{ background: 'rgba(255,255,255,0.02)', padding: '1rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-glass)', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <Clock className="accent-primary" size={24} />
                  <div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Estimated Duration</div>
                    <div style={{ fontWeight: 700, color: '#ffffff' }}>{deliveryMinutes} Minutes</div>
                  </div>
                </div>
                <div style={{ background: 'rgba(255,255,255,0.02)', padding: '1rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-glass)', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <ShieldCheck className="accent-secondary" size={24} />
                  <div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Safety Standard</div>
                    <div style={{ fontWeight: 700, color: '#ffffff' }}>Hygiene Guaranteed</div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Dynamic checkout total billing card */}
        <div className="glass-card">
          <h3 style={{ fontSize: '1.25rem', marginBottom: '1.5rem', borderBottom: '1px solid var(--border-glass)', paddingBottom: '0.5rem' }}>
            Checkout Summary
          </h3>
          
          {checkoutCart ? (
            <div>
              <div className="checkout-summary">
                <div className="summary-row">
                  <span>Items Subtotal</span>
                  <span>₹{Number(checkoutCart.item_total).toFixed(2)}</span>
                </div>
                
                {checkoutCart.discount_amount > 0 && (
                  <div className="summary-row discount">
                    <span>Voucher Saved ({checkoutCart.coupon_applied})</span>
                    <span>-₹{Number(checkoutCart.discount_amount).toFixed(2)}</span>
                  </div>
                )}

                <div className="summary-row">
                  <span>Small Cart Fee</span>
                  <span>₹{Number(checkoutCart.small_cart_fee).toFixed(2)}</span>
                </div>

                <div className="summary-row">
                  <span>Delivery Charge</span>
                  <span>₹{Number(checkoutCart.delivery_fee).toFixed(2)}</span>
                </div>

                <div className="summary-row">
                  <span>Late Night Surcharge</span>
                  <span>₹{Number(checkoutCart.late_night_fee).toFixed(2)}</span>
                </div>

                <div className="summary-row total">
                  <span>Total Payable</span>
                  <span>₹{Number(checkoutCart.total_payable).toFixed(2)}</span>
                </div>
              </div>

              {submitError && (
                <div className="error-banner" style={{ margin: '1rem 0' }}>
                  <AlertCircle size={16} />
                  <span>{submitError}</span>
                </div>
              )}

              <button 
                onClick={handlePlaceOrder}
                className="btn btn-primary"
                style={{ width: '100%', padding: '0.9rem' }}
                disabled={submittingOrder}
              >
                {submittingOrder ? 'Placing Order...' : 'Confirm & Place Order'}
              </button>
            </div>
          ) : (
            <div style={{ textAlign: 'center', padding: '2rem 1rem', color: 'var(--text-muted)' }}>
              <Truck size={36} style={{ marginBottom: '0.5rem', opacity: 0.3 }} />
              <p style={{ fontSize: '0.9rem' }}>
                Please check address serviceability on the left to compute delivery charges and enable order placement.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Checkout;
