import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { api } from '../api/client'
import type { Employee } from '../api/types'
import { renderWithProviders } from '../test/utils'
import { EmployeeFormModal } from './EmployeeFormModal'

vi.mock('../api/client', () => ({
  api: {
    getCountries: vi.fn(),
    getDepartments: vi.fn(),
    createEmployee: vi.fn(),
    updateEmployee: vi.fn(),
  },
}))

const mockApi = vi.mocked(api)

function makeEmployee(): Employee {
  return {
    id: 7,
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
    current_salary: { minor: 15000000, currency: 'USD', amount: '150000', formatted: '150,000.00 USD' },
    salary_in_base: { minor: 15000000, currency: 'USD', amount: '150000', formatted: '150,000.00 USD' },
  }
}

beforeEach(() => {
  vi.clearAllMocks()
  mockApi.getCountries.mockResolvedValue([{ code: 'US', name: 'United States', currency: 'USD' }])
  mockApi.getDepartments.mockResolvedValue([{ id: 1, name: 'Engineering' }])
  mockApi.updateEmployee.mockResolvedValue(makeEmployee())
})

describe('EmployeeFormModal', () => {
  it('submits an update for an existing employee', async () => {
    renderWithProviders(
      <EmployeeFormModal opened employee={makeEmployee()} onClose={() => {}} />,
    )

    // Prefilled from the employee.
    expect(await screen.findByDisplayValue('Ada')).toBeInTheDocument()

    await userEvent.click(screen.getByRole('button', { name: 'Save' }))

    await waitFor(() => {
      expect(mockApi.updateEmployee).toHaveBeenCalledWith(
        7,
        expect.objectContaining({ first_name: 'Ada', role: 'Senior Engineering', salary: '150000' }),
      )
    })
  })

  it('validates required fields when creating', async () => {
    renderWithProviders(<EmployeeFormModal opened employee={null} onClose={() => {}} />)

    await userEvent.click(screen.getByRole('button', { name: 'Create' }))

    expect(await screen.findAllByText('Required')).not.toHaveLength(0)
    expect(mockApi.createEmployee).not.toHaveBeenCalled()
  })
})
