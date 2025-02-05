import { ref } from 'vue'

import { IUploadedCorpus, IPicoQuery } from '@/types/corpus'
import { DEFAULT_UPLOADED_CORPUS, DEFAULT_PICO_QUERY } from '@/defaults/corpus'

interface IUploadCollectionFilesStore {
  file: File | null
  corpus: IUploadedCorpus
  picoQuery: IPicoQuery
  totalDocuments: number
}

const DEFAULT_UPLOAD_COLLECTION_FILES_STORE: IUploadCollectionFilesStore = {
  file: null,
  corpus: { ...DEFAULT_UPLOADED_CORPUS },
  picoQuery: { ...DEFAULT_PICO_QUERY },
  totalDocuments: 0,
}

export const uploadCollectionFilesStore = ref<IUploadCollectionFilesStore>({
  ...DEFAULT_UPLOAD_COLLECTION_FILES_STORE,
})

export function clearUploadCollectionFilesStore() {
  uploadCollectionFilesStore.value = {
    ...DEFAULT_UPLOAD_COLLECTION_FILES_STORE,
  }
}
