<template>
  <Panel
    :pt="panelStyles"
    header="Relevance Discovery Curve"
  >
    <Chart
      type="line"
      :data="chartData"
      :options="chartOptions"
      class="tw-h-[13rem]"
    />
  </Panel>
</template>

<script lang="ts" setup>
import Panel from 'primevue/panel'
import Chart from 'primevue/chart'
import { computed } from 'vue'
import { IRelevanceDiscoveryCurve } from '@/types/statistic'

const props = defineProps<{
  data: IRelevanceDiscoveryCurve
}>()

const chartData = computed(() => {
  return {
    labels: props.data['x-axis'].value,
    datasets: [
      {
        data: props.data['y-axis'].value,
        fill: false,
        borderColor: '#8B5CF6',
        tension: 0.4,
      },
    ],
  }
})

const chartOptions = computed(() => {
  const documentStyle = getComputedStyle(document.documentElement)
  const textColorSecondary = documentStyle.getPropertyValue(
    '--text-color-secondary',
  )
  const surfaceBorder = documentStyle.getPropertyValue('--surface-border')

  return {
    maintainAspectRatio: false,
    aspectRatio: 0.6,
    plugins: {
      legend: {
        display: false,
      },
    },
    scales: {
      x: {
        ticks: {
          color: textColorSecondary,
        },
        grid: {
          color: surfaceBorder,
        },
        title: {
          display: true,
          text: 'No. of Reviewed Studies',
        },
      },
      y: {
        ticks: {
          color: textColorSecondary,
          callback: (value: number) => Math.floor(value).toString(),
        },
        grid: {
          color: surfaceBorder,
        },
        title: {
          display: true,
          text: 'No. of Relevant Studies',
        },
      },
    },
  }
})

const panelStyles = {
  header: 'tw-py-2',
  content: 'tw-pb-0 tw-p-2',
}
</script>
