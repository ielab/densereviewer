<template>
  <Dialog
    v-model:visible="visible"
    modal
    :pt="{ root: 'tw-w-[95vw] tw-h-[100vh]' }"
  >
    <template #container>
      <div
        class="tw-rounded-t-lg tw-flex tw-overflow-y-auto tw-h-full tw-gap-4 tw-px-4"
        :class="isCompleteReview ? 'tw-bg-purple-50' : 'tw-bg-white'"
      >
        <!-- previous article button -->
        <div
          class="tw-absolute tw-top-0 tw-translate-y-[-3.5vh] tw-left-1/2 tw-translate-x-[-50%]"
          @click="prevDoc()"
        >
          <i
            class="fa-solid fa-chevron-up tw-cursor-pointer tw-text-white active:tw-scale-[0.8] tw-transition tw-duration-150 hover:tw-text-primary-500"
          />
        </div>

        <!-- next article button -->
        <div
          class="tw-absolute tw-bottom-0 tw-translate-y-[3.5vh] tw-left-1/2 tw-translate-x-[-50%]"
          @click="nextDoc()"
        >
          <i
            class="fa-solid fa-chevron-down tw-text-white tw-cursor-pointer active:tw-scale-[0.8] tw-transition tw-duration-150 hover:tw-text-primary-500"
          />
        </div>

        <!-- title, authors, pmid, ranking section -->
        <div class="tw-w-[26vw] tw-py-4">
          <div class="tw-flex tw-flex-col tw-justify-between tw-h-full">
            <div class="tw-flex tw-flex-col tw-gap-2">
              <p
                class="tw-font-medium tw-text-center tw-text-primary-500 tw-bg-primary-100"
              >
                Rank: #{{
                  currentPageReviewData.total_number_to_review *
                    currentPageIndex +
                  localDocs[currentIndex].rank
                }}
              </p>
              <p class="tw-text-2xl tw-font-bold">
                {{ localDocs[currentIndex].corpus.title }}
              </p>
              <div class="tw-flex tw-flex-wrap tw-gap-x-2">
                <span
                  class="tw-text-primary-500 tw-font-medium"
                  v-for="(au, index) in localDocs[currentIndex].corpus.authors"
                  :key="index"
                >
                  {{ au.author_abbreviated }}
                  <span
                    v-if="
                      index !==
                      localDocs[currentIndex].corpus.authors.length - 1
                    "
                  >
                    ;
                  </span>
                </span>
              </div>
              <p class="tw-text-slate-500">
                pmid: {{ localDocs[currentIndex].pmid }}
              </p>
            </div>

            <div class="tw-flex tw-flex-col tw-gap-2 tw-text-sm">
              <p class="tw-text-primary-500 tw-font-medium tw-text-right">
                {{ currentPageReviewData.reviewed }} /
                {{ currentPageReviewData.total_number_to_review }} Reviewed
              </p>
              <ProgressBar
                :showValue="false"
                style="height: 6px"
                :value="
                  (currentPageReviewData.reviewed /
                    currentPageReviewData.total_number_to_review) *
                  100
                "
              />
              <div class="tw-flex tw-items-center tw-gap-2">
                <i
                  class="fa-solid fa-circle fa-xs tw-text-green-500 border-bold tw-border-green-500 tw-rounded-full"
                />
                <p>Include ({{ currentPageReviewData.include }})</p>
              </div>
              <div class="tw-flex tw-items-center tw-gap-2">
                <i
                  class="fa-solid fa-circle fa-xs tw-text-gray-500 border-bold tw-border-gray-500 tw-rounded-full"
                />
                <p>Maybe ({{ currentPageReviewData.maybe }})</p>
              </div>
              <div class="tw-flex tw-items-center tw-gap-2">
                <i
                  class="fa-solid fa-circle fa-xs tw-text-red-500 border-bold tw-border-red-500 tw-rounded-full"
                />
                <p>Exclude ({{ currentPageReviewData.exclude }})</p>
              </div>
              <div class="tw-flex tw-items-center tw-gap-2">
                <i
                  class="fa-solid fa-circle fa-xs tw-text-white border-bold tw-border-gray-300 tw-rounded-full"
                />
                <p>
                  Unjudge ({{
                    currentPageReviewData.total_number_to_review -
                    currentPageReviewData.reviewed
                  }})
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- abstract section -->
        <ScrollPanel
          ref="autoScrollTarget"
          :pt="{
            root: 'tw-w-[48vw] tw-py-4 tw-relative tw-h-full',
            wrapper: 'tw-pr-4',
            bary: 'tw-opacity-100 tw-bg-primary-500',
          }"
        >
          <div
            v-if="extractSections(localDocs[currentIndex].corpus.abstract)"
            class="tw-flex tw-flex-col tw-gap-y-3"
          >
            <p
              v-for="section in extractSections(
                localDocs[currentIndex].corpus.abstract,
              )"
            >
              <span class="tw-font-medium">{{ section.header }}:</span>
              {{ section.content }}
            </p>
          </div>
          <p v-else>{{ localDocs[currentIndex].corpus.abstract }}</p>
        </ScrollPanel>

        <!-- keyboard guide panel section -->
        <div class="tw-w-[26vw] tw-py-2">
          <div class="tw-flex tw-justify-end">
            <i
              @click="visible = false"
              class="pi pi-window-minimize tw-mb-1 tw-text-sm tw-text-slate-500 active:tw-scale-[0.8] tw-transition tw-duration-150 hover:tw-text-primary-500 tw-cursor-pointer"
            />
          </div>
          <KeyBoardGuidePanel />
        </div>
      </div>

      <!-- shadow at bottom -->
      <div
        class="tw-text-center tw-bottom-[3.8rem] tw-absolute tw-w-full tw-bg-gradient-to-t tw-from-black/5 tw-h-[2.5rem]"
      ></div>

      <!-- footer section -->

      <div
        class="tw-p-2 tw-absolute tw-bottom-[3.8rem] tw-z-10 tw-left-1/2 tw-translate-x-[-50%]"
      >
        <Message
          v-for="msg of messages"
          :key="msg.id"
          :severity="msg.severity"
          :pt="{
            root: 'tw-bg-[#FEFCE9] tw-min-w-[60.5vw]',
          }"
          @click.stop
          @close="messages = []"
        >
          <div class="tw-flex tw-flex-col tw-gap-2 tw-px-2">
            <p>
              The following studies still require assessment. Please review them
              before continuing to the next page.
            </p>
            <p>You can navigate to each study by clicking its number.</p>
            <div class="tw-flex tw-justify-center tw-gap-4">
              <div v-for="item in unjudgeIndices">
                <Badge
                  :severity="
                    localDocs[item.index].feedback === 'unjudge'
                      ? 'warning'
                      : ''
                  "
                  :value="
                    currentPageReviewData.total_number_to_review *
                      currentPageIndex +
                    item.index +
                    1
                  "
                  class="tw-cursor-pointer tw-w-[1.6rem] tw-h-[1.6rem] tw-flex tw-text-center tw-justify-center tw-items-center tw-rounded-full"
                  :class="{
                    'tw-animate-bounce': currentIndex === item.index,
                  }"
                  @click="selectCard(item.index)"
                />
              </div>
            </div>
          </div>
        </Message>
      </div>

      <div
        class="tw-bg-white tw-flex tw-justify-between tw-px-6 tw-py-3 tw-rounded-b-lg"
      >
        <div
          class="tw-flex tw-w-full tw-justify-center tw-relative tw-items-end"
        >
          <p class="tw-absolute tw-left-0">
            #{{
              currentPageReviewData.total_number_to_review * currentPageIndex +
              localDocs[currentIndex].rank
            }}
            (Study {{ currentIndex + 1 }} of
            {{ currentPageReviewData.total_number_to_review }}, Page
            {{ currentPageIndex + 1 }})
          </p>
          <div class="tw-flex tw-gap-x-8">
            <CustomButton
              :pt="{ root: 'tw-py-[0.5rem] tw-w-[16rem]' }"
              icon="fa-solid fa-xmark"
              label="Exclude"
              severity="danger"
              @click="review('exclude', 'click')"
              :style="getActiveStyle('exclude')"
            />
            <CustomButton
              :pt="{ root: 'tw-py-[0.5rem] tw-w-[16rem]' }"
              icon="fa-solid fa-question"
              label="Maybe"
              severity="secondary"
              @click="review('maybe', 'click')"
              :style="getActiveStyle('maybe')"
            />
            <CustomButton
              :pt="{ root: 'tw-py-[0.5rem] tw-w-[16rem]' }"
              icon="fa-solid fa-check"
              label="Include"
              severity="success"
              @click="review('include', 'click')"
              :style="getActiveStyle('include')"
            />
          </div>
          <p class="tw-absolute tw-right-0">
            Page {{ currentPageIndex + 1 }} of {{ totalPageIndex }}
          </p>
        </div>
      </div>
    </template>
  </Dialog>

  <!-- Current Page Complete -->
  <Modal
    id="CurrentPageComplete"
    v-model:is-active="currentPageComplete"
    :close-on-escape="false"
  >
    <template #header>
      <h3>Current Page Completed</h3>
    </template>
    <template #body>
      <div class="tw-flex tw-flex-col tw-gap-3">
        <p>To continue:</p>
        <div class="tw-flex tw-gap-4 tw-items-center">
          <p
            class="tw-text-primary-500 tw-bg-primary-50 tw-rounded tw-px-2 tw-py-1 tw-font-medium tw-w-fit border"
          >
            Esc
          </p>
          <p>Exit focus mode</p>
        </div>
        <div
          v-if="currentPageIndex != totalPageIndex - 1"
          class="tw-flex tw-gap-4 tw-items-center"
        >
          <p
            class="tw-text-primary-500 tw-bg-primary-50 tw-rounded tw-px-2 tw-py-1 tw-font-medium tw-w-fit border"
          >
            P
          </p>
          <p>Pause screening and check summary of current assessment</p>
        </div>
        <div
          v-else
          class="tw-flex tw-gap-4 tw-items-center"
        >
          <p
            class="tw-text-primary-500 tw-bg-primary-50 tw-rounded tw-px-2 tw-py-1 tw-font-medium tw-w-fit border"
          >
            F
          </p>
          <p>Finish your screening</p>
        </div>
        <div
          v-if="currentPageIndex != totalPageIndex - 1"
          class="tw-flex tw-gap-4 tw-items-center"
        >
          <p
            class="tw-text-primary-500 tw-bg-primary-50 tw-rounded tw-px-2 tw-py-1 tw-font-medium tw-w-fit border"
          >
            N
          </p>
          <p>Continue screening on the next page</p>
        </div>
        <div
          v-if="currentPageIndex != totalPageIndex - 1"
        >
          <p
            class="tw-text-primary-500 tw-bg-primary-50 tw-rounded tw-px-2 tw-py-1 tw-font-medium border"
          >
            Note: System will rerank remaining studies based on your feedback.
            This may take a few moments.
          </p>
        </div>
      </div>
    </template>
    <template #footer>
      <div class="tw-w-full tw-flex tw-justify-end">
        <CustomButton
          label="Exit Focus Mode"
          @click="exitFocusMode()"
          severity="secondary"
        />
        <CustomButton
          v-if="currentPageIndex != totalPageIndex - 1"
          label="Pause Screening"
          severity="warning"
          @click="emit('pause')"
        />
        <CustomButton
          v-else
          label="Finish Screening"
          severity="danger"
          @click="emit('stop')"
        />
        <CustomButton
          v-if="currentPageIndex != totalPageIndex - 1"
          label="Continue to Next Page"
          class="tw-flex-1"
          @click="emitUpdatePage()"
        />
      </div>
    </template>
  </Modal>
