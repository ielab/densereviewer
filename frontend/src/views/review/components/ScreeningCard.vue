<template>
  <Card
    :pt="{
      root: 'tw-text-black tw-p-2',
      body: 'tw-p-0',
      content: 'tw-py-5 tw-px-3',
      footer: 'tw-py-0 tw-px-3',
    }"
    :style="selected ? selectedCardStyle : ''"
    class="tw-cursor-pointer border"
    :class="[
      selected ? '' : 'tw-shadow-none',
      isCompleteReview ? 'tw-bg-primary-50' : 'tw-bg-gray-50',
    ]"
  >
    <template #header>
      <div class="tw-flex tw-flex-col tw-gap-y-2">
        <div class="tw-flex tw-justify-between">
          <div class="tw-flex tw-flex-col tw-gap-y-1 tw-pl-3">
            <p class="tw-font-medium tw-text-xl tw-pr-4">
              {{ localDoc.corpus.title }}
            </p>
            <div>
              <span
                class="tw-text-primary-500 tw-font-medium"
                v-for="(au, index) in localDoc.corpus.authors"
                :key="index"
              >
                {{ au.author_abbreviated }}
                <span v-if="index != localDoc.corpus.authors.length - 1"
                  >;
                </span>
              </span>
            </div>
          </div>
          <i
            @click.stop="
              updateFullView(true);
              updatedSelectedCard(index);
            "
            class="pi pi-window-maximize tw-text-slate-500 tw-cursor-pointer tw-transform hover:tw-text-primary-500 active:tw-scale-[0.8] tw-transition tw-duration-150"
          />
        </div>
        <Divider />
      </div>
    </template>
    <template #content>
      <div :class="selected ? '' : 'tw-line-clamp-3'">
        <div v-if="extractSections(localDoc.corpus.abstract)">
          <p v-for="section in extractSections(localDoc.corpus.abstract)">
            <span>{{ section.header }}:</span>
            {{ section.content }}
          </p>
        </div>

        <div v-else>
          {{ localDoc.corpus.abstract }}
        </div>
      </div>
    </template>
    <template #footer>
      <div
        class="tw-flex tw-justify-center tw-gap-x-6 tw-relative tw-items-center"
      >
        <p class="tw-text-sm tw-text-gray-400 tw-absolute tw-left-0">
          #{{ totalNumberToReview * currentPageIndex + doc.rank }}
        </p>
        <CustomButton
          size="small"
          icon="fa-solid fa-xmark"
          label="Exclude"
          severity="danger"
          class="tw-w-1/6"
          :style="getActiveStyle('exclude')"
          @click.stop="review('exclude')"
        />
        <CustomButton
          size="small"
          icon="fa-solid fa-question"
          label="Maybe"
          severity="secondary"
          class="tw-w-1/6"
          :style="getActiveStyle('maybe')"
          @click.stop="review('maybe')"
        />
        <CustomButton
          size="small"
          icon="fa-solid fa-check"
          label="Include"
          severity="success"
          class="tw-w-1/6"
          :style="getActiveStyle('include')"
          @click.stop="review('include')"
        />
        <div class="tw-text-xs tw-text-gray-400 tw-absolute tw-right-0">
          <div class="tw-flex tw-items-center tw-gap-x-2">
            <i class="fa-solid fa-arrow-up"></i>
            <p class="tw-leading-[1rem]">
              Press Arrow Up: <span class="tw-font-bold">Move Previous</span>
            </p>
          </div>
          <div class="tw-flex tw-items-center tw-gap-x-2">
            <i class="fa-solid fa-arrow-down"></i>
            <p class="tw-leading-[1rem]">
              Press Arrow Down: <span class="tw-font-bold">Move Next</span>
            </p>
          </div>
          <div class="tw-flex tw-items-center tw-gap-x-2">
            <i class="fa-solid fa-arrow-turn-down tw-rotate-90"></i>
            <p class="tw-leading-[1rem]">
              Press Enter: <span class="tw-font-bold">Full View Mode</span>
            </p>
          </div>
        </div>
      </div>
    </template>
  </Card>
</template>

<script lang="ts" setup>
import Card from 'primevue/card'
import CustomButton from '@/components/CustomButton.vue'
import Divider from 'primevue/divider'

import { ref, watch } from 'vue'
import { IDoc } from '@/types/corpus'

const props = defineProps<{
  doc: IDoc
  index: number
  selected: boolean
  currentPageIndex: number
  totalNumberToReview: number
}>()

const emit = defineEmits([
  'update:full-view',
  'update:selected-card',
  'update:feedback',
])

const localDoc = ref<IDoc>(props.doc)
const fullView = ref(false)

// feedback
const isCompleteReview = ref(localDoc.value.feedback !== 'unjudge')
const feedback = ref<'unjudge' | 'include' | 'exclude' | 'maybe'>(
  localDoc.value.feedback,
)

function review(value: 'unjudge' | 'include' | 'exclude' | 'maybe') {
  if (isCompleteReview.value && feedback.value == value) {
    feedback.value = 'unjudge'
    isCompleteReview.value = false
  } else {
    feedback.value = value
    isCompleteReview.value = true
  }

  emit('update:feedback', { index: props.index, feedback: feedback.value })
}

const updateFullView = (value: boolean) => {
  fullView.value = value
  emit('update:full-view', fullView.value)
}
const updatedSelectedCard = (value: number) => {
  emit('update:selected-card', value)
}

const selectedCardStyle = 'box-shadow: #8B5CF6 0px 0px 0px 2px'
const includeStyle =
  'box-shadow: #dcfce7 0px 0px 0px 2px, #4ade80 0px 0px 0px 4px'
const maybeStyle =
  'box-shadow: #f1f5f9 0px 0px 0px 2px, #94a3b8 0px 0px 0px 4px'
const excludeStyle =
  'box-shadow: #fecaca 0px 0px 0px 2px, #f87171 0px 0px 0px 4px'

function getActiveStyle(value: 'unjudge' | 'include' | 'exclude' | 'maybe') {
  const styleMap = {
    unjudge: selectedCardStyle,
    include: includeStyle,
    maybe: maybeStyle,
    exclude: excludeStyle,
  }

  if (isCompleteReview.value) {
    if (localDoc.value.feedback === value) {
      return styleMap[value]
    }
    return 'opacity: 40%'
  }
}

window.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && props.selected) {
    e.preventDefault() // Prevent default action (like form submission)
    updateFullView(true)
  }
})

function extractSections(abstract: string) {
  // Regular expression to match dynamic section headers followed by a colon and content
  const sectionRegex = /([A-Z][A-Z\s]*):\s*([\s\S]*?)(?=\s*[A-Z][A-Z\s]*:|$)/g
  const sections = []
  let match

  // Iterate through all matches
  while ((match = sectionRegex.exec(abstract)) !== null) {
    const sectionHeader = match[1].trim()
    const sectionContent = match[2].trim()
    sections.push({
      header: sectionHeader,
      content: sectionContent,
    })
  }

  if (sections.length > 0) return sections
  return null
}

watch(
  () => props.doc,
  (newVal) => {
    localDoc.value = newVal
    isCompleteReview.value = localDoc.value.feedback !== 'unjudge'
    feedback.value = localDoc.value.feedback
    getActiveStyle(localDoc.value.feedback)
  },
  { deep: true },
)
</script>
