import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import Checkout from '../src/pages/Checkout';
import { AuthProvider } from '../src/context/AuthContext';

// Mock the AuthContext fetch operations
vi.mock('../src/context/AuthContext', async () => {
  const actual = await vi.importActual('../src/context/AuthContext');
  return {
    ...actual,
    useAuth: () => ({
      authFetch: async (url, options = {}) => {
        // Handle initial cart check to make sure it doesn't redirect
        if (url === '/cart') {
          return {
            ok: true,
            json: async () => ({
              items: [
                {
                  id: 1,
                  quantity: 1,
                  medicine: { id: 1, name: "Paracetamol", selling_price: 15.00, stock: 10 }
                }
              ]
            })
          };
        }
        
        // Handle serviceability check POST
        if (url === '/serviceability/check' && options.method === 'POST') {
          const body = JSON.parse(options.body);
          if (body.distance <= 5000) {
            return {
              ok: true,
              json: async () => ({
                serviceable: true,
                distance: body.distance,
                estimated_delivery_minutes: body.distance <= 2000 ? 30 : 45,
                message: "Store is serviceable."
              })
            };
          } else {
            return {
              ok: true,
              json: async () => ({
                serviceable: false,
                distance: body.distance,
                estimated_delivery_minutes: null,
                message: "Store is unserviceable. Distance exceeds maximum limit."
              })
            };
          }
        }
        
        // Return blank fallback for any other requests
        return { ok: true, json: async () => ({}) };
      }
    })
  };
});

describe('Checkout Serviceability Verification', () => {
  it('correctly handles inputs and displays serviceable or unserviceable results', async () => {
    render(
      <BrowserRouter>
        <AuthProvider>
          <Checkout />
        </AuthProvider>
      </BrowserRouter>
    );

    // Get input fields
    const pincodeInput = screen.getByPlaceholderText('e.g. 560001');
    const distanceInput = screen.getByPlaceholderText('e.g. 1500');
    const submitBtn = screen.getByRole('button', { name: /check serviceability/i });

    // 1. Test Serviceable input
    fireEvent.change(pincodeInput, { target: { value: '560001' } });
    fireEvent.change(distanceInput, { target: { value: '1500' } });
    fireEvent.click(submitBtn);

    // Wait and assert serviceable message appears
    await waitFor(() => {
      expect(screen.getByText(/serviceable!/i)).toBeInTheDocument();
      expect(screen.getByText(/store is serviceable/i)).toBeInTheDocument();
    });

    // 2. Test Unserviceable input
    fireEvent.change(distanceInput, { target: { value: '6000' } });
    fireEvent.click(submitBtn);

    // Wait and assert unserviceable message appears
    await waitFor(() => {
      expect(screen.getByText(/unserviceable\./i, { selector: 'strong' })).toBeInTheDocument();
      expect(screen.getByText(/exceeds maximum limit/i)).toBeInTheDocument();
    });
  });
});