</template>

<script lang="ts" setup>
import { ref, computed, watch } from 'vue'

import Dialog from 'primevue/dialog'
import CustomButton from '@/components/CustomButton.vue'
import KeyBoardGuidePanel from './KeyBoardGuidePanel.vue'
import ScrollPanel from 'primevue/scrollpanel'
import ProgressBar from 'primevue/progressbar'
import Modal from '@/components/Modal.vue'
import Message from 'primevue/message'
import Badge from 'primevue/badge'

import { IDoc } from '@/types/corpus'

const props = defineProps<{
  docs: IDoc[]
  index: number
  fullView: boolean
  currentPageIndex: number
  totalPageIndex: number
  currentPageReviewData: IPageReview
}>()

const emit = defineEmits([
  'update:full-view',
  'update:selected-card',
  'update:feedback',
  'update:page',
  'pause',
  'stop',
  'scroll-to-bottom',
])

const localDocs = ref<IDoc[]>(props.docs)
const currentIndex = ref(props.index)
const currentPageComplete = ref(false)

const visible = computed({
  get() {
    return props.fullView
  },
  set(value) {
    emit('update:full-view', value)
  },
})

const unjudgeIndices = ref<{ index: number }[]>([])

// feedback
const isCompleteReview = ref(
  localDocs.value[props.index].feedback !== 'unjudge',
)
const feedback = ref<'unjudge' | 'include' | 'exclude' | 'maybe'>(
  localDocs.value[currentIndex.value].feedback,
)

