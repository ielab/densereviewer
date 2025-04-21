<template>
  <LoadingScreen v-if="isLoading" />

  <BlockUI
    :blocked="isLoading"
    :pt="{ root: 'tw-z-0' }"
  >
    <Container
      icon="pi pi-inbox"
      title="My Dataset / Review List"
      class="tw-flex-col"
    >
      <template #subtitle>
        <p>
          The estimated indexing time is approximately 15 seconds for the demo
          RIS file. Please refresh the page to view the updated status and start
          screening.
        </p>
        <p>
          (Auto-refreshing in {{ countdown }} second<span v-if="countdown !== 1"
            >s</span
          >.)
        </p>
      </template>

      <div class="tw-flex tw-flex-col tw-gap-6">
        <div class="tw-flex tw-justify-end">
          <CustomButton
            class="tw-w-[13.5%]"
            icon="pi pi-plus-circle"
            label="New Dataset"
            @click="router.push({ name: 'upload' })"
          />
        </div>

        <div class="tw-flex tw-gap-4 tw-items-center">
          <i class="pi pi-search" />
          <InputText
            fluid
            class="tw-w-full"
            placeholder="Search by Name"
            v-model="searchQuery"
          />
          <Button
            v-model="filterVisible"
            icon="pi pi-filter"
            label="Filters"
            @click="toggle"
            outlined
          />

          <OverlayPanel ref="op">
            <div class="tw-flex tw-flex-col tw-gap-4 tw-w-[18vw]">
              <div class="tw-flex tw-flex-col tw-gap-1">
                <small class="tw-font-medium tw-text-primary-500">
                  Screening Status
                </small>
                <Dropdown
                  v-model="selectedScreeningStatus"
                  :options="screeningStatusArray"
                  optionLabel="name"
                  placeholder="Select Screening Status"
                >
                  <template #value="slotProps">
                    <small
                      v-if="slotProps.value"
                      class="tw-rounded tw-w-fit tw-px-2"
                      :class="getScreeningStatusClass(slotProps.value.value)"
                    >
                      {{ toTitleCase(slotProps.value.value.replace('_', ' ')) }}
                    </small>
                    <span v-else>
                      <small>{{ slotProps.placeholder }}</small>
                    </span>
                  </template>
                  <template #option="slotProps">
                    <small
                      class="tw-rounded tw-w-fit tw-px-2"
                      :class="getScreeningStatusClass(slotProps.option.value)"
                    >
                      {{
                        toTitleCase(slotProps.option.value.replace('_', ' '))
                      }}
                    </small>
                  </template>
                </Dropdown>
              </div>
              <div class="tw-flex tw-justify-between">
                <Button
                  label="Clear"
                  outlined
                  size="small"
                  :pt="{ root: 'tw-py-2', label: 'tw-text-xs' }"
                  @click="clearScreeningStatusFilter"
                />
                <Button
                  label="Apply"
                  size="small"
                  :pt="{ root: 'tw-py-2', label: 'tw-text-xs' }"
                  @click="applyScreeningStatusFilter"
                />
              </div>
            </div>
          </OverlayPanel>
        </div>

        <DataTable
          showGridlines
          stripedRows
          :value="filteredDatasets"
          paginator
          :rows="10"
          :rowsPerPageOptions="[10, 20, 50]"
        >
          <Column
            field="order"
            class=""
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
            class="tw-w-[24%]"
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
            sortable
            class=""
            :pt="{ bodyCell: 'tw-text-center' }"
          >
            <template #header>
              <p class="tw-m-auto tw-text-center">Submission<br />Timestamp</p>
            </template>
            <template #body="slotProps">
              <p>
                {{
                  formatDateTime(slotProps.data.submission_timestamp).split(
                    ', ',
                  )[0]
                }}
              </p>
              <p>
                {{
                  formatDateTime(slotProps.data.submission_timestamp).split(
                    ', ',
                  )[1]
                }}
              </p>
            </template>
          </Column>
          <Column
            field="start_indexing_timestamp"
            sortable
            class=""
            :pt="{ bodyCell: 'tw-text-center' }"
          >
            <template #header>
              <p class="tw-m-auto tw-text-center">
                Start Indexing<br />Timestamp
              </p>
            </template>
            <template #body="slotProps">
              <p>
                {{
                  formatDateTime(slotProps.data.start_indexing_timestamp).split(
                    ', ',
                  )[0]
                }}
              </p>
              <p>
                {{
                  formatDateTime(slotProps.data.start_indexing_timestamp).split(
                    ', ',
                  )[1]
                }}
              </p>
            </template>
          </Column>
          <Column
            field="indexing_time_spent"
            sortable
            class=""
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
            class="tw-w-[11%]"
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
                {{
                  toTitleCase(slotProps.data.indexing_status.replace('_', ' '))
                }}
              </p>
            </template>
          </Column>
          <Column
            field="screening_status"
            class="tw-w-[11%]"
            :pt="{ bodyCell: 'tw-text-center' }"
          >
            <template #header>
              <p class="tw-m-auto tw-text-center">Screening<br />Status</p>
            </template>
            <template #body="slotProps">
              <p
                class="tw-rounded"
                :class="
                  getScreeningStatusClass(slotProps.data.screening_status)
                "
              >
                {{
                  toTitleCase(slotProps.data.screening_status.replace('_', ' '))
                }}
              </p>
              <small
                v-if="
                  slotProps.data.screening_status === 'screening' &&
                  slotProps.data.current_page_index + 1 <=
                    slotProps.data.total_number_of_pages
                "
              >
                Page {{ slotProps.data.current_page_index + 1 }} /
                {{ slotProps.data.total_number_of_pages }}
              </small>
            </template>
          </Column>
          <Column
            field="action"
            class=""
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
                :outlined="
                  getActionButtonLabel(slotProps.data.screening_status) ===
                  'Resume SR'
                "
                :severity="
                  getActionButtonLabel(slotProps.data.screening_status) ===
                  'Start Review'
                    ? 'secondary'
                    : ''
                "
              />
            </template>
          </Column>

          <template #empty>
            <p class="tw-text-center">No dataset / review list found.</p>
          </template>
        </DataTable>
      </div>
    </Container>
  </BlockUI>
