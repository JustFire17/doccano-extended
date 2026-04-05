export interface AnnotationLabel {
  id: number
  text: string
  backgroundColor: string
  percentage: number
}

export interface AnnotationUser {
  id: number
  username: string
}

export interface Annotation {
  id: string
  example_id: number
  text: string
  labels: AnnotationLabel[]
  version: number
  users: AnnotationUser[]
  created_at?: string
}

export interface AnnotationFilters {
  dateStart?: string | null
  dateEnd?: string | null
  labelIds?: number[]
  labelTexts?: string[]
  userIds?: number[]
  perspectiveIds?: number[]
  perspectiveValues?: string[]
  annotationIds?: number[]
  projectVersion?: number[]
}

export interface AnnotationResponse {
  annotations: Annotation[]
  total?: number
} 