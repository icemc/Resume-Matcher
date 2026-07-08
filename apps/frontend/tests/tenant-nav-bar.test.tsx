import { describe, expect, it, vi, beforeEach, afterEach } from 'vitest';
import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { TenantNavBar } from '@/components/tenant/tenant-nav-bar';

const push = vi.fn();

vi.mock('next/navigation', () => ({
  useRouter: () => ({ push }),
  useParams: () => ({ locale: 'en' }),
}));

vi.mock('@/lib/i18n', () => ({
  useTranslations: () => ({ t: (key: string) => key }),
}));

describe('TenantNavBar', () => {
  let fetchMock: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    push.mockClear();
    fetchMock = vi
      .fn()
      .mockResolvedValue(new Response(JSON.stringify({ languages: ['en'] }), { status: 200 }));
    vi.stubGlobal('fetch', fetchMock);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('marks the configured tenant and the unconfigured ones distinctly', async () => {
    render(<TenantNavBar />);

    fireEvent.click(screen.getByRole('button', { expanded: false }));

    const menu = await screen.findByRole('menu');
    await waitFor(() => {
      expect(within(menu).getAllByText('tenantSwitcher.configured')).toHaveLength(1);
    });
    // The other five supported languages are not yet configured.
    expect(within(menu).getAllByText('tenantSwitcher.setUp')).toHaveLength(5);
  });

  it('navigates to the selected tenant dashboard', async () => {
    render(<TenantNavBar />);

    fireEvent.click(screen.getByRole('button', { expanded: false }));
    await waitFor(() => screen.getByText('🇫🇷 Français'));

    fireEvent.click(screen.getByText('🇫🇷 Français').closest('button')!);

    expect(push).toHaveBeenCalledWith('/fr/dashboard');
  });
});
