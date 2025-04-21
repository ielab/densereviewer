<template>
  <div class="tw-w-full tw-min-h-[86vh]">
    <div class="iframe-background">
      <div class="iframe">
        <iframe
          src="https://giphy.com/embed/pOEbLRT4SwD35IELiQ"
          width="100%"
          height="100%"
          style="position: absolute"
          frameBorder="0"
          class="giphy-embed"
          allowFullScreen
        ></iframe>
        <div class="dark-overlay"></div>
      </div>
      <div class="text-overlay tw-flex tw-flex-col tw-gap-7">
        <h1>DenseReviewer</h1>
        <h2>
          An Online Interactive Screening System to Support Systematic Review
          based on Dense Retrieval and Relevance Feedback
        </h2>
        <div class="tw-flex tw-justify-center">
          <div class="tw-text-xl tw-mt-2">
            Accelerate your title and abstract screening with DenseReviewer!
            <br />
            Simply upload your studies as the corpus and provide PICO as a
            query, and our intelligent system will streamline your screening
            workflow by prioritising relevant studies and continuously learning
            from your feedback.
          </div>
        </div>
        <CustomButton
          label="Get Started"
          class="tw-w-fit tw-mx-auto"
          @click="router.push({ name: isLoggedIn ? 'mydataset' : 'login' })"
        />
      </div>
    </div>
    <div class="tw-px-64 tw-py-16 tw-flex tw-flex-col tw-gap-16">
      <Fieldset
        legend="How to use our system"
        :pt="{
          legend: 'tw-py-0 tw-px-3 tw-border-none tw-bg-transparent tw-text-xl',
        }"
      >
        <div class="tw-grid tw-grid-cols-3 tw-p-4 tw-gap-x-16 tw-gap-y-8">
          <div
            v-for="(item, index) in howToUse"
            class="tw-flex tw-flex-col tw-gap-4"
          >
            <div class="tw-flex tw-items-center tw-gap-2">
              <div class="icon-container">
                <i
                  :class="item.icon"
                  class="fa-lg tw-text-primary-500"
                />
              </div>
              <p class="tw-font-bold">{{ index + 1 }}. {{ item.header }}</p>
            </div>
            <p class="tw-text-[#4b5563]">{{ item.label }}</p>
          </div>
        </div>
      </Fieldset>

      <Fieldset
        legend="How to prepare your dataset"
        :pt="{
          legend: 'tw-py-0 tw-px-3 tw-border-none tw-bg-transparent tw-text-xl',
        }"
      >
        <div class="tw-grid tw-grid-cols-2 tw-p-4 tw-gap-x-16 tw-gap-y-8">
          <div class="tw-flex tw-flex-col tw-gap-4">
            <div class="tw-flex tw-items-center tw-gap-2">
              <div class="icon-container">
                <i class="fa-solid fa-book fa-lg tw-text-primary-500" />
              </div>
              <p class="tw-font-bold">Corpus</p>
            </div>
            <div class="tw-flex tw-flex-col tw-gap-4 tw-text-[#4b5563]">
              <p>Your PubMed .nbib file containing these essential fields:</p>
              <div class="tw-flex">
                <p class="tw-font-medium tw-w-[25%]">PMID</p>
                <p class="tw-w-[75%]">8-digit PubMed unique identifier</p>
              </div>
              <div class="tw-flex">
                <p class="tw-font-medium tw-w-[25%]">Title</p>
                <p class="tw-w-[75%]">Study title</p>
              </div>
              <div class="tw-flex">
                <p class="tw-font-medium tw-w-[25%]">Abstract</p>
                <p class="tw-w-[75%]">Full study abstract</p>
              </div>
              <div class="tw-flex">
                <p class="tw-font-medium tw-w-[25%]">Authors</p>
                <p class="tw-w-[75%]">Author information</p>
              </div>
            </div>
          </div>

          <div class="tw-flex tw-flex-col tw-gap-4">
            <div class="tw-flex tw-items-center tw-gap-2">
              <div class="icon-container">
                <i class="fa-solid fa-bullseye fa-lg tw-text-primary-500" />
              </div>
              <p class="tw-font-bold">PICO Query</p>
            </div>
            <div class="tw-flex tw-flex-col tw-gap-4 tw-text-[#4b5563]">
              <p>Structure your clinical question using the PICO framework:</p>
              <div class="tw-flex">
                <p class="tw-font-medium tw-w-[20%]">P</p>
                <p class="tw-w-[80%]">
                  Patient/Population - Who are you studying?
                </p>
              </div>
              <div class="tw-flex">
                <p class="tw-font-medium tw-w-[20%]">I</p>
                <p class="tw-w-[80%]">
                  Intervention - What is the main intervention?
                </p>
              </div>
              <div class="tw-flex">
                <p class="tw-font-medium tw-w-[20%]">C</p>
                <p class="tw-w-[80%]">
                  Comparison - What are you comparing against?
                </p>
              </div>
              <div class="tw-flex">
                <p class="tw-font-medium tw-w-[20%]">O</p>
                <p class="tw-w-[80%]">What are you trying to measure?</p>
              </div>
              <p>
                PICO helps you define precise search criteria for more effective
                reviews.
              </p>
            </div>
          </div>
        </div>
      </Fieldset>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, computed } from 'vue'

import { accountAuthStore } from '@/stores/auth'

import Fieldset from 'primevue/fieldset'
import CustomButton from '@/components/CustomButton.vue'
import router from '@/router'

const isLoggedIn = computed(() => accountAuthStore.id !== null)

const howToUse = ref([
  {
    icon: 'fa-solid fa-arrow-right-to-bracket',
    header: 'Get Started',
    label: 'Create an account and log in to begin',
  },
  {
    icon: 'fa-solid fa-arrow-up-from-bracket',
    header: 'Upload & Configure',
    label:
      'Upload your corpus and define your PICO query to set review criteria',
  },
  {
    icon: 'fa-solid fa-database',
    header: 'Processing',
    label:
      'Let our intelligent system process your data to create an initial ranking.',
  },
  {
    icon: 'fa-solid fa-list-check',
    header: 'Screen Studies',
    label:
      'Screen studies efficiently from the ranked list, providing feedback on relevance',
  },
  {
    icon: 'fa-solid fa-arrows-rotate',
    header: 'Continuous Refinement',
    label:
      'Watch as our system continuously refines rankings based on your screening decisions',
  },
  {
    icon: 'fa-solid fa-file-export',
    header: 'Export Results',
    label: 'Export your screening results in PubMed format (.nbib)',
  },
])
</script>
