<template>
  <Container
    icon="fa-solid fa-arrow-up-from-bracket"
    title="Upload"
    class="tw-flex-col"
  >
    <div class="tw-flex tw-flex-col tw-gap-6">
      <div class="tw-w-full tw-flex tw-flex-col tw-gap-y-4">
        <h2>Instruction</h2>
        <p>
          Upload corpus.nbib or corpus.ris file (<span class="tw-text-red-500 tw-font-medium"
            >required</span
          >).
        </p>

        <Panel header="Sample Dataset">
          <p class="tw-mb-3">
            If you do not have one, you can try DenseReviewer with our sample
            corpus by downloading demo.ris (<span
              @click="downloadFile"
              style="color: blue"
              class="tw-cursor-pointer tw-underline tw-font-medium"
              >link</span
            >) here.
          </p>
          <QueryPanel :pico-query="staticPICOQuery" />
        </Panel>

        <Uploader
          @submit="uploadCorpus"
          submitLabel="Upload and Preview"
          :picoQueryDisabled="
            populations.length === 0 ||
            intervations.length === 0 ||
            comparisons.length === 0 ||
            outcomes.length === 0
          "
          :loading="isLoading"
        />
      </div>

      <p class="tw-text-[#4b5563]">
        You can click
        <span
          class="tw-cursor-pointer tw-text-primary-500 tw-font-medium"
          @click="initStaticPICOQuery()"
          >here</span
        >
        to use the PICO values from the sample dataset.
      </p>

      <!-- Population -->
      <div class="tw-flex tw-gap-x-5 tw-gap-y-2">
        <Panel
          :pt="{ header: 'tw-py-2', content: 'tw-p-2' }"
          class="tw-w-full"
        >
          <template #header>
            <p class="tw-font-medium">
              <span class="tw-font-bold"
                >P<span class="tw-text-red-500">*</span></span
              >
              - Population: The group of people or individuals being studied
            </p>
          </template>
          <div class="tw-flex tw-flex-col tw-gap-y-2">
            <div class="tw-flex tw-gap-x-2">
              <InputText
                class="tw-w-11/12"
                type="text"
                placeholder="Describe the research population"
                v-model="population"
              />
              <CustomButton
                class="tw-w-1/12"
                icon="pi pi-plus"
                label="Add"
                @click="pushPICOQuery('P')"
              />
            </div>
            <div
              v-for="(x, index) in populations"
              class="tw-flex tw-gap-x-2 tw-items-center"
            >
              <InputText
                :pt="{
                  root: 'tw-bg-primary-50 tw-text-primary-500 tw-font-medium',
                }"
                class="tw-w-11/12"
                type="text"
                :value="x"
                @input="(event) => updatePICOQuery('P', index, event)"
              />
              <CustomIconButton
                class="tw-w-1/12"
                icon="pi pi-trash"
                severity="danger"
                @click="removePICOQuery('P', index)"
              />
            </div>
          </div>
        </Panel>
      </div>

      <!-- Intervention -->
      <div class="tw-flex tw-gap-x-5 tw-gap-y-2">
        <Panel
          :pt="{ header: 'tw-py-2', content: 'tw-p-2' }"
          class="tw-w-full"
        >
          <template #header>
            <p class="tw-font-medium">
              <span class="tw-font-bold"
                >I<span class="tw-text-red-500">*</span></span
              >
              - Intervention: The treatment, exposure, or action being studied
            </p>
          </template>
          <div class="tw-flex tw-flex-col tw-gap-y-2">
            <div class="tw-flex tw-gap-x-2 tw-items-center">
              <InputText
                class="tw-w-11/12"
                type="text"
                placeholder="Describe the intervention being studied"
                v-model="intervation"
              />
              <CustomButton
                class="tw-w-1/12"
                icon="pi pi-plus"
                label="Add"
                @click="pushPICOQuery('I')"
              />
            </div>
            <div
              v-for="(x, index) in intervations"
              class="tw-flex tw-gap-x-2 tw-items-center"
            >
              <InputText
                :pt="{
                  root: 'tw-bg-primary-50 tw-text-primary-500 tw-font-medium',
                }"
                class="tw-w-11/12"
                type="text"
                :value="x"
                @input="(event) => updatePICOQuery('I', index, event)"
              />
              <CustomIconButton
                class="tw-w-1/12"
                icon="pi pi-trash"
                severity="danger"
                @click="removePICOQuery('I', index)"
              />
            </div>
          </div>
        </Panel>
      </div>

      <!-- Comparison -->
      <div class="tw-flex tw-gap-x-5 tw-gap-y-2">
        <Panel
          :pt="{ header: 'tw-py-2', content: 'tw-p-2' }"
          class="tw-w-full"
        >
          <template #header>
            <p class="tw-font-medium">
              <span class="tw-font-bold"
                >C<span class="tw-text-red-500">*</span></span
              >
              - Comparison: The alternative or standard intervention being used
              for comparison
            </p>
          </template>
          <div class="tw-flex tw-flex-col tw-gap-y-2">
            <div class="tw-flex tw-gap-x-2 tw-items-center">
              <InputText
                class="tw-w-11/12"
                type="text"
                placeholder="Describe the standard intervention being used for comparing with the studied invention"
                v-model="comparison"
              />
              <CustomButton
                class="tw-w-1/12"
                icon="pi pi-plus"
                label="Add"
                @click="pushPICOQuery('C')"
              />
            </div>
            <div
              v-for="(x, index) in comparisons"
              class="tw-flex tw-gap-x-2 tw-items-center"
            >
              <InputText
                :pt="{
                  root: 'tw-bg-primary-50 tw-text-primary-500 tw-font-medium',
                }"
                class="tw-w-11/12"
                type="text"
                :value="x"
                @input="(event) => updatePICOQuery('C', index, event)"
              />
              <CustomIconButton
                class="tw-w-1/12"
                icon="pi pi-trash"
                severity="danger"
                @click="removePICOQuery('C', index)"
              />
            </div>
          </div>
        </Panel>
      </div>

      <!-- Outcome -->
      <div class="tw-flex tw-gap-x-5 tw-gap-y-2">
        <Panel
          :pt="{ header: 'tw-py-2', content: 'tw-p-2' }"
          class="tw-w-full"
        >
          <template #header>
            <p class="tw-font-medium">
              <span class="tw-font-bold"
                >O<span class="tw-text-red-500">*</span></span
              >
              - Outcome: The result or effect being measured
            </p>
          </template>
          <div class="tw-flex tw-flex-col tw-gap-y-2">
            <div class="tw-flex tw-gap-x-2">
              <InputText
                class="tw-w-11/12"
                type="text"
                placeholder="Describe the outcomes of interest received from the study"
                v-model="outcome"
              />
              <CustomButton
                class="tw-w-1/12"
                icon="pi pi-plus"
                label="Add"
                @click="pushPICOQuery('O')"
              />
            </div>
            <div
              v-for="(x, index) in outcomes"
              class="tw-flex tw-gap-x-2 tw-items-center"
            >
              <InputText
                :pt="{
                  root: 'tw-bg-primary-50 tw-text-primary-500 tw-font-medium',
                }"
                class="tw-w-11/12"
                type="text"
                :value="x"
                @input="(event) => updatePICOQuery('O', index, event)"
              />
              <CustomIconButton
                class="tw-w-1/12"
                icon="pi pi-trash"
                severity="danger"
                @click="removePICOQuery('O', index)"
              />
            </div>
          </div>
        </Panel>
      </div>
      <ScrollTop />
    </div>
  </Container>
