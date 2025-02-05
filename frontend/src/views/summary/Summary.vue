<template>
  <LoadingScreen v-if="isLoading" class="tw-h-[86vh]" />
  <Container v-else>
    <div class="tw-flex tw-flex-col tw-gap-6">
      <p class="tw-text-2xl tw-font-bold tw-text-center">
        {{ review.dataset_name }}
      </p>
      <div
        class="tw-flex tw-justify-between tw-items-center tw-gap-4 tw-relative"
      >
        <ScreeningProgressPanel
          :items="items"
          :active-step="2"
        />
      </div>

      <QueryPanel :pico-query="review.query_pannel" />

      <div
        class="tw-flex tw-flex-col tw-gap-6 tw-bg-primary-50 tw-p-8 tw-rounded border"
      >
        <p class="tw-text-2xl tw-font-medium tw-text-center">
          You have finished your screening
        </p>

        <Panel :pt="{ header: 'tw-py-3' }">
          <template #header>
            <div class="tw-mx-auto">
              <h3>Overall</h3>
            </div>
          </template>

          <div class="tw-flex tw-items-center">
            <div class="tw-flex tw-flex-col tw-gap-2 tw-w-1/3 tw-items-center">
              <div class="tw-flex">
                <div class="tw-w-[11.5rem] tw-mr-2 tw-text-right">
                  <p>Reviewed:</p>
                </div>
                <p
                  class="tw-font-bold tw-bg-primary-200 tw-w-[2rem] tw-text-center tw-rounded"
                >
                  {{ review.dashboard_data.reviewed }}
                </p>
              </div>
              <div class="tw-flex">
                <div class="tw-w-[11.5rem] tw-mr-2 tw-text-right">
                  <p>Include:</p>
                </div>
                <p
                  class="tw-font-bold tw-bg-green-200 tw-w-[2rem] tw-text-center tw-rounded"
                >
                  {{ review.dashboard_data.include }}
                </p>
              </div>
              <div class="tw-flex">
                <div class="tw-w-[11.5rem] tw-mr-2 tw-text-right">
                  <p>Exclude:</p>
                </div>
                <p
                  class="tw-font-bold tw-bg-red-200 tw-w-[2rem] tw-text-center tw-rounded"
                >
                  {{ review.dashboard_data.exclude }}
                </p>
              </div>
              <div class="tw-flex">
                <div class="tw-w-[11.5rem] tw-mr-2 tw-text-right">
                  <p>Maybe:</p>
                </div>
                <p
                  class="tw-font-bold tw-bg-gray-200 tw-w-[2rem] tw-text-center tw-rounded"
                >
                  {{ review.dashboard_data.maybe }}
                </p>
              </div>
            </div>

            <div class="tw-w-1/3 tw-flex tw-flex-col tw-items-center">
              <Chart
                type="pie"
                :data="chartData"
                :options="chartOptions"
                class="w-full md:w-30rem"
              />
            </div>
          </div>
        </Panel>

        <div class="tw-flex tw-flex-col tw-gap-2">
          <p class="tw-text-2xl tw-font-bold">A list of studies</p>
          <div class="tw-justify-between tw-flex">
            <div class="tw-items-center tw-flex tw-gap-1">
              <CustomButton
                icon="pi pi-file-export"
                label="Export selected"
                outlined
                @click="exportReview()"
              />
              <span>.nbib</span>
            </div>
            <div class="tw-items-center tw-flex tw-gap-2">
              <CustomButton
                label="All"
                :outlined="!filters.all"
                @click="toggleFilter('all')"
              />
              <CustomButton
                label="Include"
                :outlined="!filters.include"
                severity="success"
                @click="toggleFilter('include')"
              />
              <CustomButton
                label="Maybe"
                :outlined="!filters.maybe"
                severity="secondary"
                @click="toggleFilter('maybe')"
              />
              <CustomButton
                label="Exclude"
                :outlined="!filters.exclude"
                severity="danger"
                @click="toggleFilter('exclude')"
              />
            </div>
          </div>
        </div>

        <DataTable
          :value="screeningPannel"
          showGridlines
          stripedRows
        >
          <Column>
            <template #header>
              <p class="tw-m-auto tw-text-center">Order</p>
            </template>
            <template #body="slotProps">
              <p class="tw-text-center">{{ slotProps.index + 1 }}</p>
            </template>
          </Column>
          <Column>
            <template #header>
              <p class="tw-m-auto tw-text-center">PMID</p>
            </template>
            <template #body="slotProps">
              <p class="tw-text-center">{{ slotProps.data.pmid }}</p>
            </template>
          </Column>
          <Column>
            <template #header>
              <p class="tw-m-auto tw-text-center">Title</p>
            </template>
            <template #body="slotProps">
              {{ slotProps.data.corpus.title }}
            </template>
          </Column>
          <Column>
            <template #header>
              <p class="tw-m-auto tw-text-center">Assessment</p>
            </template>
            <template #body="slotProps">
              <p
                class="tw-text-center tw-rounded tw-font-medium"
                :class="{
                  'tw-bg-green-200': slotProps.data.feedback === 'include',
                  'tw-bg-red-200': slotProps.data.feedback === 'exclude',
                  'tw-bg-gray-200': slotProps.data.feedback === 'maybe',
                }"
              >
                {{ toTitleCase(slotProps.data.feedback) }}
              </p>
            </template>
          </Column>
        </DataTable>
      </div>
    </div>
  </Container>
</template>

<script lang="ts" setup>
import axios, { AxiosError } from 'axios'
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { getTokenHeader } from '@/utils/auth'
import { useError } from '@/composables/error'
import { useToast } from '@/composables/toast'
import { useLoading } from '@/composables/loading'
import { toTitleCase } from '@/utils/string'
import { IDoc, IReview } from '@/types/corpus'
import { DEFAULT_REVIEW } from '@/defaults/corpus'

