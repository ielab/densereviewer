<template>
  <LoadingScreen v-if="isLoading" />
  <Container
    v-else
    icon="pi pi-inbox"
    title="My Dataset / Review List"
    class="tw-flex-col"
  >
    <template #subtitle>
      <p>
        The estimated indexing time is approximately 30 seconds for the demo RIS
        file. Please refresh the page to view the updated status and start
        screening.
      </p>
      <p>
        (Auto-refreshing in {{ countdown }} second<span v-if="countdown !== 1"
          >s</span
        >.)
      </p>
    </template>

    <div class="tw-flex tw-justify-end tw-mb-8">
      <CustomButton
        class="tw-w-[13.5%]"
        icon="pi pi-plus-circle"
        label="New Dataset"
        @click="router.push({ name: 'upload' })"
      />
    </div>

    <DataTable
      showGridlines
      stripedRows
      :value="datasets"
    >
      <Column
        field="order"
        class="tw-w-[5%]"
        :pt="{ bodyCell: 'tw-text-center' }"
      >
        <template #header>
          <p class="tw-m-auto tw-text-center">Order</p>
        </template>
        <template #body="slotProps">
          {{ slotProps.index + 1 }}
        </template>
      </Column>
      <Column
        field="name"
        class="tw-w-[27%]"
        :pt="{ bodyCell: 'tw-text-center' }"
      >
        <template #header>
          <p class="tw-m-auto tw-text-center">Name</p>
        </template>
        <template #body="slotProps">
          {{ slotProps.data.name }}
        </template>
      </Column>
      <Column
        field="submission_timestamp"
        class="tw-w-[10%]"
        :pt="{ bodyCell: 'tw-text-center' }"
      >
        <template #header>
          <p class="tw-m-auto tw-text-center">Submission<br />Timestamp</p>
        </template>
        <template #body="slotProps">
          {{ formatDateTime(slotProps.data.submission_timestamp) }}
        </template>
      </Column>
      <Column
        field="start_indexing_timestamp"
        class="tw-w-[10%]"
        :pt="{ bodyCell: 'tw-text-center' }"
      >
        <template #header>
          <p class="tw-m-auto tw-text-center">Start Indexing<br />Timestamp</p>
        </template>
        <template #body="slotProps">
          {{ formatDateTime(slotProps.data.start_indexing_timestamp) }}
        </template>
      </Column>
      <Column
        field="indexing_time_spent"
        class="tw-w-[10%]"
        :pt="{ bodyCell: 'tw-text-center' }"
      >
        <template #header>
          <p class="tw-m-auto tw-text-center">Indexing<br />Time Spent</p>
        </template>
        <template #body="slotProps">
          <p v-if="slotProps.data.indexing_time_spent">
            {{ slotProps.data.indexing_time_spent }}
          </p>
          <p v-else>—</p>
        </template>
      </Column>
      <Column
        field="indexing_status"
        class="tw-w-[13%]"
        :pt="{ bodyCell: 'tw-text-center' }"
      >
        <template #header>
          <p class="tw-m-auto tw-text-center">Indexing<br />Status</p>
        </template>
        <template #body="slotProps">
          <p
            class="tw-rounded"
            :class="getIndexingStatusClass(slotProps.data.indexing_status)"
          >
            {{ toTitleCase(slotProps.data.indexing_status.replace('_', ' ')) }}
          </p>
        </template>
      </Column>
      <Column
        field="screening_status"
        class="tw-w-[10%]"
        :pt="{ bodyCell: 'tw-text-center' }"
      >
        <template #header>
          <p class="tw-m-auto tw-text-center">Screening<br />Status</p>
        </template>
        <template #body="slotProps">
          <p
            class="tw-rounded"
            :class="getScreeningStatusClass(slotProps.data.screening_status)"
          >
            {{ toTitleCase(slotProps.data.screening_status.replace('_', ' ')) }}
          </p>
        </template>
      </Column>
      <Column
        field="action"
        class="tw-w-[13.5%]"
      >
        <template #header>
          <p class="tw-m-auto tw-text-center">Action</p>
        </template>
        <template #body="slotProps">
          <CustomButton
            @click="
              navigation(
                slotProps.data.id,
                slotProps.data.screening_status,
                slotProps.data.current_page_index,
              )
            "
            class="tw-w-full"
            size="small"
            :label="getActionButtonLabel(slotProps.data.screening_status)"
            :disabled="
              slotProps.data.indexing_status !== 'index_ready' &&
              slotProps.data.indexing_status !== 're-rank_ready'
            "
          />
        </template>
      </Column>
    </DataTable>
  </Container>
