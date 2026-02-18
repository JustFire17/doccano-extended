import ApiService from '@/services/api.service'
import { AnnotationRepository } from '@/domain/models/annotation/annotationRepository'
import { AnnotationResponse, AnnotationFilters } from '@/domain/models/annotation/annotation'

export class APIAnnotationRepository implements AnnotationRepository {
  constructor(private readonly request = ApiService) {}

  async getAnnotations(projectId: string | number, filters?: AnnotationFilters): Promise<AnnotationResponse> {
    const queryParams = new URLSearchParams()
    
    if (filters?.dateStart) {
      queryParams.append('dateStart', filters.dateStart)
    }
    
    if (filters?.dateEnd) {
      queryParams.append('dateEnd', filters.dateEnd)
    }
    
    if (filters?.labelIds && filters.labelIds.length > 0) {
      queryParams.append('labelIds', filters.labelIds.join(','))
    }
    
    if (filters?.labelTexts && filters.labelTexts.length > 0) {
      queryParams.append('labelTexts', filters.labelTexts.join(','))
    }
    
    if (filters?.userIds && filters.userIds.length > 0) {
      queryParams.append('username', filters.userIds.join(','))
    }
    
    if (filters?.perspectiveIds && filters.perspectiveIds.length > 0) {
      queryParams.append('perspectiveId', filters.perspectiveIds.join(','))
    }
    
    if (filters?.perspectiveValues && filters.perspectiveValues.length > 0) {
      queryParams.append('perspectiveValue', filters.perspectiveValues.join(','))
    }
    
    if (filters?.annotationIds && filters.annotationIds.length > 0) {
      queryParams.append('exampleId', filters.annotationIds.join(','))
    }

    if (filters?.projectVersion && filters.projectVersion.length > 0) {
      queryParams.append('projectVersion', filters.projectVersion.join(','))
    }

    const url = `/projects/${projectId}/annotation-statistics`
    const query = queryParams.toString()
    const fullUrl = query ? `${url}?${query}` : url
    
    const response = await this.request.get(fullUrl)
    return {
      annotations: response.data.annotations || [],
      total: response.data.annotations?.length || 0
    }
  }
} 