<template>
  <div class="tw-flex tw-gap-6 tw-px-4 tw-min-h-[94vh]">
    <!-- Progress Review Side Bar -->
    <div
      v-if="showProgressReviewSideBar"
      class="tw-w-[26vw] tw-sticky tw-h-full tw-top-[7.25vh] tw-flex tw-flex-col tw-gap-2"
    >
      <CustomButton
        size="small"
        :disabled="selectedCard == null ? true : false"
        @click="enterFocusMode(true)"
        class="tw-w-full"
        icon="pi pi-window-maximize"
        label="Full View Mode"
      />
      <CurrentPageReview
        :data="progressReview.current_page_review"
        :current-page-index="currentPageIndex"
      />
      <OverallReview :data="progressReview.total_page_review" />
      <ScreeningTrendLineChart
        :data="progressReview.relevance_discovery_curve"
      />
      <div
        class="tw-absolute tw-right-[-0.75rem] tw-top-1/2"
        @click="setShowProgressReviewSideBar()"
      >
        <CustomIconButton
          icon="fa-solid fa-chevron-right"
          rounded
          size="small"
        />
      </div>
    </div>
    <div
      v-else
      class="tw-sticky tw-top-[3.3rem] tw-flex tw-flex-col tw-justify-center tw-h-[92vh]"
      @click="setShowProgressReviewSideBar()"
    >
      <CustomIconButton
        icon="fa-solid fa-chevron-left"
        rounded
        size="small"
      />
    </div>

    <!-- Main -->
    <div
      v-if="isLoading"
      :class="showProgressReviewSideBar ? 'tw-w-[74vw]' : 'tw-w-full'"
      class="tw-flex tw-flex-col tw-gap-4"
    >
      <div
        class="tw-text-primary-500 tw-gap-2 tw-w-full tw-h-full tw-flex tw-flex-col tw-justify-center tw-items-center tw-min-h-[86vh]"
      >
        <i class="pi pi-spin pi-spinner tw-mx-auto tw-text-[5rem]" />
        <p>Loading...</p>
      </div>
    </div>

    <div
      v-else
      :class="showProgressReviewSideBar ? 'tw-w-[74vw]' : 'tw-w-full'"
      class="tw-flex tw-flex-col tw-gap-4 tw-py-4"
    >
      <p class="tw-text-2xl tw-font-bold tw-text-center">
        {{ review.dataset_name }}
      </p>
      <div
        v-if="showProgressAndQuery"
        class="tw-flex tw-flex-col tw-gap-2"
      >
        <div class="tw-flex tw-flex-col tw-gap-4">
          <ScreeningProgressPanel
            :items="items"
            :active-step="1"
          />
          <QueryPanel :pico-query="review.query_pannel" />
        </div>
        <div class="tw-flex tw-gap-4 tw-pt-2">
          <Divider />
          <div @click="setShowProgressAndQuery()">
            <CustomIconButton
              size="small"
              icon="fa-solid fa-chevron-down"
              rounded
            />
          </div>
          <Divider />
        </div>
      </div>
      <div
        v-else
        class="tw-flex tw-gap-4"
      >
        <Divider />
        <div @click="setShowProgressAndQuery()">
          <CustomIconButton
            size="small"
            icon="fa-solid fa-chevron-up"
            rounded
          />
        </div>
        <Divider />
      </div>
      <div
        class="tw-flex tw-flex-col tw-items-center tw-justify-center tw-h-full tw-gap-y-4"
      >
        <div
          v-for="(doc, index) in review.screening_pannel"
          :key="index"
          @click="selectCard(Number(index))"
          class="screening-card tw-w-full"
        >
          <ScreeningCard
            :doc="doc"
            :index="Number(index)"
            :selected="selectedCard === Number(index)"
            :current-page-index="currentPageIndex"
            :total-number-to-review="
              progressReview.current_page_review.total_number_to_review
            "
            @update:full-view="enterFocusMode"
            @update:selected-card="updateSelectedCard"
            @update:feedback="updateFeedback"
          />
          <ScreeningFullView
            v-if="Number(index) === selectedCard"
            :docs="review.screening_pannel"
            :index="Number(index)"
            :full-view="fullView"
            :current-page-index="currentPageIndex"
            :total-page-index="review.total_number_of_pages"
            :current-page-review-data="progressReview.current_page_review"
            @update:full-view="enterFocusMode"
            @update:selected-card="updateSelectedCard"
            @update:feedback="updateFeedback"
            @update:page="updatePage"
            @pause="
              router.push({
                name: 'progress',
                params: { id: route.params.id },
                query: { index: currentPageIndex },
              })
            "
            @stop="
              router.push({
                name: 'summary',
                params: { id: route.params.id },
                query: { index: currentPageIndex },
              })
            "
            @scroll-to-bottom="scrollToBottom"
          />
        </div>
      </div>
    </div>
  </div>
  <!-- Footer -->
  <div
    class="tw-flex tw-justify-center tw-relative tw-w-full tw-items-center tw-pb-4"
  >
    <!-- Paginator -->
    <Paginator
      :current-page-index="currentPageIndex"
      :last-accessible-page="review.current_page_index + 1"
      :total-page-index="review.total_number_of_pages"
      :are-all-feedbacks-judged="getAreAllFeedbacksJudged()"
      :is-loading="isLoading"
      @update:page="updatePage"
      @update:dont-allow-next-page="dontAllowNextPage = true"
    />

    <CustomIconButton
      v-if="
        currentPageIndex === review.current_page_index &&
        currentPageIndex !== review.total_number_of_pages - 1
      "
      class="tw-absolute tw-right-4"
      severity="warning"
      icon="fa-solid fa-pause"
      rounded
      v-tooltip.top="'Pause'"
      @click="checkProgress('pause')"
      :disabled="isLoading"
    />

    <CustomIconButton
      v-else-if="currentPageIndex === review.total_number_of_pages - 1"
      class="tw-absolute tw-right-4"
      severity="danger"
      icon="fa-solid fa-stop"
      rounded
      v-tooltip.top="'Stop'"
      @click="checkProgress('stop')"
      :disabled="isLoading"
    />
  </div>

  <!-- Incomplete Screening Modal (Next Page) -->
  <Modal
    id="DontAllowNextPage"
    v-model:is-active="dontAllowNextPage"
    header="Must complete the screening on this page"
    title="Warning"
    leftBtn="Back"
    icon="pi pi-exclamation-circle"
    iconColor="warning"
    @close="scrollToUnjudgeCard()"
  >
    <template #body
      >You have not yet completed screening all of the studies on this page.
      Please provide assessment/feedback to all of the studies on this page
      before going to the next page.</template
    >
  </Modal>

  <!-- Incomplete Screening Modal (Pause) -->
  <Modal
    id="IncompleteScreeningModal"
    v-model:is-active="incompleteScreeningWarning"
    header="Must complete the screening on this page"
    title="Warning"
    leftBtn="Back"
    icon="pi pi-exclamation-circle"
    iconColor="warning"
    @close="scrollToUnjudgeCard()"
  >
    <template #body
      >You have not yet completed screening all of the studies on this page.
      Please provide assessment/feedback to all of the studies on this page
      before pausing your screening.</template
    >
  </Modal>

  <!-- Incomplete Screening Modal (Finish) -->
  <Modal
    id="DontAllowFinish"
    v-model:is-active="dontAllowFinish"
    header="Must complete the screening on this page"
    title="Warning"
    leftBtn="Back"
    icon="pi pi-exclamation-circle"
    iconColor="warning"
    @close="scrollToUnjudgeCard()"
  >
    <template #body
      >You have not yet completed screening all of the studies on this page.
      Please provide assessment/feedback to all of the studies on this page
      before finishing your screening.</template
    >
  </Modal>

  <!-- Pause Screening Confirmation Modal -->
  <Modal
    id="PauseScreeningConfirmationModal"
    v-model:is-active="pauseScreeningConfirm"
    header="Confirm to pause your screening"
    title="Information"
    leftBtn="Back"
    rightBtn="Confirm"
    icon="pi pi-exclamation-circle"
    iconColor="warning"
    @confirm="
      router.push({
        name: 'progress',
        params: { id: route.params.id },
        query: { index: currentPageIndex },
      })
    "
  >
    <template #body>
      Once you have paused your screening, you can view a summary and download
      your screening outcomes in nbib format. You can later resume your
      screening from the point you stop.
    </template>
  </Modal>

  <!-- Finish Screening Confirmation Modal -->
  <Modal
    id="FinishScreeningConfirmationModal"
    v-model:is-active="finishScreeningConfirm"
    header="Confirm to finish your screening"
    title="Information"
    leftBtn="Back"
    rightBtn="Confirm"
    icon="pi pi-exclamation-circle"
    iconColor="warning"
    @confirm="
      router.push({
        name: 'summary',
        params: { id: route.params.id },
        query: { index: currentPageIndex },
      })
    "
  >
    <template #body
      >Once you have finished your screening, you will not be able to make any
      changes regarding assessment/feedback provided to each study.
    </template>
  </Modal>

  <Message
    v-for="msg of messages"
    :key="msg.id"
    :severity="msg.severity"
    :pt="{
      root: 'tw-fixed tw-bottom-6 tw-bg-[#FEFCE9] tw-left-1/2 tw-translate-x-[-50%] tw-min-w-[62vw]',
    }"
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
              review.screening_pannel[item.index].feedback === 'unjudge'
                ? 'warning'
                : ''
            "
            :value="
              progressReview.current_page_review.total_number_to_review *
                currentPageIndex +
              item.index +
              1
            "
            class="tw-cursor-pointer tw-w-[1.6rem] tw-h-[1.6rem] tw-flex tw-text-center tw-justify-center tw-items-center tw-rounded-full"
            :class="{ 'tw-animate-bounce': selectedCard === item.index }"
            @click="selectCard(item.index)"
          />
        </div>
      </div>
    </div>
  </Message>
