import { AnnotationRepository } from '@/domain/models/annotation/annotationRepository'
import { AnnotationResponse, AnnotationFilters } from '@/domain/models/annotation/annotation'

export class AnnotationApplicationService {
  constructor(private readonly repository: AnnotationRepository) {}

  public async getAnnotations(
    projectId: string | number,
    filters?: AnnotationFilters
  ): Promise<AnnotationResponse> {
    try {
      return await this.repository.getAnnotations(projectId, filters)
    } catch (error) {
      console.error('Error fetching annotations:', error)
      throw error
    }
  }
} 