</template>

<script lang="ts" setup>
import Container from '@/components/Container.vue'
import Uploader from '@/components/Uploader.vue'
import Panel from 'primevue/panel'
import InputText from 'primevue/inputtext'
import CustomButton from '@/components/CustomButton.vue'
import CustomIconButton from '@/components/CustomIconButton.vue'
import ScrollTop from '@/components/ScrollTop.vue'
import QueryPanel from '../review/components/QueryPanel.vue'

import { ref } from 'vue'

import { useLoading } from '@/composables/loading'
const {setLoading, isLoading} = useLoading(false)

import { useRouter } from 'vue-router'
const router = useRouter()

import { useToast } from '@/composables/toast'
const { showToast } = useToast()

// import axios, { AxiosError } from 'axios'
import axios from 'axios'
import {
  uploadCollectionFilesStore,
  clearUploadCollectionFilesStore,
} from '@/stores/uploadCollection'
import { getTokenHeader } from '@/utils/auth'
import { IPicoQuery } from '@/types/corpus'

// Validate files to upload
const validateFiles = (files: File[]) => {
  // 1: INVALID -> No file selected
  if (files.length === 0)
    return showToast(
      'error',
      'No file selected',
      'Please select a file to upload.',
    )
  // 2: INVALID -> Too many files
  if (files.length > 2)
    return showToast(
      'error',
      'Too many files',
      'Please select only corpus.jsonl and queries.jsonl.',
    )
  // 3: INVALID -> Invalid file on 1 file upload
  // if (files.length === 1 && files[0].name !== 'corpus.jsonl')
  //   return showToast('error', 'Invalid file', 'Please select corpus.jsonl.')
  // 4: INVALID -> Invalid file on 2 files upload
  // const fileNames = files.map((file) => file.name)
  // if (
  //   files.length === 2 &&
  //   (!fileNames.includes('corpus.jsonl') ||
  //     !fileNames.includes('queries.jsonl'))
  // )
  //   return showToast(
  //     'error',
  //     'Invalid file',
  //     'There is some invalid file. Please select corpus.jsonl and queries.jsonl.',
  //   )
  // Otherwise, VALID
  return true
}