import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import LoadingScreen from '@/components/LoadingScreen.vue'
import Container from '@/components/Container.vue'
import CustomButton from '@/components/CustomButton.vue'
import QueryPanel from '../review/components/QueryPanel.vue'
import ScreeningProgressPanel from '../review/components/ScreeningProgressPanel.vue'
import Panel from 'primevue/panel'
import Chart from 'primevue/chart'

const route = useRoute()
const { getResponseErrorMessage } = useError()
const { showToast } = useToast()
const { isLoading, setLoading } = useLoading(false)

import startIcon from '@/assets/icons/start.png'
import reviewIcon from '@/assets/icons/review.png'
import finishedIcon from '@/assets/icons/flag.png'

const items = ref([
  {
    label: 'Started',
    icon: startIcon,
  },
  {
    label: 'Reviewing',
    icon: reviewIcon,
  },
  {
    label: 'Finished',
    icon: finishedIcon,
  },
])

const review = ref<IReview>(DEFAULT_REVIEW)
const screeningPannel = ref<IDoc[]>(review.value.screening_pannel)
const filters = ref({ all: true, include: false, maybe: false, exclude: false })

function toggleFilter(filter: string): void {
  filters.value[filter as keyof typeof filters.value] =
    !filters.value[filter as keyof typeof filters.value]
  if (filter === 'all') {
    filters.value = { all: true, include: false, maybe: false, exclude: false }
  } else {
    filters.value.all = false
    const activeFilters = Object.keys(filters.value).filter(
      (key) =>
        filters.value[key as keyof typeof filters.value] && key !== 'all',
    )
    const inactiveFilters = Object.keys(filters.value).filter(
      (key) =>
        !filters.value[key as keyof typeof filters.value] && key !== 'all',
    )
    if (activeFilters.length === 3 || inactiveFilters.length === 3)
      filters.value = {
        all: true,
        include: false,
        maybe: false,
        exclude: false,
      }
  }
  applyFilters()
}

function applyFilters(): void {
  const activeFilters = Object.keys(filters.value).filter(
    (key) => filters.value[key as keyof typeof filters.value] && key !== 'all',
  )
  screeningPannel.value = activeFilters.length
    ? review.value.screening_pannel.filter((item) =>
        activeFilters.includes(item.feedback),
      )
    : review.value.screening_pannel
}

const exportReview = async () => {
  try {
    const judgementArray = filters.value.all
      ? ['include', 'maybe', 'exclude']
      : ['include', 'maybe', 'exclude'].filter(
          (judgment) => filters.value[judgment as keyof typeof filters.value],
        )
    const body = {
      review_id: route.params.id,
      page_index: route.query.index,
      judgment_type: judgementArray,
      export_data: screeningPannel.value,
    }
    const result = await axios.post(
      '/encoder/export_review',
      body,
      getTokenHeader(),
    )

    const link = document.createElement('a')
    link.href = result.data.url
    link.click()
  } catch (error) {
    console.error(error)
    if (error instanceof AxiosError) {
      const e = getResponseErrorMessage(error)
      showToast('error', 'Cannot Export Data', e.message)
    } else if (error instanceof Error) {
      showToast('error', 'Cannot Export Data', error.message)
    } else {
      showToast('error', 'Cannot Export Data', 'An error occurred')
    }
  }
}

const stopReview = async () => {
  try {
    setLoading(true)
    // Make the request
    const headers = {
      'Content-Type': 'multipart/form-data',
      ...getTokenHeader(),
    }
    const formData = new FormData()
    formData.append('review_id', String(route.params.id))
    formData.append('page_index', String(route.query.index))
    formData.append('is_finished', '1')
    const result = await axios.post(
      'encoder/review_progress',
      formData,
      headers,
    )
    review.value = result.data.data
    screeningPannel.value = review.value.screening_pannel
  } catch (error) {
    console.error(error)
    if (error instanceof AxiosError) {
      const e = getResponseErrorMessage(error)
      showToast('error', 'Cannot Fetch Review Data', e.message)
    } else if (error instanceof Error) {
      showToast('error', 'Cannot Fetch Review Data', error.message)
    } else {
      showToast('error', 'Cannot Fetch Review Data', 'An error occurred')
    }
  } finally {
    setLoading(false)
  }
}

onMounted(async () => {
  await stopReview()
  chartData.value = setChartData()
  chartOptions.value = setChartOptions()
})

const chartData = ref()
const chartOptions = ref()

const setChartData = () => {
  const documentStyle = getComputedStyle(document.body)

  return {
    labels: ['Include', 'Maybe', 'Exclude'],
    datasets: [
      {
        data: [
          review.value.dashboard_data.include,
          review.value.dashboard_data.maybe,
          review.value.dashboard_data.exclude,
        ],
        backgroundColor: [
          documentStyle.getPropertyValue('--green-400'),
          documentStyle.getPropertyValue('--gray-400'),
          documentStyle.getPropertyValue('--red-400'),
        ],
        hoverBackgroundColor: [
          documentStyle.getPropertyValue('--green-400'),
          documentStyle.getPropertyValue('--gray-400'),
          documentStyle.getPropertyValue('--red-400'),
        ],
      },
    ],
  }
}

const setChartOptions = () => {
  const documentStyle = getComputedStyle(document.documentElement)
  const textColor = documentStyle.getPropertyValue('--text-color')

  return {
    plugins: {
      legend: {
        labels: {
          usePointStyle: true,
          color: textColor,
        },
      },
    },
  }
}
</script>
