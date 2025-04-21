<template>
  <LoadingScreen v-if="isLoading" />

  <BlockUI
    :blocked="isLoading"
    :pt="{ root: 'tw-z-0' }"
  >
    <Container
      icon="fa-solid fa-arrow-up-from-bracket"
      title="Upload"
      class="tw-flex-col"
    >
      <FileUpload
        :multiple="true"
        :fileLimit="fileLimit"
        :maxFileSize="maxSize"
        customUpload
        :pt="{
          badge: { root: 'tw-hidden' },
          buttonbar: 'tw-p-0 tw-border-none tw-bg-white',
          content: 'tw-p-0 tw-border-none',
        }"
      >
        <template #header="{ chooseCallback, files }">
          <div class="tw-w-full tw-flex tw-flex-col tw-gap-6">
            <div class="tw-w-full tw-flex tw-flex-col tw-gap-y-4">
              <h2>Instruction</h2>
              <p>
                Upload corpus.nbib or corpus.ris file <span
                  class="tw-text-red-500 tw-font-medium"
                  >* (required)</span
                >
              </p>

              <Panel header="Sample Dataset">
                <div class="tw-flex tw-gap-4 tw-items-center tw-mb-3">
                  <p>
                    If you don’t have one, you can try DenseReviewer with our
                    sample corpus and pico query by clicking this button
                  </p>
                  <CustomButton
                    @click="useDemoFile(files)"
                    label="Sample Dataset"
                    icon="pi pi-file"
                    outlined
                  />
                </div>
                <QueryPanel :pico-query="staticPICOQuery" />
              </Panel>
            </div>

            <div
              class="tw-bg-[#fafafa] tw-w-full border tw-p-4 tw-rounded-t-lg"
            >
              <div class="tw-w-fit">
                <CustomButton
                  @click="chooseCallback"
                  label="Choose File"
                  type="light"
                  icon="pi pi-plus"
                  :disabled="files.length > 0"
                />
              </div>
            </div>
          </div>
        </template>

        <template #content="{ files, removeFileCallback }">
          <div class="tw-flex tw-flex-col tw-gap-6">
            <ul
              v-if="files.length > 0"
              class="tw-p-0 tw-m-0 tw-list-none tw-flex tw-flex-wrap tw-gap-2"
            >
              <li
                v-for="(file, index) in files"
                :key="file.name + index"
                class="tw-flex tw-items-center tw-justify-between tw-w-full tw-p-6 border tw-rounded-b-lg"
                style="border-top: none !important"
              >
                <div class="tw-flex tw-items-center tw-gap-6">
                  <img
                    :src="getIcon(file.name)"
                    width="36"
                    :style="{
                      filter: `invert(0.5) sepia(1) saturate(300%) ${getHue(
                        file.name,
                      )}`,
                    }"
                  />
                  <div>
                    <div class="tw-text-gray-600 tw-font-medium tw-mb-1">
                      {{ file.name }}
                    </div>
                    <div class="tw-text-gray-500 tw-text-xs">
                      {{ prettyBytes(file.size) }}
                    </div>
                  </div>
                </div>
                <i
                  @click="removeFileCallback(index)"
                  class="pi pi-times tw-cursor-pointer tw-text-red-500 tw-text-xl hover:tw-bg-red-100 tw-w-8 tw-h-8 tw-flex tw-items-center tw-justify-center tw-rounded-full tw-duration-150 active:tw-scale-95"
                />
              </li>
            </ul>

            <div
              v-else
              class="tw-flex tw-items-center tw-justify-center tw-flex-col tw-p-10 border tw-rounded-b-lg"
              style="border-top: none"
            >
              <i
                class="tw-m-2 pi pi-cloud-upload tw-rounded-full tw-border-2 tw-border-solid tw-text-gray-400 tw-border-gray-400 tw-p-8 tw-text-8xl"
              />
              <p class="tw-mt-4 tw-mb-0">Drag and drop files here to upload.</p>
            </div>

            <Panel :pt="{ content: 'tw-flex tw-flex-col tw-gap-4' }">
              <template #header>
                <p class="tw-font-medium">
                  <span class="tw-font-bold">PICO Query </span>
                  <span class="tw-text-red-500">* (You must enter at least 1 value of Pico Query.)</span>
                </p>
              </template>
              <!-- Population -->
              <div class="tw-flex tw-gap-x-5 tw-gap-y-2">
                <Panel
                  :pt="{ header: 'tw-py-2', content: 'tw-p-2' }"
                  class="tw-w-full"
                >
                  <template #header>
                    <p class="tw-font-medium">
                      <span class="tw-font-bold">P</span>
                      - Population: The group of people or individuals being
                      studied
                    </p>
                  </template>
                  <div class="tw-flex tw-flex-col tw-gap-y-2">
                    <div
                      class="tw-flex tw-gap-x-2"
                      @keydown.enter="pushPICOQuery('P')"
                    >
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
                        @input="(event:any) => updatePICOQuery('P', index, event)"
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
                      <span class="tw-font-bold">I</span>
                      - Intervention: The treatment, exposure, or action being
                      studied
                    </p>
                  </template>
                  <div class="tw-flex tw-flex-col tw-gap-y-2">
                    <div
                      class="tw-flex tw-gap-x-2 tw-items-center"
                      @keydown.enter="pushPICOQuery('I')"
                    >
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
                        @input="(event:any) => updatePICOQuery('I', index, event)"
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
                      <span class="tw-font-bold">C</span>
                      - Comparison: The alternative or standard intervention
                      being used for comparison
                    </p>
                  </template>
                  <div class="tw-flex tw-flex-col tw-gap-y-2">
                    <div
                      class="tw-flex tw-gap-x-2 tw-items-center"
                      @keydown.enter="pushPICOQuery('C')"
                    >
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
                        @input="(event:any) => updatePICOQuery('C', index, event)"
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
                      <span class="tw-font-bold">O</span>
                      - Outcome: The result or effect being measured
                    </p>
                  </template>
                  <div class="tw-flex tw-flex-col tw-gap-y-2">
                    <div
                      class="tw-flex tw-gap-x-2"
                      @keydown.enter="pushPICOQuery('O')"
                    >
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
                        @input="(event:any) => updatePICOQuery('O', index, event)"
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
            </Panel>

            <div class="tw-flex tw-justify-end">
              <CustomButton
                @click="submit(files)"
                label="Next to Preview"
                :disabled="
                  !files.length ||
                  (populations.length === 0 &&
                    intervations.length === 0 &&
                    comparisons.length === 0 &&
                    outcomes.length === 0)
                "
              />
            </div>
          </div>
        </template>
      </FileUpload>
    </Container>
  </BlockUI>