</template>

<script lang="ts" setup>
import Container from '@/components/Container.vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import CustomButton from '@/components/CustomButton.vue'
import LoadingScreen from '@/components/LoadingScreen.vue'

import { ref, onMounted } from 'vue'
import { formatDateTime } from '@/utils/datetime'
import { toTitleCase } from '@/utils/string'

import axios, { AxiosError } from 'axios'
import { getTokenHeader } from '@/utils/auth'

import { useRoute } from 'vue-router'
const route = useRoute()

import { useError } from '@/composables/error'
const { getResponseErrorMessage } = useError()

import { useToast } from '@/composables/toast'
const { showToast } = useToast()

import { useLoading } from '@/composables/loading'
import { IDataset, IIndexingStatus, IScreeningStatus } from '@/types/dataset'
import router from '@/router'
const { isLoading, setLoading } = useLoading(false)

const datasets = ref<IDataset[]>()

const getDataset = async () => {
  try {
    setLoading(true)
    const result = await axios.get('encoder/get_review_list', getTokenHeader())
    datasets.value = result.data.data
  } catch (error) {
    console.error(error)
    if (error instanceof AxiosError) {
      const e = getResponseErrorMessage(error)
      showToast('error', 'Cannot Fetch Dataset/Review List', e.message)
    } else if (error instanceof Error) {
      showToast('error', 'Cannot Fetch Dataset/Review List', error.message)
    } else {
      showToast(
        'error',
        'Cannot Fetch Dataset/Review List',
        'An error occurred',
      )
    }
  } finally {
    setLoading(false)
  }
}

function getIndexingStatusClass(status: IIndexingStatus): string {
  if (status === 'queued') {
    return 'tw-bg-gray-200 tw-text-gray-500'
  }
  if (status === 'indexing' || status === 're-ranking') {
    return 'tw-bg-yellow-100 tw-text-yellow-500'
  }
  if (status === 'index_ready' || status === 're-rank_ready') {
    return 'tw-bg-green-100 tw-text-green-500'
  }
  if (status === 'archived') {
    return 'tw-bg-gray-200 tw-text-gray-500'
  }
  if (status === 'indexing_error') {
    return 'tw-bg-red-100 tw-text-red-500'
  }
  return ''
}

function getScreeningStatusClass(status: IScreeningStatus): string {
  if (status === 'not_start') {
    return 'tw-bg-gray-200 tw-text-gray-500'
  }
  if (status === 'screening') {
    return 'tw-bg-green-100 tw-text-green-500'
  }
  if (status === 'paused') {
    return 'tw-bg-orange-100 tw-text-orange-500'
  }
  if (status === 'finished') {
    return 'tw-bg-primary-100 tw-text-primary-500'
  }
  return ''
}

function getActionButtonLabel(status: IScreeningStatus): string {
  if (status === 'screening') {
    return 'Resume SR'
  }
  if (status === 'paused' || status === 'finished') {
    return 'SR Summary'
  }
  return 'Start Review'
}

function navigation(
  id: number,
  status: IScreeningStatus,
  currentPageIndex: number,
) {
  if (status === 'paused') {
    return router.push({
      name: 'progress',
      params: { id },
      query: { index: currentPageIndex },
    })
  }
  if (status === 'finished') {
    return router.push({
      name: 'summary',
      params: { id },
      query: { index: currentPageIndex },
    })
  }
  return router.push({
    name: 'review',
    params: { id },
  })
}

function hasQueuedOrIndexingStatus(datasets: IDataset[]): boolean {
  return datasets.some(
    (dataset) =>
      dataset.indexing_status === 'queued' ||
      dataset.indexing_status === 'indexing',
  )
}

function checkStatusEvery30Seconds(datasetsRef: typeof datasets): void {
  setInterval(() => {
    const result = hasQueuedOrIndexingStatus(datasetsRef.value ?? []) // Use fallback to empty array
    if (result && route.name === 'mydataset') {
      window.location.reload()
    }
  }, 30000)
}

const countdown = ref(30)
const startCountdown = () => {
  setInterval(() => {
    if (countdown.value > 0) {
      countdown.value -= 1 // Decrease by 1 every second
    } else {
      countdown.value = 30 // Reset to 30 when it reaches 0
    }
  }, 1000) // Update every 1 second
}

// Fetch dataset and start periodic checks
onMounted(async () => {
  await getDataset()
  checkStatusEvery30Seconds(datasets)
  startCountdown()
})
</script>
