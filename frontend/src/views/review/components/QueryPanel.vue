<template>
  <div class="tw-flex tw-gap-4 tw-w-full">
    <Accordion
      v-for="(items, index) in picoQuery"
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
          <p v-if="index === 'P'">Poppulation</p>
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
import { PropType } from 'vue'

import Accordion from 'primevue/accordion'
import AccordionTab from 'primevue/accordiontab'
import { IPicoQuery } from '@/types/corpus'

defineProps({
  picoQuery: { type: Object as PropType<IPicoQuery> },
})
</script>
