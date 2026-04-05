import { AnnotationResponse, AnnotationFilters } from './annotation'

export interface AnnotationRepository {
  getAnnotations(projectId: string | number, filters?: AnnotationFilters): Promise<AnnotationResponse>
} 