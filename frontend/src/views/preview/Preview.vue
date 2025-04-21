<template>
  <LoadingScreen v-if="isLoading" />

  <BlockUI
    :blocked="isLoading || emptyCorpus || emptyPicoQuery"
    :pt="{ root: 'tw-z-0' }"
  >
    <Container>
      <div class="tw-flex tw-flex-col tw-gap-6">
        <div class="tw-flex tw-flex-col tw-gap-2">
          <div class="tw-flex tw-w-full">
            <div
              v-focustrap
              class="tw-w-2/3 tw-flex tw-flex-col tw-gap-2"
            >
              <label>
                Dataset/Review Name <span class="tw-text-red-500">*</span>
              </label>
              <InputText
                fluid
                class="tw-w-full"
                :class="[{ 'tw-border-red-500': duplicateError }]"
                v-model="datasetName"
                autofocus
                @keyup.enter="submit()"
              />
            </div>
            <div
              class="tw-w-1/3 tw-flex tw-flex-row tw-gap-2 tw-justify-end tw-items-end"
            >
              <CustomButton
                label="Cancel"
                severity="secondary"
                class="tw-w-fit"
                @click="deleteCorpus()"
              />
              <CustomButton
                label="Create Dataset/Review"
                class="tw-w-fit"
                @click="submit()"
              />
            </div>
          </div>
          <small
            v-if="duplicateError"
            class="tw-text-red-500"
          >
            {{ errorMessage }} Please retry with a new name.
          </small>
        </div>

        <Divider />

        <Panel header="Corpus Format Requirements">
          <div class="tw-flex tw-flex-col tw-gap-4">
            <p>
              Make sure that your dataset conform to the system requirements and
              follow the format below:
            </p>

            <div class="tw-flex tw-flex-col tw-gap-2">
              <p>
                - <b>corpus.ris</b>: a text file in ris format from your
                literature management software such as EndNote, which includes 3
                fields:
              </p>
              <p class="tw-indent-3">
                pmid : the PubMed unique identifier or unique record identifier
                of literature in a custom database
              </p>
              <p class="tw-indent-3">
                title : the title of a scholarly article
              </p>
              <p class="tw-indent-3">
                abstract : the abstract of a scholarly article with paragraphs
                or passages
              </p>
            </div>

            <p>
              If your dataset does not follow the described format, please
              update your files and re-upload.
            </p>
          </div>
        </Panel>

        <Panel>
          <template #header>
            <div class="tw-flex tw-items-center tw-gap-4">
              <b>Corpus File</b>
              <div
                class="tw-flex tw-text-sm tw-text-[#4b5563] tw-items-center tw-gap-2"
              >
                <i class="pi pi-info-circle" />
                <p>
                  Showing preview of first entry • Total
                  <span class="tw-text-primary-500 tw-font-medium"
                    >{{ uploadCollectionFilesStore.totalDocuments }}
                    <span v-if="uploadCollectionFilesStore.totalDocuments === 1"
                      >study</span
                    ><span v-else>studies</span></span
                  >
                  in corpus
                </p>
              </div>
            </div>
          </template>
          <Textarea
            v-model="corpusFirstEntry"
            :rows="20"
            disabled
            class="tw-w-full"
          />
        </Panel>
        <QueryPanel :pico-query="picoQuery" />
        <ScrollTop />
      </div>
    </Container>
  </BlockUI>

  <Modal
    v-model:isActive="isCreateModalActive"
    header="Confirm to create a dataset for your systematic review project  "
    title="Information"
    leftBtn="Back"
    rightBtn="Confirm"
    icon="pi pi-exclamation-circle"
    iconColor="warning"
    @confirm="confirmSubmit"
  >
    <template #body>
      <p>
        Once you have created a dataset, please note that you will not be able
        to rename the dataset or make changes to the uploaded corpus and PICO
        evidence-based query. This is because the system will promptly index and
        rank studies based on your provided PICO query.
      </p>
      <p>
        For demonstration purposes, we will periodically delete uploaded
        datasets and their indices to safeguard the privacy and information that
        you input into our system.
      </p>
    </template>
  </Modal>
</template>

<script lang="ts" setup>
import { onMounted, ref, nextTick } from 'vue'

