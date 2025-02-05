<template>
  <div class="tw-w-full tw-py-1">
    <Steps
    :model="props.items"
    :active-step="props.activeStep"
  >
    <template #item="{ item, index }">
      <div
        class="tw-flex tw-flex-col tw-items-center tw-text-center tw-justify-center tw-z-10 tw-gap-2"
      >
        <span>
          <div
            class="tw-bg-purple-200 tw-rounded-full tw-p-3 tw-flex"
            :class="index == props.activeStep ? 'active-step tw-bg-purple-300' : ''"
          >
            <img
              :src="item.icon"
              alt="Icon"
              width="30"
              height="30"
            />
          </div>
        </span>
        <div>{{ item.label }}</div>
      </div>
    </template>
  </Steps>
  </div>
</template>

<script setup lang="ts">
import Steps from 'primevue/steps'

interface Item {
  label: string;
  icon: string;
}

const props = defineProps<{
  activeStep: number
  items: Item[]
}>()
</script>