</template>

<script lang="ts" setup>
import CustomButton from '@/components/CustomButton.vue'
import CustomIconButton from '@/components/CustomIconButton.vue'
import Modal from '@/components/Modal.vue'
import Divider from 'primevue/divider'
import CurrentPageReview from './components/CurrentPageReview.vue'
import OverallReview from './components/OverallReview.vue'
import ScreeningProgressPanel from './components/ScreeningProgressPanel.vue'
import QueryPanel from './components/QueryPanel.vue'
import ScreeningCard from './components/ScreeningCard.vue'
import ScreeningTrendLineChart from './components/ScreeningTrendLineChart.vue'
import Paginator from './components/Paginator.vue'
import ScreeningFullView from './components/ScreeningFullView.vue'
import Badge from 'primevue/badge'
import Message from 'primevue/message'

import { ref, onMounted } from 'vue'

import axios, { AxiosError } from 'axios'
import { getTokenHeader } from '@/utils/auth'

import Cookies from 'js-cookie'
const TOKEN_KEY = import.meta.env.VITE_AUTH_TOKEN_KEY

import { useError } from '@/composables/error'
const { getResponseErrorMessage } = useError()

import { useToast } from '@/composables/toast'
const { showToast } = useToast()

import { useLoading } from '@/composables/loading'
const { isLoading, setLoading } = useLoading(false)

