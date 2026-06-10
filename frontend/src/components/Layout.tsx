import { AppShell, Group, NavLink as MantineNavLink, Title } from '@mantine/core'
import { IconChartBar, IconUsers } from '@tabler/icons-react'
import { Link, Outlet, useLocation } from 'react-router-dom'

const NAV_ITEMS = [
  { label: 'Dashboard', to: '/', icon: IconChartBar },
  { label: 'Employees', to: '/employees', icon: IconUsers },
]

export function Layout() {
  const { pathname } = useLocation()

  const isActive = (to: string) => (to === '/' ? pathname === '/' : pathname.startsWith(to))

  return (
    <AppShell header={{ height: 56 }} navbar={{ width: 220, breakpoint: 'xs' }} padding="md">
      <AppShell.Header>
        <Group h="100%" px="md">
          <Title order={4}>Salary Management</Title>
        </Group>
      </AppShell.Header>

      <AppShell.Navbar p="sm">
        {NAV_ITEMS.map((item) => (
          <MantineNavLink
            key={item.to}
            component={Link}
            to={item.to}
            label={item.label}
            leftSection={<item.icon size={18} />}
            active={isActive(item.to)}
          />
        ))}
      </AppShell.Navbar>

      <AppShell.Main>
        <Outlet />
      </AppShell.Main>
    </AppShell>
  )
}
