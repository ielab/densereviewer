<template>
  <Dialog
    v-model:visible="visible"
    modal
    :pt="{ root: 'tw-w-[40rem]' }"
    :breakpoints="{ '1199px': '75vw', '575px': '90vw' }"
    :close-on-escape="closeOnEscape"
  >
    <template #header>
      <div class="tw-flex tw-gap-3 tw-items-center">
        <i
          v-if="icon"
          :class="[
            icon,
            {
              'tw-text-red-500': iconColor == 'danger',
              'tw-text-amber-500': iconColor == 'warning',
              'tw-text-teal-500': iconColor == 'success',
            },
          ]"
          class="tw-text-2xl"
        />
        <span
          v-if="header"
          class="tw-font-bold"
          >{{ header }}</span
        >
        <slot name="header" />
      </div>
    </template>
    <div class="tw-flex">
      <span class="tw-flex tw-flex-col">
        <h2 v-if="title">{{ title }}</h2>
        <div class="tw-font-bold tw-text-violet-600 tw-text-lg tw-break-all">
          <slot name="value"></slot>
        </div>
        <div class="tw-flex tw-flex-col tw-gap-3 tw-pt-3">
          <slot name="body"></slot>
        </div>
        <div>
          <slot name="note"></slot>
        </div>
      </span>
    </div>
    <template #footer>
      <div
        v-focustrap
        class="tw-flex tw-justify-end"
      >
        <slot name="footer">
          <CustomButton
            v-if="leftBtn"
            :label="leftBtn"
            severity="secondary"
            @click="handleClose"
          />
          <CustomButton
            autofocus
            v-if="rightBtn"
            :label="rightBtn"
            :severity="severity"
            @click="handleConfirm"
          />
        </slot>
      </div>
    </template>
  </Dialog>
</template>

<script lang="ts" setup>
import { computed } from 'vue'

import Dialog from 'primevue/dialog'
import CustomButton from './CustomButton.vue'

import { useRouter } from 'vue-router'
const router = useRouter()

const props = defineProps({
  isActive: { type: Boolean, default: false },
  header: { type: String },
  title: { type: String },
  leftBtn: { type: String },
  rightBtn: { type: String },
  icon: { type: String },
  iconColor: { type: String },
  route: { type: String },
  severity: { type: String },
  closeOnEscape: { type: Boolean, default: true },
})

const emit = defineEmits(['update:isActive', 'confirm', 'close'])
const visible = computed({
  get() {
    return props.isActive
  },
  set(value) {
    emit('update:isActive', value)
  },
})

function handleClose() {
  visible.value = false
  emit('close', true)
}

function handleConfirm() {
  setTimeout(() => {
    visible.value = false
    router.push({ name: props.route })
    emit('confirm', true)
  }, 100)
}
</script>
