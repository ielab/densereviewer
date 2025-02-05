export type IIndexingStatus =
  | 'queued'
  | 'indexing'
  | 'index_ready'
  | 're-ranking'
  | 're-rank_ready'
  | 'archived'
  | 'indexing_error'

export type IScreeningStatus = 'not_start' | 'screening' | 'paused' | 'finished'

export interface IDataset {
  id: number | null
  name: string
  submission_timestamp: string
  indexing_status: IIndexingStatus
  start_indexing_timestamp: string
  indexing_time_spent: string
  screening_status: IScreeningStatus
  current_page_index: number
}
