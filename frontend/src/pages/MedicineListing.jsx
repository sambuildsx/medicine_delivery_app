import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Search, ShoppingCart, Plus, Info, AlertTriangle, CheckCircle } from 'lucide-react';

const MedicineListing = () => {
  const { authFetch } = useAuth();
  const [medicines, setMedicines] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Tracking addition status to show subtle checkmark confirmations
  const [addingId, setAddingId] = useState(null);
  const [successId, setSuccessId] = useState(null);

  const fetchMedicines = async (query = '') => {
    setLoading(true);
    setError(null);
    try {
      const endpoint = query ? `/medicines/search?q=${encodeURIComponent(query)}` : '/medicines';
      const res = await authFetch(endpoint);
      if (res.ok) {
        const data = await res.json();
        setMedicines(data);
      } else {
        throw new Error('Failed to fetch medicines. Please try again later.');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMedicines();
  }, []);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchMedicines(searchQuery);
  };

  const handleAddToCart = async (medicine) => {
    if (medicine.stock <= 0) return;
    
    setAddingId(medicine.id);
    try {
      const res = await authFetch('/cart/items', {
        method: 'POST',
        body: JSON.stringify({
          medicine_id: medicine.id,
          quantity: 1
        })
      });
      
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Could not add to cart.');
      }
      
      // Dispatch custom cart event to notify navbar count
      window.dispatchEvent(new Event('cartUpdated'));
      
      // Show success animation
      setSuccessId(medicine.id);
      setTimeout(() => setSuccessId(null), 2000);
    } catch (err) {
      alert(err.message);
    } finally {
      setAddingId(null);
    }
  };

  return (
    <div>
      <div style={{ marginBottom: '2.5rem', textAlign: 'center' }}>
        <h1 style={{ fontSize: '2.5rem', fontFamily: 'var(--font-display)', fontWeight: 800, marginBottom: '0.5rem', background: 'linear-gradient(135deg, #ffffff 60%, var(--accent-primary) 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
          Medicine Catalogue
        </h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '1.1rem' }}>
          Search and order certified medicines with fast delivery check.
        </p>
      </div>

      <form onSubmit={handleSearchSubmit} className="search-header">
        <div className="search-box-container">
          <Search size={20} className="search-icon" />
          <input 
            type="text" 
            className="form-control search-input" 
            placeholder="Search by medicine name or salt composition (e.g. Paracetamol, Ibuprofen)..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <button type="submit" className="btn btn-primary" style={{ padding: '0.75rem 2rem' }}>
          Search
        </button>
      </form>

      {loading ? (
        <div style={{ display: 'flex', justifyContent: 'center', padding: '4rem' }}>
          <div style={{ width: '40px', height: '40px', border: '3px solid rgba(255,255,255,0.1)', borderTopColor: 'var(--accent-primary)', borderRadius: '50%', animation: 'pulseGlow 1s infinite linear' }}></div>
        </div>
      ) : error ? (
        <div className="error-banner" style={{ maxWidth: '600px', margin: '2rem auto' }}>
          <AlertTriangle size={18} />
          <span>{error}</span>
        </div>
      ) : medicines.length === 0 ? (
        <div className="glass-card" style={{ textAlign: 'center', padding: '4rem 2rem', borderStyle: 'dashed' }}>
          <Info size={48} className="accent-secondary" style={{ marginBottom: '1rem', opacity: 0.5 }} />
          <h3>No Medicines Found</h3>
          <p style={{ color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
            We couldn't find anything matching "{searchQuery}". Try adjusting your keywords.
          </p>
        </div>
      ) : (
        <div className="medicines-grid">
          {medicines.map((med) => {
            // Calculate saving percent
            const savings = med.mrp > med.selling_price 
              ? Math.round(((med.mrp - med.selling_price) / med.mrp) * 100)
              : 0;
            
            const isOOS = med.stock <= 0;
            const isLowStock = med.stock > 0 && med.stock < 10;
            
            return (
              <div key={med.id} className="glass-card medicine-card">
                <div>
                  <div className="medicine-header">
                    <span className={med.prescription_required ? "badge-prescription" : "badge-otc"}>
                      {med.prescription_required ? "Rx Required" : "OTC"}
                    </span>
                    <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                      ID: #{med.id}
                    </span>
                  </div>

                  <h3 className="medicine-title">{med.name}</h3>
                  <div className="salt-composition">{med.salt_composition}</div>
                  
                  <div className="stock-indicator">
                    <span className={`stock-dot ${isOOS ? 'oos' : isLowStock ? 'low-stock' : 'in-stock'}`}></span>
                    <span style={{ color: isOOS ? '#ef4444' : isLowStock ? '#f59e0b' : 'var(--accent-primary)', fontWeight: 600 }}>
                      {isOOS ? 'Out of Stock' : isLowStock ? `Low Stock (Only ${med.stock} left)` : 'In Stock'}
                    </span>
                  </div>
                </div>

                <div>
                  <div className="pricing-section">
                    <span className="selling-price">₹{med.selling_price}</span>
                    {med.mrp > med.selling_price && (
                      <>
                        <span className="mrp-price">M.R.P. ₹{med.mrp}</span>
                        <span className="discount-tag">{savings}% OFF</span>
                      </>
                    )}
                  </div>

                  <button 
                    onClick={() => handleAddToCart(med)}
                    className="btn btn-primary"
                    style={{ 
                      width: '100%', 
                      background: isOOS 
                        ? 'rgba(255,255,255,0.05)' 
                        : successId === med.id 
                          ? '#10b981' 
                          : 'linear-gradient(135deg, var(--accent-primary), var(--accent-primary-hover))',
                      color: isOOS ? 'var(--text-muted)' : 'var(--bg-base)',
                      border: isOOS ? '1px solid var(--border-glass)' : 'none'
                    }}
                    disabled={isOOS || addingId === med.id}
                  >
                    {isOOS ? (
                      'Out of Stock'
                    ) : successId === med.id ? (
                      <>
                        <CheckCircle size={16} />
                        <span>Added to Cart</span>
                      </>
                    ) : addingId === med.id ? (
                      'Adding...'
                    ) : (
                      <>
                        <Plus size={16} />
                        <span>Add to Cart</span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default MedicineListing;
