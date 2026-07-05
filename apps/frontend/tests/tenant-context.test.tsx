import { describe, expect, it, vi } from 'vitest';
import { renderHook } from '@testing-library/react';
import { useTenant } from '@/lib/context/tenant-context';

const mockUseParams = vi.fn();

vi.mock('next/navigation', () => ({
  useParams: () => mockUseParams(),
}));

describe('useTenant', () => {
  it('returns the locale route param when it is a supported language', () => {
    mockUseParams.mockReturnValue({ locale: 'fr' });
    const { result } = renderHook(() => useTenant());
    expect(result.current).toBe('fr');
  });

  it('falls back to the default locale for an unsupported/missing param', () => {
    mockUseParams.mockReturnValue({ locale: 'xx' });
    const { result: bogus } = renderHook(() => useTenant());
    expect(bogus.current).toBe('en');

    mockUseParams.mockReturnValue({});
    const { result: missing } = renderHook(() => useTenant());
    expect(missing.current).toBe('en');
  });
});
