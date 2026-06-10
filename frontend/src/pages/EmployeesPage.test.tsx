import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { api } from '../api/client'
import type { Employee, Page } from '../api/types'
import { renderWithProviders } from '../test/utils'
import { EmployeesPage } from './EmployeesPage'

vi.mock('../api/client', () => ({
  api: {
    listEmployees: vi.fn(),
    getCountries: vi.fn(),
    getDepartments: vi.fn(),
  },
}))

const mockApi = vi.mocked(api)

function makeEmployee(overrides: Partial<Employee> = {}): Employee {
  return {
    id: 1,
    first_name: 'Ada',
    last_name: 'Lovelace',
    email: 'ada@acme.example',
    country: { code: 'US', name: 'United States', currency: 'USD' },
    department: { id: 1, name: 'Engineering' },
    role: 'Senior Engineering',
    level: 4,
    hire_date: '2024-01-01',
    status: 'active',
    manager_id: null,
    current_salary: { minor: 15000000, currency: 'USD', amount: '150000.00', formatted: '150,000.00 USD' },
    salary_in_base: { minor: 15000000, currency: 'USD', amount: '150000.00', formatted: '150,000.00 USD' },
    ...overrides,
  }
}

function makePage(items: Employee[]): Page<Employee> {
  return { items, total: items.length, page: 1, page_size: 25 }
}

beforeEach(() => {
  vi.clearAllMocks()
  mockApi.getCountries.mockResolvedValue([{ code: 'US', name: 'United States', currency: 'USD' }])
  mockApi.getDepartments.mockResolvedValue([{ id: 1, name: 'Engineering' }])
  mockApi.listEmployees.mockResolvedValue(makePage([makeEmployee()]))
})

describe('EmployeesPage', () => {
  it('renders employees returned by the API', async () => {
    renderWithProviders(<EmployeesPage />)

    expect(await screen.findByText('Ada Lovelace')).toBeInTheDocument()
    expect(screen.getAllByText('150,000.00 USD').length).toBeGreaterThan(0)
  })

  it('passes the debounced search term to the API', async () => {
    renderWithProviders(<EmployeesPage />)
    await screen.findByText('Ada Lovelace')

    await userEvent.type(screen.getByLabelText('Search'), 'zel')

    await waitFor(() => {
      expect(mockApi.listEmployees).toHaveBeenLastCalledWith(
        expect.objectContaining({ q: 'zel', page: 1 }),
      )
    })
  })

  it('shows an empty state when there are no results', async () => {
    mockApi.listEmployees.mockResolvedValue(makePage([]))
    renderWithProviders(<EmployeesPage />)

    expect(await screen.findByText('No employees match these filters.')).toBeInTheDocument()
  })
})
