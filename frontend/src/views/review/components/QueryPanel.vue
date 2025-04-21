<template>
  <div class="tw-flex tw-gap-4 tw-w-full">
    <Accordion
      v-for="(items, index) in sortedPicoQuery"
      :key="index"
      :activeIndex="0"
      class="tw-w-full"
      expandIcon="pi pi-chevron-up"
      collapseIcon="pi pi-chevron-down"
    >
      <AccordionTab
        :pt="{
          headerAction: 'tw-py-3',
          content: 'tw-py-3',
        }"
      >
        <template #header>
          <p v-if="index === 'P'">Population</p>
          <p v-if="index === 'I'">Intervention</p>
          <p v-if="index === 'C'">Comparison</p>
          <p v-if="index === 'O'">Outcome</p>
        </template>
        <p v-if="items.length === 0">—</p>
        <li
          class="tw-text-sm"
          v-for="item in items"
        >
          {{ item }}
        </li>
      </AccordionTab>
    </Accordion>
  </div>
</template>

<script lang="ts" setup>
import { PropType, computed } from 'vue'

import Accordion from 'primevue/accordion'
import AccordionTab from 'primevue/accordiontab'
import { IPicoQuery } from '@/types/corpus'

const props = defineProps({
  picoQuery: { type: Object as PropType<IPicoQuery>, required: true },
})

// Sort keys explicitly in PICO order
const sortedPicoQuery = computed(() => {
  const order = ['P', 'I', 'C', 'O']
  return Object.fromEntries(
    order.map((key) => [key, props.picoQuery[key] || []]),
  )
})
</script>