import { useRoute, useRouter } from 'vue-router'
const route = useRoute()
const router = useRouter()

import { useScroll } from '@/composables/scroll'
// const { scrollToTop, scrollToSelectedCard, scrollToBottom } = useScroll()
const {scrollToSelectedCard, scrollToBottom } = useScroll()

import startIcon from '@/assets/icons/start.png'
import reviewIcon from '@/assets/icons/review.png'
import flagIcon from '@/assets/icons/flag.png'

import { IReview } from '@/types/corpus'
import { IProgessReview } from '@/types/statistic'
import { DEFAULT_REVIEW } from '@/defaults/corpus'
import { DEFAULT_PROGRESS_REVIEW } from '@/defaults/statistic'

const showProgressReviewSideBar = ref(false)
const showProgressAndQuery = ref(false)
const fullView = ref(false)
const unjudgeIndices = ref<{ index: number }[]>([])

const currentPageIndex = ref()
const receivedMessage = ref(false)

const progressReview = ref<IProgessReview>(DEFAULT_PROGRESS_REVIEW)

// items for display Progress Panel
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
    icon: flagIcon,
  },
])

// Pause and Finished
const incompleteScreeningWarning = ref(false)
const dontAllowNextPage = ref(false)
const dontAllowFinish = ref(false)
const pauseScreeningConfirm = ref(false)
const finishScreeningConfirm = ref(false)

function getAreAllFeedbacksJudged() {
  return review.value.screening_pannel.every(
    (doc) => doc.feedback !== 'unjudge',
  )
}

