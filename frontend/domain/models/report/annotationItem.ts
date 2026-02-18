export interface AnnotationItem {
  id: number
  username: string
  created_at: string
  type: string
  example_text: string
  label_text: string
  example_id?: number
  label_id?: number
  backgroundColor?: string
  project_version: number
}

export interface AnnotatorStats {
  username: string
  totalAnnotations: number
  avgPerDay: number
  lastActive: string
} 