// warning unjudge =========================================================
const messages = ref<
  { severity: string; content: { index: number }[]; id: number }[]
>([])
let count = ref(0)

function review(
  value: 'unjudge' | 'include' | 'exclude' | 'maybe',
  event: 'click' | 'keyup',
) {
  if (!props.fullView) return
  if (
    (isCompleteReview.value && feedback.value == value && event === 'click') ||
    value === 'unjudge'
  ) {
    feedback.value = 'unjudge'
    isCompleteReview.value = false
  } else {
    feedback.value = value
    isCompleteReview.value = true
  }

  if (localDocs.value[currentIndex.value].feedback != feedback.value) {
    emit('update:feedback', {
      index: currentIndex.value,
      feedback: feedback.value,
    })
  }

  if (getAreAllFeedbacksJudged()) {
    currentPageComplete.value = true
  } else if (
    currentIndex.value ===
      props.currentPageReviewData.total_number_to_review - 1 &&
    !getAreAllFeedbacksJudged()
  ) {
    unjudgeIndices.value = localDocs.value
      .map((item, index) => (item.feedback === 'unjudge' ? { index } : null))
      .filter((entry) => entry !== null) as { index: number }[]

    messages.value = [
      { severity: 'warn', content: unjudgeIndices.value, id: count.value++ },
    ]
  }
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
    if (localDocs.value[currentIndex.value].feedback === value) {
      return styleMap[value]
    }
    return 'opacity: 40%'
  }
}