function checkProgress(value: 'pause' | 'stop') {
  const areAllFeedbacksJudged = getAreAllFeedbacksJudged()

  if (areAllFeedbacksJudged) {
    if (value === 'pause') {
      pauseScreeningConfirm.value = true
    } else {
      finishScreeningConfirm.value = true
    }
  } else {
    if (value === 'pause') {
      incompleteScreeningWarning.value = true
    } else {
      dontAllowFinish.value = true
    }
  }
}

// selecting article
const selectedCard = ref<number | null>(null)
const selectCard = (index: number) => {
  selectedCard.value = selectedCard.value === index ? null : index
  scrollToSelectedCard(index)
}

const handleArrowDown = () => {
  if (fullView.value) return
  if (selectedCard.value === null) {
    selectedCard.value = 0 // Start at the first card
  } else if (selectedCard.value >= review.value.screening_pannel.length - 1) {
    selectedCard.value = 0 // Immediately loop back to the first card
  } else {
    selectedCard.value += 1 // Move to the next card
  }
  scrollToSelectedCard(selectedCard.value)
}

const handleArrowUp = () => {
  if (fullView.value) return
  if (selectedCard.value === null || selectedCard.value === 0) {
    selectedCard.value = review.value.screening_pannel.length - 1 // Start at the last card
  } else {
    selectedCard.value -= 1 // Move to the previous card
  }
  scrollToSelectedCard(selectedCard.value)
}

window.addEventListener('keyup', (e) => {
  if (!fullView.value) {
    if (e.key === 'ArrowDown') {
      handleArrowDown()
      e.preventDefault()
    } else if (e.key === 'ArrowUp') {
      handleArrowUp()
      e.preventDefault()
    }
  }
})

// update fullView
const enterFocusMode = (value: boolean) => {
  fullView.value = value
}

// update selectedCard
const updateSelectedCard = (value: number) => {
  selectedCard.value = value
  scrollToSelectedCard(selectedCard.value)
}

// Function to wait for receivedMessage to be true
const waitForReRanking = (timeoutMs: number = 30000): Promise<boolean> => {
  return new Promise((resolve, reject) => {
    const startTime = Date.now()

    const checkSuccess = () => {
      // If reranking succeeded, resolve immediately
      if (receivedMessage.value) {
        return resolve(true)
      }

      // Check if timeout has been exceeded
      const elapsedTime = Date.now() - startTime
      if (elapsedTime >= timeoutMs) {
        return reject(
          new Error(`Reranking timeout after ${timeoutMs / 1000} seconds`),
        )
      }

      // Continue checking
      requestAnimationFrame(checkSuccess)
    }

    // Start checking
    checkSuccess()
  })
}

// update page
const updatePage = async (index: number) => {
  if (!fullView.value) {
    selectedCard.value = null
  }
  
  const previousPageIndex = currentPageIndex.value

  try {
    setLoading(true)

    // Only perform reranking when moving to next page
    const isNeedReRanking = index > currentPageIndex.value
    currentPageIndex.value = index

    if (isNeedReRanking) {
      await reRanking()
      try {
        await waitForReRanking()
        // Only proceed if reranking was successful
        if (receivedMessage.value) {
          await getReview()
          scrollToSelectedCard(0)
          receivedMessage.value = false
        }
      } catch (error) {
        // Revert to previous page if reranking times out
        currentPageIndex.value = previousPageIndex
        throw error // Re-throw to be caught by outer try-catch
      }
    } else {
      await getReview()
      scrollToSelectedCard(0)
    }
  } catch (error) {
    console.error('Error during page update:', error)
    currentPageIndex.value = previousPageIndex

    if (error instanceof Error) {
      showToast('error', 'Page Update Failed', error.message)
    } else {
      showToast('error', 'Page Update Failed', 'An unexpected error occurred')
    }
  } finally {
    setLoading(false)
  }
}

// warning unjudge =========================================================
const messages = ref<
  { severity: string; content: { index: number }[]; id: number }[]
>([])
let count = ref(0)

function scrollToUnjudgeCard() {
  unjudgeIndices.value = review.value.screening_pannel
    .map((item, index) => (item.feedback === 'unjudge' ? { index } : null))
    .filter((entry): entry is { index: number } => entry !== null)

  selectedCard.value = unjudgeIndices.value[0]?.index ?? null

  messages.value = [
    { severity: 'warn', content: unjudgeIndices.value, id: count.value++ },
  ]

  scrollToSelectedCard(unjudgeIndices.value[0]?.index)
}

