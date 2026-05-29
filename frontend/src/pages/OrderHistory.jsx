import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { ClipboardList, Calendar, MapPin, Truck, ChevronDown, ChevronUp, AlertCircle, ShoppingCart } from 'lucide-react';

const OrderHistory = () => {
  const { authFetch } = useAuth();
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Track expanded order IDs
  const [expandedOrders, setExpandedOrders] = useState({});

  const fetchOrders = async () => {
    try {
      const res = await authFetch('/orders');
      if (res.ok) {
        const data = await res.json();
        setOrders(data);
      } else {
        throw new Error('Failed to retrieve order history.');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOrders();
  }, []);

  const toggleExpand = (orderId) => {
    setExpandedOrders(prev => ({
      ...prev,
      [orderId]: !prev[orderId]
    }));
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

  return (
    <div>
      <div style={{ marginBottom: '2.5rem' }}>
        <h1 style={{ fontSize: '2.25rem', fontFamily: 'var(--font-display)', fontWeight: 800, marginBottom: '0.5rem' }}>
          Your Order History
        </h1>
        <p style={{ color: 'var(--text-secondary)' }}>
          Trace your active deliveries, explore invoices, and review medicine receipts.
        </p>
      </div>

      {orders.length === 0 ? (
        <div className="glass-card" style={{ textAlign: 'center', padding: '5rem 2rem', borderStyle: 'dashed' }}>
          <ClipboardList size={48} className="accent-secondary" style={{ marginBottom: '1.5rem', opacity: 0.4 }} />
          <h2 style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>No Orders Yet</h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>
            You haven't placed any medicine orders on MedVibe yet.
          </p>
        </div>
      ) : (
        <div className="order-history-list">
          {orders.map((order) => {
            const isExpanded = !!expandedOrders[order.id];
            const dateStr = new Date(order.created_at).toLocaleString('en-IN', {
              day: 'numeric',
              month: 'short',
              year: 'numeric',
              hour: '2-digit',
              minute: '2-digit'
            });

            return (
              <div key={order.id} className="glass-card order-history-card" style={{ padding: '1.5rem' }}>
                <div style={{ display: 'flex', justifyContent: 'between', alignItems: 'center', cursor: 'pointer' }} onClick={() => toggleExpand(order.id)}>
                  <div style={{ flex: 1, display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem' }}>
                    <div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Order ID</div>
                      <div style={{ fontWeight: 700, fontSize: '1.05rem', color: '#ffffff' }}>#{order.id}</div>
                    </div>
                    <div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Placed On</div>
                      <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                        <Calendar size={14} />
                        <span>{dateStr}</span>
                      </div>
                    </div>
                    <div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Total Bill</div>
                      <div style={{ fontWeight: 800, fontSize: '1.05rem', color: 'var(--accent-primary)', fontFamily: 'var(--font-display)' }}>₹{Number(order.total_payable).toFixed(2)}</div>
                    </div>
                    <div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Status</div>
                      <div>
                        <span className={`order-status-badge ${order.status}`}>
                          {order.status}
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  <button className="remove-item-btn" style={{ marginLeft: '1rem' }}>
                    {isExpanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
                  </button>
                </div>

                {/* Expanded receipt details section */}
                {isExpanded && (
                  <div style={{ marginTop: '1.5rem', borderTop: '1px solid var(--border-glass)', paddingTop: '1.5rem', animation: 'fadeIn 0.25s ease-out' }}>
                    <div className="cart-layout" style={{ gap: '1.5rem' }}>
                      {/* Left side: Purchased items list */}
                      <div>
                        <h4 style={{ fontSize: '1rem', color: '#ffffff', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                          <ShoppingCart size={16} className="accent-primary" />
                          <span>Receipt Items</span>
                        </h4>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                          {order.items.map((item) => (
                            <div key={item.id} style={{ display: 'flex', justifyContent: 'space-between', padding: '0.75rem 1rem', background: 'rgba(255,255,255,0.01)', border: '1px solid var(--border-glass)', borderRadius: 'var(--radius-md)', fontSize: '0.9rem' }}>
                              <div>
                                <strong style={{ color: '#ffffff' }}>{item.name}</strong>
                                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontStyle: 'italic', display: 'block' }}>
                                  {item.salt_composition}
                                </span>
                              </div>
                              <div style={{ textAlign: 'right' }}>
                                <strong>₹{(item.selling_price * item.quantity).toFixed(2)}</strong>
                                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block' }}>
                                  ₹{item.selling_price} × {item.quantity}
                                </span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Right side: Invoice bill & Delivery log */}
                      <div style={{ background: 'rgba(255,255,255,0.02)', padding: '1.25rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-glass)' }}>
                        <h4 style={{ fontSize: '1rem', color: '#ffffff', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                          <Truck size={16} className="accent-secondary" />
                          <span>Delivery & Fees</span>
                        </h4>
                        
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '1rem', paddingBottom: '1rem', borderBottom: '1px solid var(--border-glass)' }}>
                          <div style={{ display: 'flex', justify: 'between' }}>
                            <span>Deliver Pincode:</span>
                            <span style={{ color: '#ffffff', fontWeight: 600 }}>{order.pincode}</span>
                          </div>
                          <div style={{ display: 'flex', justify: 'between' }}>
                            <span>Store Distance:</span>
                            <span style={{ color: '#ffffff', fontWeight: 600 }}>{order.distance} meters</span>
                          </div>
                          <div style={{ display: 'flex', justify: 'between' }}>
                            <span>Estimated Duration:</span>
                            <span style={{ color: '#ffffff', fontWeight: 600 }}>{order.estimated_delivery_minutes} mins</span>
                          </div>
                        </div>

                        <div className="checkout-summary" style={{ fontSize: '0.85rem', gap: '0.5rem', border: 'none', padding: 0, margin: 0 }}>
                          <div className="summary-row">
                            <span>Subtotal</span>
                            <span>₹{Number(order.item_total).toFixed(2)}</span>
                          </div>
                          {order.discount_amount > 0 && (
                            <div className="summary-row discount">
                              <span>Voucher ({order.coupon_applied})</span>
                              <span>-₹{Number(order.discount_amount).toFixed(2)}</span>
                            </div>
                          )}
                          <div className="summary-row">
                            <span>Small Cart Fee</span>
                            <span>₹{Number(order.small_cart_fee).toFixed(2)}</span>
                          </div>
                          <div className="summary-row">
                            <span>Delivery Fee</span>
                            <span>₹{Number(order.delivery_fee).toFixed(2)}</span>
                          </div>
                          <div className="summary-row">
                            <span>Late Night Surcharge</span>
                            <span>₹{Number(order.late_night_fee).toFixed(2)}</span>
                          </div>
                          <div className="summary-row total" style={{ fontSize: '1.1rem', marginTop: '0.5rem' }}>
                            <span>Paid Total</span>
                            <span>₹{Number(order.total_payable).toFixed(2)}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default OrderHistory;
