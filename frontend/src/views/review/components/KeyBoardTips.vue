<!-- <template>
  <div
    class="tw-flex tw-flex-col tw-items-center tw-justify-center tw-text-center tw-gap-x-2"
  >
    <div
      :class="'tw-bg-' + color + '-200'"
      class="tw-w-[2.5rem] tw-h-[2.5rem] tw-rounded-lg tw-flex tw-justify-center"
    >
      <div
        class="tw-w-[1.5rem] tw-h-[1.5rem] tw-rounded tw-mt-[0.3rem] tw-flex tw-justify-center"
        :class="
          secondary ? 'tw-bg-white' : 'tw-bg-' + color + '-500'
        "
      >
        <p
          v-if="!keyIcon"
          class="tw-font-bold tw-text-white tw-text-xs"
        >
          {{ label }}
        </p>
        <i
          v-if="keyIcon !== 'Option'"
          class="tw-text-xs"
          :class="[
            keyIcon,
            secondary
              ? 'tw-text-' + color + '-500'
              : 'tw-text-white',
          ]"
        ></i>

        <img
          v-else
          :src="optionIcon"
          class="tw-h-[0.6rem] tw-mt-1"
        />
      </div>
    </div>
    <div class="tw-font-medium tw-text-sm">
      <p v-if="event">
        {{ event }}:
        <span
          :class="'tw-text-' + color + '-500'"
          class="tw-font-bold"
          >{{ label }}</span
        >
      </p>
      <p>{{ for }}</p>
      <i :class="forIcon"></i>
    </div>
  </div>
</template> -->

<template>
  <div class="tw-flex tw-flex-col tw-items-center">
    <div
      :class="{
        'tw-bg-primary-200': color === 'primary',
        'tw-bg-red-200': color === 'red',
        'tw-bg-green-200': color === 'green',
        'tw-bg-slate-200': color === 'slate',
      }"
      class="tw-w-[2.5rem] tw-h-[2.5rem] tw-rounded-lg tw-flex tw-justify-center"
    >
      <div
        :class="{
          'tw-bg-primary-500': color === 'primary',
          'tw-bg-red-500': color === 'red',
          'tw-bg-green-500': color === 'green',
          'tw-bg-slate-500': color === 'slate',
        }"
        class="tw-w-[1.5rem] tw-h-[1.5rem] tw-rounded tw-mt-[0.3rem] tw-flex tw-justify-center tw-font-bold tw-text-white tw-text-xs"
      >
        <img
          v-if="icon === 'option'"
          :src="optionIcon"
          class="tw-h-[0.6rem] tw-mt-1"
        />
        <i
          v-else-if="icon"
          :class="icon"
          class="tw-mt-[0.2rem]"
        />
        <p v-else-if="label">{{ label }}</p>
      </div>
    </div>
    <div v-if="showDetail" class="tw-text-sm tw-text-center tw-font-medium">
      <p>
        {{ event }}:
        <span
          :class="{
            'tw-text-primary-500': color === 'primary',
            'tw-text-red-500': color === 'red',
            'tw-text-green-500': color === 'green',
            'tw-text-slate-500': color === 'slate',
          }"
          class="tw-font-bold"
          >{{ label }}</span
        >
      </p>
      <p>{{ for }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
// import { ref } from 'vue'
import optionIcon from '@/assets/icons/option.png'

defineProps({
  color: { type: String, default: undefined },
  label: { type: String, default: undefined },
  icon: { type: String, default: undefined },
  event: { type: String, default: 'Press' },
  for: { type: String, default: undefined },
  forIcon: { type: String, default: undefined },
  secondary: { type: Boolean, default: false },
  showDetail: { type: Boolean, default: true },
})
</script>
