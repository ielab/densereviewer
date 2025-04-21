<template>
  <div class="tw-flex tw-gap-2 tw-items-center">
    <CustomIconButton
      rounded
      text
      icon="fa-solid fa-chevron-left"
      :disabled="page === 1 || isLoading"
      @click="updatePage('prevClick')"
      :pt="{root:'tw-h-8 tw-w-8'}"
    />
    <InputNumber
      v-model:modelValue="page"
      :suffix="` / ${totalPageIndex}`"
      @update:modelValue="updatePage('input')"
      :pt="{ input: 'tw-text-center tw-w-[8rem]' }"
      :disabled="isLoading"
    />
    <CustomIconButton
      rounded
      :text="
        areAllFeedbacksJudged && currentPageIndex != totalPageIndex - 1
          ? false
          : true
      "
      icon="fa-solid fa-chevron-right"
      :disabled="page === totalPageIndex || isLoading"
      @click="updatePage('nextClick')"
      :class="
        areAllFeedbacksJudged && currentPageIndex != totalPageIndex - 1
          ? 'tw-animate-ping'
          : undefined
      "
      :pt="{root:'tw-h-8 tw-w-8'}"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import CustomIconButton from '@/components/CustomIconButton.vue'
import InputNumber from 'primevue/inputnumber'

const props = defineProps({
  currentPageIndex: {
    type: Number,
    default: 0,
  },
  totalPageIndex: {
    type: Number,
    default: 0,
  },
  lastAccessiblePage: {
    type: Number,
    default: 0,
  },
  isLoading: {
    type: Boolean,
  },
  areAllFeedbacksJudged: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:page', 'update:dont-allow-next-page'])

const page = ref(props.currentPageIndex + 1)

function updatePage(type: 'input' | 'nextClick' | 'prevClick') {
  const inputElement = document.querySelector(
    '.p-inputnumber-input',
  ) as HTMLInputElement

  if (type === 'input' && page.value - 1 === props.currentPageIndex) {
    return
  }

  if (type === 'prevClick' && page.value - 1 > 0) {
    page.value -= 1
    emit('update:page', page.value - 1)
    return
  }

  if (!props.areAllFeedbacksJudged && page.value >= props.lastAccessiblePage) {
    page.value = props.currentPageIndex + 1
    setTimeout(() => {
      emit('update:dont-allow-next-page')
    }, 100)
    return
  }

  if (type === 'nextClick' && page.value < props.totalPageIndex) {
    page.value += 1
  }

  if (inputElement && type === 'input' && page.value < 1) {
    page.value = 1
  }

  if (
    inputElement &&
    type === 'input' &&
    page.value - props.lastAccessiblePage > 1
  ) {
    page.value = props.lastAccessiblePage
  }

  // if (type !== 'prevClick' && lastAccessiblePage.value < page.value) {
  //   lastAccessiblePage.value = page.value
  // }

  emit('update:page', page.value - 1)
  return
}

watch(
  () => props.currentPageIndex,
  (newValue) => {
    page.value = newValue + 1
  },
)
</script>