</template>

<script lang="ts" setup>
import { ref } from 'vue'
import prettyBytes from 'pretty-bytes'
import Container from '@/components/Container.vue'
import FileUpload from 'primevue/fileupload'
import CustomButton from '@/components/CustomButton.vue'
import Panel from 'primevue/panel'
import QueryPanel from '@/views/review/components/QueryPanel.vue'
import CustomIconButton from '@/components/CustomIconButton.vue'
import InputText from 'primevue/inputtext'
import BlockUI from 'primevue/blockui'
import LoadingScreen from '@/components/LoadingScreen.vue'

import { useLoading } from '@/composables/loading'
const { setLoading, isLoading } = useLoading(false)

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

defineProps({
  fileLimit: { type: Number, default: 3 },
  maxSize: { type: Number, default: 1024 ** 3 }, // 1GB
  submitLabel: { type: String, default: 'Submit' },
  picoQueryDisabled: { type: Boolean, default: true },
  loading: { type: Boolean, default: false },
})

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
    return showToast('error', 'Too many files', 'Please select only one file.')
  return true
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

// -------------------------------------------------------------------

const getIcon = (filename: string) => {
  if (['nbib', 'ris'].includes(filename.split('.')[1])) {
    return '/file.png'
  }
  return '/warning.png'
}

const getHue = (filename: string) => {
  if (['nbib', 'ris'].includes(filename.split('.')[1])) {
    return 'hue-rotate(60deg)'
  }
  return 'hue-rotate(315deg)'
}

const useDemoFile = (files: File[]) => {
  // Clear all existing files
  files.splice(0, files.length)

  fetch('/demo.ris')
    .then((response) => response.blob())
    .then((blob) => {
      const demoFile = new File([blob], 'demo.ris', {
        type: blob.type,
      })
      files.push(demoFile)
    })
    .catch((error) => {
      console.error('Error fetching demo file:', error)
    })

  initStaticPICOQuery()
}

const submit = async (files: File[]) => {
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
    uploadCollectionFilesStore.value.totalDocuments =
      result.data.data.total_documents

    // Redirect to the preview page
    router.push({ name: 'preview' })
  } catch (error) {
    setLoading(false)
    console.error('Error uploading corpus:', error)
    throw error // Optionally rethrow the error for further handling
  }
}

// Download demo.ris file
// const downloadFile = () => {
//   const filePath = '/demo.ris' // Relative path to the file
//   const link = document.createElement('a')
//   link.href = filePath
//   link.download = 'demo.ris' // Optional: Set the download name
//   link.click()
// }
</script>
