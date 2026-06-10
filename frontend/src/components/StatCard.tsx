import { Group, Paper, Text, ThemeIcon } from '@mantine/core'
import type { Icon } from '@tabler/icons-react'

interface StatCardProps {
  label: string
  value: string
  icon: Icon
  color?: string
}

export function StatCard({ label, value, icon: IconComponent, color = 'blue' }: StatCardProps) {
  return (
    <Paper withBorder p="md" radius="md">
      <Group justify="space-between" wrap="nowrap">
        <div>
          <Text size="xs" c="dimmed" tt="uppercase" fw={600}>
            {label}
          </Text>
          <Text size="xl" fw={700} mt={4}>
            {value}
          </Text>
        </div>
        <ThemeIcon color={color} variant="light" size={42} radius="md">
          <IconComponent size={24} />
        </ThemeIcon>
      </Group>
    </Paper>
  )
}