</template>

<script lang="ts" setup>
import Container from '@/components/Container.vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import CustomButton from '@/components/CustomButton.vue'
import LoadingScreen from '@/components/LoadingScreen.vue'
import BlockUI from 'primevue/blockui'
import InputText from 'primevue/inputtext'
import Dropdown from 'primevue/dropdown'
import OverlayPanel from 'primevue/overlaypanel'
import Button from 'primevue/button'

import { ref, computed, onMounted } from 'vue'
import { formatDateTime } from '@/utils/datetime'
import { toTitleCase } from '@/utils/string'

import axios, { AxiosError } from 'axios'
import { getTokenHeader } from '@/utils/auth'

import { useRoute, useRouter } from 'vue-router'
const route = useRoute()
const router = useRouter()

import { useError } from '@/composables/error'
const { getResponseErrorMessage } = useError()

import { useToast } from '@/composables/toast'
const { showToast } = useToast()

import { useLoading } from '@/composables/loading'
const { isLoading, setLoading } = useLoading(false)

import { IDataset, IIndexingStatus, IScreeningStatus } from '@/types/dataset'
import { DEFAULT_DATASET } from '@/defaults/dataset'

const originalDatasets = ref<IDataset[]>([DEFAULT_DATASET])
const datasets = ref<IDataset[]>([DEFAULT_DATASET])

const searchQuery = ref('')
const filterVisible = ref(false)
const selectedScreeningStatus = ref()
const screeningStatusArray = ref([
  { name: 'Not Started', value: 'not_start' },
  { name: 'Screening', value: 'screening' },
  { name: 'Paused', value: 'paused' },
  { name: 'Finished', value: 'finished' },
])

// overlay panel
const op = ref()
const toggle = (event: any) => {
  op.value.toggle(event)
}

// Computed property for filtering datasets
const filteredDatasets = computed(() => {
  if (!searchQuery.value) return datasets.value
  return datasets.value.filter((dataset) =>
    dataset.name.toLowerCase().includes(searchQuery.value.toLowerCase()),
  )
})

const clearScreeningStatusFilter = (event: any) => {
  op.value.toggle(event)
  selectedScreeningStatus.value = null
  datasets.value = originalDatasets.value
}

const applyScreeningStatusFilter = (event: any) => {
  op.value.toggle(event)

  if (!selectedScreeningStatus.value) return

  datasets.value = datasets.value.filter(
    (dataset) =>
      dataset.screening_status === selectedScreeningStatus.value.value,
  )
}

const getDataset = async () => {
  try {
    setLoading(true)
    const result = await axios.get('encoder/get_review_list', getTokenHeader())
    const sortedData = result.data.data.sort(
      (a: IDataset, b: IDataset) =>
        new Date(b.submission_timestamp).getTime() -
        new Date(a.submission_timestamp).getTime(),
    )
    originalDatasets.value = sortedData
    datasets.value = sortedData
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

const countdown = ref(15)
const startCountdown = () => {
  setInterval(() => {
    if (countdown.value > 0) {
      countdown.value -= 1 // Decrease by 1 every second
    } else {
      countdown.value = 15 // Reset to 15 when it reaches 0
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
