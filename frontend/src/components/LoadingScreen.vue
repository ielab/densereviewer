<template>
  <div
    class="tw-text-white tw-gap-2 tw-w-full tw-h-full tw-flex tw-flex-col tw-justify-center tw-items-center tw-min-h-[86vh] tw-fixed tw-top-[6vh] tw-z-[100]"
  >
    <i class="pi pi-spin pi-spinner tw-mx-auto tw-text-[5rem]" />
    <p>{{ label }}</p>
  </div>
</template>

<script lang="ts" setup>
defineProps({
  label: { type: String, default: "Loading..." },
});
</script>