function setShowProgressAndQuery() {
  showProgressAndQuery.value = !showProgressAndQuery.value
  localStorage.setItem(
    'showProgressAndQuery',
    showProgressAndQuery.value ? '1' : '0',
  )
}

function setShowProgressReviewSideBar() {
  showProgressReviewSideBar.value = !showProgressReviewSideBar.value
  localStorage.setItem(
    'showProgressReviewSideBar',
    showProgressReviewSideBar.value ? '1' : '0',
  )
}

function initDisplayStatus() {
  if (
    localStorage.getItem('showProgressAndQuery') &&
    localStorage.getItem('showProgressReviewSideBar')
  ) {
    showProgressAndQuery.value =
      localStorage.getItem('showProgressAndQuery') == '1' ? true : false
    showProgressReviewSideBar.value =
      localStorage.getItem('showProgressReviewSideBar') == '1' ? true : false
  } else {
    setShowProgressAndQuery()
    setShowProgressReviewSideBar()
  }
}

// fetch Data
const review = ref<IReview>({ ...DEFAULT_REVIEW })
const getReview = async () => {
  try {
    setLoading(true)

    // Make the request
    const headers = {
      'Content-Type': 'multipart/form-data',
      ...getTokenHeader(),
    }
    const formData = new FormData()
    formData.append('review_id', String(route.params.id))

    if (currentPageIndex.value !== undefined) {
      formData.append('page_index', String(currentPageIndex.value))
    }

    const result = await axios.post('encoder/review_dataset', formData, headers)

    // If the request succeeds
    review.value = result.data.data

    if (currentPageIndex.value === undefined) {
      currentPageIndex.value = review.value.current_page_index
    }

    progressReview.value = review.value.dashboard_data
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

const reRanking = async () => {
  try {
    // Make the request
    const headers = {
      'Content-Type': 'multipart/form-data',
      ...getTokenHeader(),
    }
    const formData = new FormData()
    formData.append('review_id', String(route.params.id))
    formData.append('page_index', String(currentPageIndex.value - 1))
    await axios.post('encoder/re_ranking', formData, headers)
  } catch (error) {
    console.error(error)
    if (error instanceof AxiosError) {
      const e = getResponseErrorMessage(error)
      showToast('error', 'Cannot Re-Ranking Data', e.message)
    } else if (error instanceof Error) {
      showToast('error', 'Cannot Re-Ranking Data', error.message)
    } else {
      showToast('error', 'Cannot Re-Ranking Data', 'An error occurred')
    }
  }
}

async function updateFeedback(data: {
  index: number
  feedback: 'unjudge' | 'include' | 'exclude' | 'maybe'
}) {
  try {
    // Update Button at Frontend
    review.value.screening_pannel.splice(data.index, 1, {
      ...review.value.screening_pannel[data.index],
      feedback: data.feedback,
    })

    // Make the request
    const headers = {
      'Content-Type': 'multipart/form-data',
      ...getTokenHeader(),
    }
    const formData = new FormData()
    formData.append('review_id', route.params.id as string)
    formData.append('page_index', String(currentPageIndex.value))
    formData.append('in_page_rank_index', String(data.index))
    formData.append('pmid', review.value.screening_pannel[data.index].pmid)
    formData.append('feedback', data.feedback)
    const result = await axios.post(
      '/encoder/update_feedback',
      formData,
      headers,
    )
    progressReview.value = result.data.data
  } catch (error) {
    console.error(error)
    if (error instanceof AxiosError) {
      const e = getResponseErrorMessage(error)
      showToast('error', 'Cannot Update Feedback', e.message)
    } else if (error instanceof Error) {
      showToast('error', 'Cannot Update Feedback', error.message)
    } else {
      showToast('error', 'Cannot Update Feedback', 'An error occurred')
    }
  }
}

// Create websocket connection
function createWSConnection(token: string) {
  // Define target
  const target: string = `wss://${window.location.host}/ws`

  // Create websocket
  const websocket = new WebSocket(target)
  websocket.onopen = () => websocket.send(token)
  console.log('Websocket connection created')
  websocket.onmessage = handleWebSocketMessage
}

// Handle notification
function handleWebSocketMessage() {
  console.log('Received message from websocket')
  receivedMessage.value = true
}

onMounted(async () => {
  initDisplayStatus()
  await getReview()
  createWSConnection(Cookies.get(TOKEN_KEY) as string)
})
</script>