// keys event
const judge = ref<string>('')
let isKeyPressed = false

type KeyCombo =
  | 'Backspace'
  | 'ArrowUp'
  | 'ArrowDown'
  | 'ArrowLeft'
  | 'KeyM'
  | 'ArrowRight'
  | 'Alt+ArrowLeft'
  | 'Alt+KeyM'
  | 'Alt+ArrowRight'
  | 'Alt+ArrowDown'
  | 'Alt+ArrowUp'
  | 'Alt+Backspace'

const keyMappings: Record<KeyCombo, () => void> = {
  ArrowUp: () => prevDoc(),
  ArrowDown: () => nextDoc(),
  Backspace: () => review('unjudge', 'keyup'),
  ArrowLeft: () => review('exclude', 'keyup'),
  KeyM: () => review('maybe', 'keyup'),
  ArrowRight: () => review('include', 'keyup'),
  // composite keys
  'Alt+Backspace': () => {
    review('unjudge', 'keyup')
    setTimeout(() => {
      nextDoc()
    }, 500)
  },
  'Alt+ArrowLeft': () => {
    review('exclude', 'keyup')
    setTimeout(() => {
      nextDoc()
    }, 500)
  },
  'Alt+KeyM': () => {
    review('maybe', 'keyup')
    setTimeout(() => {
      nextDoc()
    }, 500)
  },
  'Alt+ArrowRight': () => {
    review('include', 'keyup')
    setTimeout(() => {
      nextDoc()
    }, 500)
  },
  'Alt+ArrowDown': () => {
    slowScrollDown()
  },
  'Alt+ArrowUp': () => {
    slowScrollTop()
  },
}

