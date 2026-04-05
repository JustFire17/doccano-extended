import ApiService from '@/services/api.service'
import { AnnotationItem } from '@/domain/models/report/annotationItem'

export class ApiReportRepository {
  constructor(private readonly request = ApiService) {}

  async getAnnotatorReports(
    projectId: string | number,
    params: {
      dateStart?: string | null,
      dateEnd?: string | null,
      perspectiveId?: string | null,
      perspectiveValue?: string | null,
      exampleId?: string | null,
      username?: string | null,
      projectVersion?: string | null
    }
  ): Promise<AnnotationItem[]> {
    // Construir query params
    const queryParams = new URLSearchParams()
    
    if (params.dateStart) {
      queryParams.append('dateStart', params.dateStart)
    }
    
    if (params.dateEnd) {
      queryParams.append('dateEnd', params.dateEnd)
    }
    
    if (params.perspectiveId) {
      queryParams.append('perspectiveId', String(params.perspectiveId))
    }
    
    if (params.perspectiveValue) {
      queryParams.append('perspectiveValue', String(params.perspectiveValue))
    }
    
    if (params.exampleId) {
      queryParams.append('exampleId', String(params.exampleId))
    }

    if (params.username) {
      queryParams.append('username', params.username)
    }

    if (params.projectVersion) {
      queryParams.append('projectVersion', params.projectVersion)
    }

    const url = `/projects/${projectId}/reports/annotators`
    const query = queryParams.toString()
    const fullUrl = query ? `${url}?${query}` : url
    
    const response = await this.request.get(fullUrl)
    return response.data
  }
} 