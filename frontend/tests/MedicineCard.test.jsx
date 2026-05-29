import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import MedicineListing from '../src/pages/MedicineListing';
import { AuthProvider } from '../src/context/AuthContext';

// Mock the AuthContext fetch operations
vi.mock('../src/context/AuthContext', async () => {
  const actual = await vi.importActual('../src/context/AuthContext');
  return {
    ...actual,
    useAuth: () => ({
      authFetch: async (url) => {
        // Return structured mocked catalog
        return {
          ok: true,
          json: async () => [
            {
              id: 10,
              name: "OOS Med 150mg",
              salt_composition: "Mock Salt",
              mrp: 20.00,
              selling_price: 15.00,
              stock: 0, // OUT OF STOCK
              prescription_required: false
            }
          ]
        };
      }
    })
  };
});

describe('MedicineListing Catalog Stock Checks', () => {
  it('disables the Add to Cart button for out-of-stock items', async () => {
    render(
      <AuthProvider>
        <MedicineListing />
      </AuthProvider>
    );

    // Wait for the mock medicines to render
    const btn = await screen.findByRole('button', { name: /out of stock/i });
    
    // Assert disabled state and proper text representation
    expect(btn).toBeInTheDocument();
    expect(btn).toBeDisabled();
  });
});
