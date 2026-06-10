import { screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import App from './App'
import { renderWithProviders } from './test/utils'

describe('App', () => {
  it('renders the app shell with the product title', () => {
    renderWithProviders(<App />)
    expect(screen.getByText('Salary Management')).toBeInTheDocument()
  })

  it('shows the dashboard on the index route', () => {
    renderWithProviders(<App />, { route: '/' })
    expect(screen.getByRole('heading', { name: 'Dashboard' })).toBeInTheDocument()
  })
})
