<template>
  <Panel
    :pt="panelStyles"
    header="Current Page Review"
  >
    <div class="tw-absolute tw-w-full tw-px-5">
      <div class="tw-flex tw-justify-between tw-w-full">
        <div>
          <p class="tw-font-bold">Page {{ currentPageIndex + 1 }}</p>
        </div>
        <div class="tw-flex tw-flex-col tw-text-right tw-gap-y-1">
          <div class="tw-flex">
            <div class="tw-w-[11rem] tw-mr-2">
              <p>Total number to review:</p>
            </div>
            <p
              class="tw-font-bold tw-text-white tw-bg-primary-500 tw-w-[2rem] tw-text-center tw-rounded"
            >
              {{ data.total_number_to_review }}
            </p>
          </div>
          <div class="tw-flex">
            <div class="tw-w-[11rem] tw-mr-2">
              <p>Reviewed:</p>
            </div>
            <p
              class="tw-font-bold tw-bg-primary-200 tw-w-[2rem] tw-text-center tw-rounded"
            >
              {{ data.reviewed }}
            </p>
          </div>
        </div>
      </div>
    </div>
    <Knob
      v-model="percentageReviewed"
      valueTemplate="{value}%"
      :min="0"
      :max="100"
      class="tw-mt-7"
      :size="70"
      readonly
    />

    <div class="tw-flex tw-justify-between tw-w-full tw-gap-x-2">
      <div class="tw-flex tw-items-center">
        <label class="tw-mr-1">Include:</label>
        <p
          class="tw-font-bold tw-bg-green-200 tw-w-[2rem] tw-text-center tw-rounded"
        >
          {{ data.include }}
        </p>
      </div>
      <div class="tw-flex tw-items-center">
        <label class="tw-mr-1">Maybe:</label>
        <p
          class="tw-font-bold tw-bg-slate-200 tw-w-[2rem] tw-text-center tw-rounded"
        >
          {{ data.maybe }}
        </p>
      </div>
      <div class="tw-flex tw-items-center">
        <label class="tw-mr-1">Exclude:</label>
        <p
          class="tw-font-bold tw-bg-red-200 tw-w-[2rem] tw-text-center tw-rounded"
        >
          {{ data.exclude }}
        </p>
      </div>
    </div>
  </Panel>
</template>

<script lang="ts" setup>
import Panel from 'primevue/panel'
import Knob from 'primevue/knob'
import { computed } from 'vue'
import { IPageReview } from '@/types/statistic'

const props = defineProps<{
  data: IPageReview
  currentPageIndex: number
}>()

const percentageReviewed = computed(() => {
  return Math.round((props.data.reviewed / props.data.total_number_to_review) * 100)
})

const panelStyles = {
  header: 'tw-py-2',
  content: 'tw-py-2 tw-flex tw-flex-col tw-items-center tw-relative tw-text-sm',
}
</script>