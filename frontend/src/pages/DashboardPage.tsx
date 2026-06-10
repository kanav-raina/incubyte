import type { ReactNode } from 'react'
import { Grid, Paper, SimpleGrid, Stack, Text, Title } from '@mantine/core'
import { IconCash, IconChartBar, IconScale, IconUsers } from '@tabler/icons-react'
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { useByCountry, useDistribution, useSummary } from '../api/hooks'
import { QueryState } from '../components/QueryState'
import { StatCard } from '../components/StatCard'
import { compactCurrency, currencyFormatter, toNumber } from '../utils/format'

function ChartCard({ title, children }: { title: string; children: ReactNode }) {
  return (
    <Paper withBorder p="md" radius="md" h="100%">
      <Text fw={600} mb="md">
        {title}
      </Text>
      {children}
    </Paper>
  )
}

export function DashboardPage() {
  const summary = useSummary()
  const byCountry = useByCountry()
  const distribution = useDistribution()

  const isLoading = summary.isLoading || byCountry.isLoading || distribution.isLoading
  const error = summary.error || byCountry.error || distribution.error

  const baseCurrency = summary.data?.base_currency ?? 'USD'
  const fmt = currencyFormatter(baseCurrency)

  const countryData = (byCountry.data?.groups ?? []).map((g) => ({
    name: g.key,
    average: toNumber(g.average.amount),
    median: toNumber(g.median?.amount),
  }))

  const bandData = (distribution.data?.bands ?? []).map((b) => ({
    level: `L${b.level}`,
    min: toNumber(b.min.amount),
    median: toNumber(b.median?.amount),
    max: toNumber(b.max.amount),
  }))

  const percentiles = Object.entries(distribution.data?.percentiles ?? {})

  return (
    <Stack>
      <Title order={2}>Dashboard</Title>

      <QueryState isLoading={isLoading} error={error}>
        {summary.data && (
          <SimpleGrid cols={{ base: 1, sm: 2, lg: 4 }}>
            <StatCard
              label="Headcount"
              value={summary.data.headcount.toLocaleString()}
              icon={IconUsers}
              color="blue"
            />
            <StatCard
              label="Total payroll"
              value={summary.data.total_payroll.formatted}
              icon={IconCash}
              color="teal"
            />
            <StatCard
              label="Average salary"
              value={summary.data.average_salary.formatted}
              icon={IconChartBar}
              color="grape"
            />
            <StatCard
              label="Median salary"
              value={summary.data.median_salary?.formatted ?? '—'}
              icon={IconScale}
              color="orange"
            />
          </SimpleGrid>
        )}

        <Grid mt="xs">
          <Grid.Col span={{ base: 12, md: 7 }}>
            <ChartCard title={`Pay by country (${baseCurrency})`}>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={countryData}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} />
                  <XAxis dataKey="name" />
                  <YAxis tickFormatter={compactCurrency} width={60} />
                  <Tooltip formatter={(value) => fmt(Number(value))} />
                  <Legend />
                  <Bar dataKey="average" name="Average" fill="#7950f2" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="median" name="Median" fill="#15aabf" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </ChartCard>
          </Grid.Col>

          <Grid.Col span={{ base: 12, md: 5 }}>
            <ChartCard title="Pay distribution (percentiles)">
              <SimpleGrid cols={2}>
                {percentiles.map(([label, money]) => (
                  <Paper key={label} withBorder p="sm" radius="md">
                    <Text size="xs" c="dimmed" tt="uppercase" fw={600}>
                      {label}
                    </Text>
                    <Text fw={700}>{money.formatted}</Text>
                  </Paper>
                ))}
              </SimpleGrid>
            </ChartCard>
          </Grid.Col>
        </Grid>

        <ChartCard title={`Compensation bands by level (${baseCurrency})`}>
          <ResponsiveContainer width="100%" height={320}>
            <BarChart data={bandData}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="level" />
              <YAxis tickFormatter={compactCurrency} width={60} />
              <Tooltip formatter={(value) => fmt(Number(value))} />
              <Legend />
              <Bar dataKey="min" name="Min" fill="#a5d8ff" radius={[4, 4, 0, 0]} />
              <Bar dataKey="median" name="Median" fill="#4dabf7" radius={[4, 4, 0, 0]} />
              <Bar dataKey="max" name="Max" fill="#1971c2" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </QueryState>
    </Stack>
  )
}