function pushPICOQuery(type: 'P' | 'I' | 'C' | 'O') {
  if (type === 'P' && population.value) {
    populations.value.push(population.value)
    population.value = ''
  } else if (type === 'I' && intervation.value) {
    intervations.value.push(intervation.value)
    intervation.value = ''
  } else if (type === 'C' && comparison.value) {
    comparisons.value.push(comparison.value)
    comparison.value = ''
  } else if (type === 'O' && outcome.value) {
    outcomes.value.push(outcome.value)
    outcome.value = ''
  }
}

function updatePICOQuery(
  type: 'P' | 'I' | 'C' | 'O',
  index: number,
  event: Event,
) {
  const target = event.target as HTMLInputElement | null
  if (target) {
    if (type === 'P') {
      populations.value[index] = target.value
    } else if (type === 'I') {
      intervations.value[index] = target.value
    } else if (type === 'C') {
      comparisons.value[index] = target.value
    } else {
      outcomes.value[index] = target.value
    }
  }
}

function removePICOQuery(type: 'P' | 'I' | 'C' | 'O', index: number) {
  if (type === 'P') {
    populations.value.splice(index, 1)
  } else if (type === 'I') {
    intervations.value.splice(index, 1)
  } else if (type === 'C') {
    comparisons.value.splice(index, 1)
  } else {
    outcomes.value.splice(index, 1)
  }
}

// PICO Queryy ----------------------------------------
const populations = ref<string[]>([])
const population = ref<string>('')

const intervations = ref<string[]>([])
const intervation = ref<string>('')

const comparisons = ref<string[]>([])
const comparison = ref<string>('')

const outcomes = ref<string[]>([])
const outcome = ref<string>('')

const staticPICOQuery = ref<IPicoQuery>({
  P: ['Aged 80 and over 80+ years', 'Adult 19-44 years'],
  I: ['Clarithromycin', 'Lincomycin'],
  C: ['Placebo', 'Drug Therapy'],
  O: ['All Cause Mortality', 'Serious Adverse Event'],
})

function initStaticPICOQuery() {
  populations.value = [...staticPICOQuery.value.P]
  intervations.value = [...staticPICOQuery.value.I]
  comparisons.value = [...staticPICOQuery.value.C]
  outcomes.value = [...staticPICOQuery.value.O]
}
// ----------------------------------------------------

// Download demo.ris file
const downloadFile = () => {
  const filePath = '/demo.ris' // Relative path to the file
  const link = document.createElement('a')
  link.href = filePath
  link.download = 'demo.ris' // Optional: Set the download name
  link.click()
}

const uploadCorpus = async (files: File[]) => {
  // Reset stored files
  clearUploadCollectionFilesStore()

  // Validate files
  if (!validateFiles(files)) return

  // Store files in your upload collection store (if needed for tracking)
  files.forEach((file) => {
    uploadCollectionFilesStore.value.file = file
  })

  // Create FormData for the request
  const formData = new FormData()
  const corpusFile = files.find(
    (file) => file.name.endsWith('.nbib') || file.name.endsWith('.ris'),
  ) // Adjust file name logic if needed

  if (!corpusFile) {
    console.error('No .nbib or .ris file found!')
    return
  }

  formData.append('nbib_file', corpusFile)

  try {
    setLoading(true)

    // Make the request
    const headers = {
      'Content-Type': 'multipart/form-data',
      ...getTokenHeader(),
    }

    const picoQuery = {
      P: populations.value,
      I: intervations.value,
      C: comparisons.value,
      O: outcomes.value,
    }
    const result = await axios.post('/encoder/upload_corpus', formData, headers)

    uploadCollectionFilesStore.value.corpus =
      result.data.data.preview_uploaded_corpus
    uploadCollectionFilesStore.value.picoQuery = picoQuery
    uploadCollectionFilesStore.value.totalDocuments = result.data.data.total_documents

    // Redirect to the preview page
    router.push({ name: 'preview' })
  } catch (error) {
    console.error('Error uploading corpus:', error)
    throw error // Optionally rethrow the error for further handling
  } finally {
    setLoading(false)
  }
}
</script>