import Container from '@/components/Container.vue'
import CustomButton from '@/components/CustomButton.vue'
import Divider from 'primevue/divider'
import Panel from 'primevue/panel'
import Textarea from 'primevue/textarea'
import QueryPanel from '../review/components/QueryPanel.vue'
import ScrollTop from '@/components/ScrollTop.vue'
import Modal from '@/components/Modal.vue'
import BlockUI from 'primevue/blockui'
import LoadingScreen from '@/components/LoadingScreen.vue'

import axios, { AxiosError } from 'axios'
import { getTokenHeader } from '@/utils/auth.ts'

import {
  uploadCollectionFilesStore,
  clearUploadCollectionFilesStore,
} from '@/stores/uploadCollection'
import InputText from 'primevue/inputtext'
import { IUploadedCorpus, IPicoQuery } from '@/types/corpus.js'

import { ValidationError } from 'joi'
import { validateCollection } from './validations/validateCollection.ts'

import { useToast } from '@/composables/toast'
const { showToast } = useToast()

import { useError } from '@/composables/error'
const { getResponseErrorMessage } = useError()

import { useLoading } from '@/composables/loading'
const { isLoading, setLoading } = useLoading(false)

const duplicateError = ref(false)
const errorMessage = ref('')

import { useRouter } from 'vue-router'
const router = useRouter()

const datasetName = ref('')

const corpus = ref<IUploadedCorpus>(uploadCollectionFilesStore.value.corpus)
const corpusFirstEntry = ref(corpus.value.corpus_first_entry)

const picoQuery = ref<IPicoQuery>(uploadCollectionFilesStore.value.picoQuery)

const isCreateModalActive = ref(false)
const isCreateDatasetSuccess = ref(false)

const emptyCorpus = ref(false)
const emptyPicoQuery = ref(false)

const submit = async () => {
  try {
    // Validate collection name
    const validation = validateCollection(datasetName.value)
    if (validation.error) throw validation.error
    setTimeout(() => {
      isCreateModalActive.value = true
    }, 100)
  } catch (error) {
    console.error(error)
    if (error instanceof ValidationError) {
      errorMessage.value = error.details
        .map((detail) => detail.message)
        .join(' ')
      showToast('error', 'Invalid Dataset/Review Name', errorMessage.value)
    } else if (error instanceof Error) {
      showToast('error', 'Invalid Dataset/Review Name', error.message)
    } else {
      showToast('error', 'Invalid Dataset/Review Name', 'An error occurred.')
    }
  }
}

const confirmSubmit = async () => {
  try {
    setLoading(true)
    duplicateError.value = false

    const body = {
      corpus_id: corpus.value.id,
      dataset_name: datasetName.value,
      pico_query: { ...picoQuery.value },
    }
    await axios.post('/encoder/dataset_creation', body, getTokenHeader())
    isCreateDatasetSuccess.value = true
    router.push({ name: 'mydataset' })
  } catch (error) {
    setLoading(false)
    console.error(error)

    if (error instanceof Error) {
      errorMessage.value = error.message
    }

    if (error instanceof AxiosError) {
      errorMessage.value = getResponseErrorMessage(error).message

      const regex = /^The collection name\((.*?)\) is duplicated\.$/
      if (regex.test(errorMessage.value)) {
        duplicateError.value = true
      }
    }

    showToast('error', 'Failed to create datasets', errorMessage.value)
  }
}

const deleteCorpus = async () => {
  try {
    setLoading(true)
    const params = { corpus_id: corpus.value.id }
    await axios.delete('/encoder/upload_corpus', getTokenHeader({ params }))
    clearUploadCollectionFilesStore()
    return router.push({ name: 'home' })
  } catch (error) {
    setLoading(false)
    console.error(error)
    let errorMessage = ''
    console.log(errorMessage)
    if (error instanceof Error) errorMessage = error.message
    if (error instanceof AxiosError)
      errorMessage = getResponseErrorMessage(error).message
    throw error
  }
}

onMounted(async () => {
  emptyCorpus.value = uploadCollectionFilesStore.value.totalDocuments <= 0
  emptyPicoQuery.value = Object.values(picoQuery.value).every(
    (arr) => Array.isArray(arr) && arr.length === 0,
  )

  if (emptyCorpus.value || emptyPicoQuery.value) {
    alert(
      'Your uploaded corpus file was not found. Please upload the corpus file and pico query first.',
    )

    await nextTick()
    router.push({ name: 'upload' })
  }
})
</script>
