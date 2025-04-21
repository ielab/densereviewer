<template>
  <div class="tw-w-full tw-flex tw-flex-col tw-gap-4">
    <!-- Control Keys -->
    <Panel
      header="Control Keys"
      :pt="{ header: 'tw-p-2', content: 'tw-p-2' }"
      class="tw-w-full"
    >
      <div class="tw-flex tw-justify-around">
        <KeyBoardTips
          color="primary"
          label="Esc"
          for="Quit Full Screen"
        />
        <KeyBoardTips
          color="primary"
          icon="fa-solid fa-arrow-up"
          label="Up"
          for="Previous"
        />
        <KeyBoardTips
          color="primary"
          icon="fa-solid fa-arrow-down"
          label="Down"
          for="Next"
        />
      </div>
    </Panel>

    <!-- Assessment Keys -->
    <Panel
      header="Assessment Keys"
      :pt="{ header: 'tw-p-2', content: 'tw-p-2' }"
      class="tw-w-full"
    >
      <div class="tw-grid tw-grid-cols-4">
        <KeyBoardTips
          color="red"
          icon="fa-solid fa-arrow-left"
          label="Left"
          for="Exclude"
        />
        <KeyBoardTips
          color="slate"
          label="M"
          for="Maybe"
        />
        <KeyBoardTips
          color="green"
          icon="fa-solid fa-arrow-right"
          label="Right"
          for="Include"
        />
        <KeyBoardTips
          color="yellow"
          icon="pi pi-delete-left"
          label="Bksp"
          for="Deselect"
        />
      </div>
    </Panel>

    <!-- Composite Keys -->
    <Panel
      header="Composite Keys"
      :pt="{ header: 'tw-p-2', content: 'tw-p-2' }"
      class="tw-w-full"
    >
      <div class="tw-flex tw-flex-col tw-gap-2">
        <div class="tw-flex tw-items-center">
          <div class="tw-font-medium tw-text-sm tw-w-[50%]">
            <div class="tw-flex tw-justify-around tw-items-end tw-w-full">
              <div>
                <KeyBoardTips
                  color="primary"
                  label="Alt"
                  :showDetail="false"
                />
                <div class="tw-flex">
                  Hold:&nbsp;<span class="tw-font-bold tw-text-primary-500"
                    >Alt <i class="fa-brands fa-windows"></i
                  ></span>
                </div>
              </div>
              <span>/</span>
              <div>
                <KeyBoardTips
                  color="primary"
                  icon="option"
                  :showDetail="false"
                />
                <div class="tw-flex">
                  <span class="tw-font-bold tw-text-primary-500"
                    >Option <i class="fa-brands fa-apple"></i
                  ></span>
                </div>
              </div>
            </div>
          </div>
          <i class="fa-solid fa-plus"></i>
          <div class="tw-w-[50%] tw-flex tw-items-center tw-justify-around">
            <p class="tw-font-medium">Assessment Key</p>
          </div>
        </div>
        <p class="tw-text-sm tw-font-medium tw-text-center">
          Assessment and Move to Next
        </p>
      </div>

      <Divider class="tw-my-3" />

      <div class="tw-flex tw-flex-col tw-gap-2">
        <div class="tw-flex tw-items-center">
          <div class="tw-font-medium tw-text-sm tw-w-[50%]">
            <div class="tw-flex tw-justify-around tw-items-end tw-w-full">
              <div>
                <KeyBoardTips
                  color="primary"
                  label="Alt"
                  :showDetail="false"
                />
                <div class="tw-flex">
                  Hold:&nbsp;<span class="tw-font-bold tw-text-primary-500"
                    >Alt <i class="fa-brands fa-windows"></i
                  ></span>
                </div>
              </div>
              <span>/</span>
              <div>
                <KeyBoardTips
                  color="primary"
                  icon="option"
                  :showDetail="false"
                />
                <div class="tw-flex">
                  <span class="tw-font-bold tw-text-primary-500"
                    >Option <i class="fa-brands fa-apple"></i
                  ></span>
                </div>
              </div>
            </div>
          </div>
          <i class="fa-solid fa-plus"></i>
          <div class="tw-font-medium tw-text-sm tw-w-[50%]">
            <div class="tw-flex tw-justify-around tw-items-end tw-w-full">
              <div>
                <KeyBoardTips
                  color="primary"
                  icon="fa-solid fa-arrow-up"
                  :secondary="true"
                  :showDetail="false"
                />
                <div class="tw-flex">
                  Keypress:&nbsp;<span class="tw-font-bold tw-text-primary-500"
                    >Up</span
                  >
                </div>
              </div>
              <span>/</span>
              <div class="tw-flex tw-flex-col tw-items-center">
                <KeyBoardTips
                  color="primary"
                  icon="fa-solid fa-arrow-down"
                  :secondary="true"
                  :showDetail="false"
                />
                <div class="tw-flex">
                  <span class="tw-font-bold tw-text-primary-500">Down</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        <p class="tw-text-sm tw-font-medium tw-text-center">
          Scroll Up or Scroll Down
        </p>
      </div>
    </Panel>
  </div>
</template>

<script lang="ts" setup>
import Panel from 'primevue/panel'
import Divider from 'primevue/divider'
import KeyBoardTips from './KeyBoardTips.vue'
// import InlineMessage from 'primevue/inlinemessage'
</script>
