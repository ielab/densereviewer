import { IDataset } from '@/types/dataset'

export const DEFAULT_DATASET: IDataset = {
  id: null,
  name: '',
  submission_timestamp: '',
  indexing_status: 'queued',
  start_indexing_timestamp: '',
  indexing_time_spent: '',
  screening_status: 'not_start',
  current_page_index: 0,
}
