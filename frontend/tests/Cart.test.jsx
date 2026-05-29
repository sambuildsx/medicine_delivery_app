import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import Cart from '../src/pages/Cart';
import { AuthProvider } from '../src/context/AuthContext';

// Mock the AuthContext fetch operations
vi.mock('../src/context/AuthContext', async () => {
  const actual = await vi.importActual('../src/context/AuthContext');
  return {
    ...actual,
    useAuth: () => ({
      authFetch: async (url) => {
        // Return standard mocked cart structure
        return {
          ok: true,
          json: async () => ({
            items: [
              {
                id: 101,
                quantity: 1,
                medicine: {
                  id: 1,
                  name: "Paracetamol 500mg",
                  salt_composition: "Paracetamol",
                  mrp: 20.00,
                  selling_price: 100.00, // selling_price matching total calculations
                  stock: 10,
                  prescription_required: false
                }
              }
            ],
            item_total: 100.00,
            discount_amount: 20.00,
            small_cart_fee: 29.00,
            delivery_fee: 0.00, // delivery fee is calculated at checkout
            late_night_fee: 25.00,
            total_payable: 134.00, // 100 - 20 + 29 + 25
            coupon_applied: "MOCKCODE"
          })
        };
      }
    })
  };
});

describe('Cart Billing Calculations Render', () => {
  it('correctly calculates and displays items total, discounts, cart fees, and payable sums', async () => {
    render(
      <BrowserRouter>
        <AuthProvider>
          <Cart />
        </AuthProvider>
      </BrowserRouter>
    );

    // Assert items total
    const itemTotalEls = await screen.findAllByText('₹100.00');
    expect(itemTotalEls.length).toBeGreaterThanOrEqual(1);

    // Assert coupon discount
    const discountEl = await screen.findByText('-₹20.00');
    expect(discountEl).toBeInTheDocument();

    // Assert small cart fee
    const smallCartEl = await screen.findByText('₹29.00');
    expect(smallCartEl).toBeInTheDocument();

    // Assert late night surcharge
    const lateNightEl = await screen.findByText('₹25.00');
    expect(lateNightEl).toBeInTheDocument();

    // Assert final payable sum
    const totalPayableEl = await screen.findByText('₹134.00');
    expect(totalPayableEl).toBeInTheDocument();
  });
});