const emitUpdatePage = () => {
  if (props.currentPageIndex + 1 <= props.totalPageIndex - 1) {
    emit('update:page', props.currentPageIndex + 1)
  }
  // if (reopenFocusMode) {
  //   enterFocusMode(true)
  // }
}

const selectCard = (index: number) => {
  currentIndex.value = index
  initDoc()
}

window.addEventListener('keydown', (e) => {
  if (
    e.altKey &&
    [
      'KeyM',
      'ArrowLeft',
      'ArrowRight',
      'ArrowDown',
      'ArrowUp',
      'Backspace',
    ].includes(e.code)
  ) {
    e.preventDefault()
  } else if (
    [
      'KeyM',
      'ArrowLeft',
      'ArrowRight',
      'ArrowDown',
      'ArrowUp',
      'Backspace',
    ].includes(e.code)
  ) {
    e.preventDefault()
  }
})

window.addEventListener('keyup', (e) => {
  if (isKeyPressed) return
  isKeyPressed = true

  setTimeout(() => {
    isKeyPressed = false
  }, 500) // ป้องกันการกดซ้ำภายใน 500ms

  let combo: KeyCombo | null = null

  if (e.key === 'Escape') {
    if (currentPageComplete.value) {
      exitFocusMode()
    } else {
      emit('update:selected-card', currentIndex.value)
    }
  } else if (
    e.code === 'KeyN' &&
    currentPageComplete.value &&
    props.currentPageIndex !== props.totalPageIndex - 1
  ) {
    // exitFocusMode()
    emitUpdatePage()
  } else if (
    e.code === 'KeyP' &&
    currentPageComplete.value &&
    props.currentPageIndex !== props.totalPageIndex - 1
  ) {
    emit('pause')
  } else if (
    e.code === 'KeyF' &&
    currentPageComplete.value &&
    props.currentPageIndex === props.totalPageIndex - 1
  ) {
    emit('stop')
  }
  // Detect Alt + specific key combinations
  else if (
    e.altKey &&
    ['KeyM', 'ArrowLeft', 'ArrowRight', 'ArrowDown', 'ArrowUp'].includes(e.code)
  ) {
    if (!currentPageComplete.value) combo = `Alt+${e.code}` as KeyCombo
  }
  // Detect single key presses
  else if (
    ['KeyM', 'ArrowLeft', 'ArrowRight', 'ArrowDown', 'ArrowUp'].includes(
      e.code,
    ) &&
    !currentPageComplete.value
  ) {
    if (!currentPageComplete.value) combo = e.code as KeyCombo
  }
  // Detect Alt + backspace key combinations
  else if (e.altKey && 'Backspace' === e.code) {
    combo = `Alt+${e.code}` as KeyCombo
  }
  // Detect backspace key presses
  else if ('Backspace' === e.code) {
    combo = e.code as KeyCombo
  }

  if (combo && combo in keyMappings) {
    judge.value = combo
    keyMappings[judge.value as KeyCombo]()
    judge.value = ''
  }
})

// scroll
import type { ComponentPublicInstance } from 'vue'
import { IPageReview } from '@/types/statistic'
const autoScrollTarget = ref<ComponentPublicInstance | null>(null)

function scrollToTop() {
  const scrollTarget = autoScrollTarget.value?.$el.querySelector(
    '.p-scrollpanel-content',
  ) as HTMLElement | null

  if (scrollTarget) {
    scrollTarget.scrollTop = 0
  } else {
    console.warn('Scroll target is not available.')
  }
}

