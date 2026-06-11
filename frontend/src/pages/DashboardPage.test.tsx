import { screen } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { api } from '../api/client'
import type { Money } from '../api/types'
import { renderWithProviders } from '../test/utils'
import { DashboardPage } from './DashboardPage'

vi.mock('../api/client', () => ({
  api: {
    getSummary: vi.fn(),
    getByCountry: vi.fn(),
    getByDepartment: vi.fn(),
    getDistribution: vi.fn(),
  },
}))

const mockApi = vi.mocked(api)

function money(amount: string, formatted: string): Money {
  return { minor: Math.round(Number(amount) * 100), currency: 'USD', amount, formatted }
}

beforeEach(() => {
  vi.clearAllMocks()
  mockApi.getSummary.mockResolvedValue({
    base_currency: 'USD',
    headcount: 9659,
    total_payroll: money('917438805.79', '917,438,805.79 USD'),
    average_salary: money('94982.79', '94,982.79 USD'),
    median_salary: money('73672.50', '73,672.50 USD'),
  })
  mockApi.getByCountry.mockResolvedValue({
    base_currency: 'USD',
    groups: [
      {
        key: 'US',
        label: 'United States',
        headcount: 2860,
        total: money('350000000', '...'),
        average: money('122604.31', '122,604.31 USD'),
        median: money('97510.00', '97,510.00 USD'),
      },
    ],
  })
  mockApi.getByDepartment.mockResolvedValue({
    base_currency: 'USD',
    groups: [
      {
        key: '1',
        label: 'Engineering',
        headcount: 3400,
        total: money('400000000', '...'),
        average: money('118000.00', '118,000.00 USD'),
        median: money('95000.00', '95,000.00 USD'),
      },
    ],
  })
  mockApi.getDistribution.mockResolvedValue({
    base_currency: 'USD',
    percentiles: { p50: money('73672.50', '73,672.50 USD') },
    bands: [
      {
        level: 1,
        headcount: 1922,
        min: money('21062.25', '21,062.25 USD'),
        median: money('47896.20', '47,896.20 USD'),
        max: money('63239.00', '63,239.00 USD'),
      },
    ],
  })
})

describe('DashboardPage', () => {
  it('shows summary stat cards', async () => {
    renderWithProviders(<DashboardPage />)

    expect(await screen.findByText('9,659')).toBeInTheDocument()
    expect(screen.getByText('917,438,805.79 USD')).toBeInTheDocument()
    // Median appears both as a stat card and as the p50 percentile.
    expect(screen.getAllByText('73,672.50 USD').length).toBeGreaterThan(0)
  })

  it('renders the percentile breakdown', async () => {
    renderWithProviders(<DashboardPage />)

    expect(await screen.findByText('p50')).toBeInTheDocument()
  })

  it('renders the by-country and by-department breakdowns', async () => {
    renderWithProviders(<DashboardPage />)

    expect(await screen.findByText('Pay by country (USD)')).toBeInTheDocument()
    expect(screen.getByText('Pay by department (USD)')).toBeInTheDocument()
  })
})