function slowScrollDown() {
  const scrollTarget = autoScrollTarget.value?.$el.querySelector(
    '.p-scrollpanel-content',
  ) as HTMLElement | null // Allow null

  if (!scrollTarget) {
    console.error('Scroll target not found')
    return // Exit early if scrollTarget is null
  }

  const startPosition = scrollTarget.scrollTop
  const maxScrollPosition =
    scrollTarget.scrollHeight - scrollTarget.clientHeight

  if (startPosition < maxScrollPosition) {
    const scrollAmount = scrollTarget.clientHeight / 3
    const targetPosition = Math.min(
      startPosition + scrollAmount,
      maxScrollPosition,
    )

    let startTime: number | null = null

    function animation(currentTime: number) {
      if (startTime === null) startTime = currentTime
      if (!scrollTarget) {
        return // Exit early if scrollTarget is null
      }
      const timeElapsed = currentTime - startTime
      const run = ease(
        timeElapsed,
        startPosition,
        targetPosition - startPosition,
        500,
      ) // Adjust duration if needed
      scrollTarget.scrollTop = run

      if (timeElapsed >= 500) {
        scrollTarget.scrollTop = targetPosition
      } else {
        requestAnimationFrame(animation)
      }
    }

    function ease(t: number, b: number, c: number, d: number) {
      t /= d / 2
      if (t < 1) return (c / 2) * t * t + b
      t--
      return (-c / 2) * (t * (t - 2) - 1) + b
    }

    requestAnimationFrame(animation)
  }
}

function slowScrollTop() {
  const scrollTarget = autoScrollTarget.value?.$el.querySelector(
    '.p-scrollpanel-content',
  ) as HTMLElement

  if (!scrollTarget) {
    console.error('Scroll target not found')
    return // Exit early if scrollTarget is null
  }

  const startPosition = scrollTarget.scrollTop
  const scrollAmount = scrollTarget.clientHeight / 3

  if (startPosition > 0) {
    const targetPosition = Math.max(startPosition - scrollAmount, 0)

    let startTime: number | null = null

    function animation(currentTime: number) {
      if (startTime === null) startTime = currentTime
      const timeElapsed = currentTime - startTime
      const run = ease(
        timeElapsed,
        startPosition,
        targetPosition - startPosition,
        500,
      ) // Adjust duration
      scrollTarget.scrollTop = run

      if (timeElapsed >= 500) {
        scrollTarget.scrollTop = targetPosition
      } else {
        requestAnimationFrame(animation)
      }
    }

    function ease(t: number, b: number, c: number, d: number) {
      t /= d / 2
      if (t < 1) return (c / 2) * t * t + b
      t--
      return (-c / 2) * (t * (t - 2) - 1) + b
    }

    requestAnimationFrame(animation)
  }
}

// control index docs
function prevDoc() {
  if (currentIndex.value - 1 >= 0 && props.fullView) {
    currentIndex.value = currentIndex.value - 1
    initDoc()
    scrollToTop()
    // emit('update:selected-card', currentIndex.value)
  }
}

function nextDoc() {
  // unjudgeIndices.value = []

  if (
    isCompleteReview.value &&
    currentIndex.value ===
      props.currentPageReviewData.total_number_to_review - 1
  ) {
    if (!getAreAllFeedbacksJudged()) {
      unjudgeIndices.value = localDocs.value
        .map((item, index) => (item.feedback === 'unjudge' ? { index } : null))
        .filter((entry) => entry !== null) as { index: number }[]
    } else {
      currentPageComplete.value = true
    }
  } else if (currentIndex.value + 1 < props.docs.length && props.fullView) {
    currentIndex.value = currentIndex.value + 1
    initDoc()
    scrollToTop()
    // emit('update:selected-card', currentIndex.value)
  }
}

// extract abstract section
function extractSections(abstract: string | undefined) {
  if (!abstract) {
    return
  }

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

function initDoc() {
  isCompleteReview.value =
    localDocs.value[currentIndex.value].feedback !== 'unjudge'
  feedback.value = localDocs.value[currentIndex.value].feedback
  getActiveStyle(localDocs.value[currentIndex.value].feedback)
}

function getAreAllFeedbacksJudged() {
  return localDocs.value.every((doc) => doc.feedback !== 'unjudge')
}

function exitFocusMode() {
  currentPageComplete.value = false
  visible.value = false
  setTimeout(() => {
    emit('scroll-to-bottom')
  }, 100)
}

watch(
  () => props.docs,
  (newVal) => {
    localDocs.value = newVal
    initDoc()
  },
  { deep: true },
)
</script>
